package dev.dqdebug.sandboxharness;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Deterministic local draft state for the full catalog. It intentionally has no
 * API that reads or writes Dungeon Quest memory, saves, native models, or services.
 */
public final class SandboxState {
    public enum Preset { BASELINE, POWER_PREVIEW, DIAGNOSTICS }

    private final List<CatalogEntry> catalog;
    private final LinkedHashMap<String, CatalogEntry> entriesById = new LinkedHashMap<>();
    private final LinkedHashMap<String, String> values = new LinkedHashMap<>();
    private final Deque<LinkedHashMap<String, String>> undo = new ArrayDeque<>();
    private final List<String> events = new ArrayList<>();

    public SandboxState(List<CatalogEntry> catalog) {
        if (catalog == null || catalog.isEmpty()) {
            throw new IllegalArgumentException("Catalog must not be empty");
        }
        this.catalog = Collections.unmodifiableList(new ArrayList<>(catalog));
        for (CatalogEntry entry : catalog) {
            if (entriesById.put(entry.id, entry) != null) {
                throw new IllegalArgumentException("Duplicate stable ID: " + entry.id);
            }
            if (!"action".equals(entry.control)) values.put(entry.id, entry.defaultValue);
        }
        record("Catalog loaded; all values are local drafts and the game adapter is disconnected.");
    }

    public synchronized String get(String id) {
        String value = values.get(id);
        if (value == null) throw new IllegalArgumentException("Unknown or non-setting ID: " + id);
        return value;
    }

    public synchronized Map<String, String> snapshot() {
        return Collections.unmodifiableMap(new LinkedHashMap<>(values));
    }

    public List<CatalogEntry> catalog() {
        return catalog;
    }

    public int catalogCount() {
        return catalog.size();
    }

    public synchronized int stagedCount() {
        int count = 0;
        for (CatalogEntry entry : catalog) {
            if (!"action".equals(entry.control) && !entry.defaultValue.equals(values.get(entry.id))) count++;
        }
        return count;
    }

    public synchronized boolean isDefault(String id) {
        CatalogEntry entry = entriesById.get(id);
        if (entry == null) throw new IllegalArgumentException("Unknown stable ID: " + id);
        return "action".equals(entry.control) || entry.defaultValue.equals(values.get(id));
    }

    public synchronized void set(String id, String value) {
        CatalogEntry entry = entriesById.get(id);
        if (entry == null) throw new IllegalArgumentException("Unknown stable ID: " + id);
        if ("action".equals(entry.control)) {
            throw new IllegalArgumentException("Actions are requests, not staged settings: " + id);
        }
        String normalized = validateAndNormalize(entry, value);
        String current = values.get(id);
        if (normalized.equals(current)) return;
        remember();
        values.put(id, normalized);
        record("Local draft changed: " + id + " = " + normalized + " (no game effect).");
    }

    public synchronized boolean undo() {
        if (undo.isEmpty()) {
            record("Undo requested; no local setting change is available.");
            return false;
        }
        values.clear();
        values.putAll(undo.removeLast());
        record("Last local draft snapshot restored; no game state changed.");
        return true;
    }

    public synchronized void applyPreset(Preset preset) {
        if (preset == null) throw new IllegalArgumentException("Preset is required");
        LinkedHashMap<String, String> next = new LinkedHashMap<>();
        for (CatalogEntry entry : catalog) {
            if (!"action".equals(entry.control)) next.put(entry.id, entry.defaultValue);
        }
        if (preset == Preset.POWER_PREVIEW) {
            for (CatalogEntry entry : catalog) {
                if ("action".equals(entry.control)) continue;
                if ("toggle".equals(entry.control)
                        && ("Player & Survival".equals(entry.category)
                        || "Combat Lab".equals(entry.category))) {
                    next.put(entry.id, "true");
                } else if ("slider".equals(entry.control)
                        && ("Player & Survival".equals(entry.category)
                        || "Combat Lab".equals(entry.category)
                        || "Economy Lab".equals(entry.category))) {
                    double value = snap(entry, entry.min + (entry.max - entry.min) * 0.65);
                    next.put(entry.id, numberText(value));
                } else if ("select".equals(entry.control) && entry.options.contains("free")) {
                    next.put(entry.id, "free");
                }
            }
        } else if (preset == Preset.DIAGNOSTICS) {
            for (CatalogEntry entry : catalog) {
                if ("action".equals(entry.control)) continue;
                if ("toggle".equals(entry.control)
                        && ("Debug Tools".equals(entry.category)
                        || "Camera & Visuals".equals(entry.category)
                        || "UI & Accessibility".equals(entry.category))) {
                    next.put(entry.id, "true");
                }
            }
        }
        if (!next.equals(values)) {
            remember();
            values.clear();
            values.putAll(next);
        }
        record("Loaded local draft preset: " + preset.name() + ".");
    }

    public synchronized void reset() {
        LinkedHashMap<String, String> defaults = new LinkedHashMap<>();
        for (CatalogEntry entry : catalog) {
            if (!"action".equals(entry.control)) defaults.put(entry.id, entry.defaultValue);
        }
        if (!defaults.equals(values)) {
            remember();
            values.clear();
            values.putAll(defaults);
        }
        record("Local drafts reset to catalog defaults; no game state changed.");
    }

    public synchronized void recordActionPreview(String id) {
        CatalogEntry entry = entriesById.get(id);
        if (entry == null || !"action".equals(entry.control)) {
            throw new IllegalArgumentException("ID is not a catalog action: " + id);
        }
        record("Preview request only: " + id + ". Rejected for gameplay because the game adapter is disconnected.");
    }

    public boolean isGameAdapterConnected() {
        return false;
    }

    public synchronized List<String> recentEvents(int count) {
        int start = Math.max(0, events.size() - Math.max(0, count));
        return Collections.unmodifiableList(new ArrayList<>(events.subList(start, events.size())));
    }

    public synchronized String exportJson() {
        StringBuilder out = new StringBuilder();
        out.append("{\n  \"scope\": \"local-ui-preview-only\",\n");
        out.append("  \"gameAdapterConnected\": false,\n");
        out.append("  \"catalogItemCount\": ").append(catalog.size()).append(",\n");
        out.append("  \"stagedSettingCount\": ").append(stagedCount()).append(",\n");
        out.append("  \"settings\": {\n");
        int i = 0;
        for (CatalogEntry entry : catalog) {
            if ("action".equals(entry.control)) continue;
            out.append("    ").append(quote(entry.id)).append(": {\"control\": ")
                    .append(quote(entry.control)).append(", \"value\": ")
                    .append(typedJsonValue(entry, values.get(entry.id))).append("}");
            i++;
            if (i < values.size()) out.append(',');
            out.append('\n');
        }
        out.append("  },\n  \"recentEvents\": [\n");
        List<String> recent = recentEvents(20);
        for (int k = 0; k < recent.size(); k++) {
            out.append("    ").append(quote(recent.get(k)));
            if (k + 1 < recent.size()) out.append(',');
            out.append('\n');
        }
        out.append("  ]\n}\n");
        return out.toString();
    }

    private String typedJsonValue(CatalogEntry entry, String value) {
        if ("toggle".equals(entry.control)) return Boolean.toString(Boolean.parseBoolean(value));
        if ("slider".equals(entry.control)) return numberText(Double.parseDouble(value));
        if ("select".equals(entry.control)) return quote(value);
        String[] parts = value.split(":", -1);
        return "{\"min\": " + numberText(Double.parseDouble(parts[0]))
                + ", \"max\": " + numberText(Double.parseDouble(parts[1])) + "}";
    }

    private String validateAndNormalize(CatalogEntry entry, String raw) {
        if (raw == null) throw new IllegalArgumentException("Value must not be null: " + entry.id);
        if ("toggle".equals(entry.control)) {
            if (!"true".equalsIgnoreCase(raw) && !"false".equalsIgnoreCase(raw)) {
                throw new IllegalArgumentException("Expected boolean for " + entry.id);
            }
            return Boolean.toString(Boolean.parseBoolean(raw));
        }
        if ("select".equals(entry.control)) {
            if (!entry.options.contains(raw)) throw new IllegalArgumentException("Unknown option for " + entry.id + ": " + raw);
            return raw;
        }
        if ("slider".equals(entry.control)) {
            double number = parseFinite(raw, entry.id);
            validateNumber(entry, number);
            return numberText(number);
        }
        if ("range".equals(entry.control)) {
            String[] parts = raw.split(":", -1);
            if (parts.length != 2) throw new IllegalArgumentException("Range must be min:max for " + entry.id);
            double low = parseFinite(parts[0], entry.id);
            double high = parseFinite(parts[1], entry.id);
            validateNumber(entry, low);
            validateNumber(entry, high);
            if (low > high) throw new IllegalArgumentException("Range minimum exceeds maximum for " + entry.id);
            return numberText(low) + ":" + numberText(high);
        }
        throw new IllegalArgumentException("Unsupported setting type: " + entry.control);
    }

    private void validateNumber(CatalogEntry entry, double value) {
        if (value < entry.min - 1e-9 || value > entry.max + 1e-9) {
            throw new IllegalArgumentException("Value outside bounds for " + entry.id);
        }
        double ticks = (value - entry.min) / entry.step;
        if (Math.abs(ticks - Math.rint(ticks)) > 1e-6) {
            throw new IllegalArgumentException("Value does not align to step for " + entry.id);
        }
    }

    private double snap(CatalogEntry entry, double value) {
        double ticks = Math.rint((value - entry.min) / entry.step);
        return Math.max(entry.min, Math.min(entry.max, entry.min + ticks * entry.step));
    }

    private static double parseFinite(String text, String id) {
        final double value;
        try {
            value = Double.parseDouble(text.trim());
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException("Invalid number for " + id, ex);
        }
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            throw new IllegalArgumentException("Non-finite number for " + id);
        }
        return value;
    }

    private static String numberText(double value) {
        if (Math.abs(value - Math.rint(value)) < 1e-8) return Long.toString(Math.round(value));
        String s = String.format(java.util.Locale.US, "%.6f", value);
        while (s.contains(".") && s.endsWith("0")) s = s.substring(0, s.length() - 1);
        if (s.endsWith(".")) s = s.substring(0, s.length() - 1);
        return s;
    }

    private static String quote(String value) {
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c == '\"' || c == '\\') out.append('\\').append(c);
            else if (c == '\n') out.append("\\n");
            else if (c == '\r') out.append("\\r");
            else if (c == '\t') out.append("\\t");
            else if (c < 0x20) out.append(String.format(java.util.Locale.US, "\\u%04x", (int) c));
            else out.append(c);
        }
        return out.append('\"').toString();
    }

    private void remember() {
        undo.addLast(new LinkedHashMap<>(values));
        while (undo.size() > 30) undo.removeFirst();
    }

    private void record(String event) {
        events.add(event);
        while (events.size() > 150) events.remove(0);
    }
}
