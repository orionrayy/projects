package dev.dqdebug.sandboxharness;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** Immutable rendering/validation metadata for one stable catalog ID. */
public final class CatalogEntry {
    public final String id;
    public final String label;
    public final String category;
    public final String description;
    public final String control;
    public final String defaultValue;
    public final String unit;
    public final String risk;
    public final String integrationStatus;
    public final double min;
    public final double max;
    public final double step;
    public final List<String> options;
    public final List<String> tags;
    public final List<String> parameterSummaries;

    public CatalogEntry(String id, String label, String category, String description,
            String control, String defaultValue, String unit, String risk,
            String integrationStatus, double min, double max, double step,
            List<String> options, List<String> tags, List<String> parameterSummaries) {
        this.id = requireText(id, "id");
        this.label = requireText(label, "label");
        this.category = requireText(category, "category");
        this.description = description == null ? "" : description;
        this.control = requireText(control, "control");
        this.defaultValue = defaultValue == null ? "" : defaultValue;
        this.unit = unit == null ? "" : unit;
        this.risk = risk == null ? "unknown" : risk;
        this.integrationStatus = integrationStatus == null ? "requires_game_adapter" : integrationStatus;
        this.min = min;
        this.max = max;
        this.step = step;
        this.options = immutable(options);
        this.tags = immutable(tags);
        this.parameterSummaries = immutable(parameterSummaries);
        if (!("toggle".equals(control) || "slider".equals(control) || "range".equals(control)
                || "select".equals(control) || "action".equals(control))) {
            throw new IllegalArgumentException("Unsupported control type: " + control);
        }
        if (("slider".equals(control) || "range".equals(control))
                && (!Double.isFinite(min) || !Double.isFinite(max) || !Double.isFinite(step)
                || min > max || step <= 0.0)) {
            throw new IllegalArgumentException("Invalid numeric contract for " + id);
        }
        if ("select".equals(control) && this.options.isEmpty()) {
            throw new IllegalArgumentException("Select requires options: " + id);
        }
    }

    public static CatalogEntry fromJson(JSONObject object) throws JSONException {
        String id = object.getString("id");
        String control = object.getString("control");
        String def = defaultText(object, control);
        double min = object.isNull("min") ? Double.NaN : object.getDouble("min");
        double max = object.isNull("max") ? Double.NaN : object.getDouble("max");
        double step = object.isNull("step") ? Double.NaN : object.getDouble("step");
        return new CatalogEntry(
                id,
                object.getString("label"),
                object.getString("category"),
                object.optString("description", ""),
                control,
                def,
                object.optString("unit", ""),
                object.optString("risk", "unknown"),
                object.optString("integration_status", "requires_game_adapter"),
                min, max, step,
                strings(object.optJSONArray("options")),
                strings(object.optJSONArray("tags")),
                parameterSummaries(object.optJSONArray("parameters")));
    }

    private static String defaultText(JSONObject object, String control) throws JSONException {
        if ("toggle".equals(control)) {
            return Boolean.toString(object.optBoolean("default", false));
        }
        if ("slider".equals(control)) {
            return numberText(object.getDouble("default"));
        }
        if ("range".equals(control)) {
            JSONObject value = object.getJSONObject("default");
            return numberText(value.getDouble("min")) + ":" + numberText(value.getDouble("max"));
        }
        if ("select".equals(control)) {
            return object.getString("default");
        }
        return "";
    }

    private static String numberText(double value) {
        if (value == Math.rint(value)) return Long.toString((long) value);
        return Double.toString(value);
    }

    private static List<String> strings(JSONArray array) throws JSONException {
        if (array == null) return Collections.emptyList();
        List<String> values = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) values.add(array.getString(i));
        return values;
    }

    private static List<String> parameterSummaries(JSONArray array) throws JSONException {
        if (array == null) return Collections.emptyList();
        List<String> values = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            JSONObject p = array.getJSONObject(i);
            StringBuilder s = new StringBuilder(p.optString("name", "parameter"));
            s.append(" · ").append(p.optString("type", "value"));
            if (p.optBoolean("required", false)) s.append(" · required");
            if (p.has("min") && p.has("max") && !p.isNull("min") && !p.isNull("max")) {
                s.append(" · ").append(numberText(p.getDouble("min")))
                        .append("–").append(numberText(p.getDouble("max")));
            }
            JSONArray allowed = p.optJSONArray("options");
            if (allowed != null && allowed.length() > 0) {
                List<String> opts = strings(allowed);
                s.append(" · ").append(String.join("/", opts));
            }
            values.add(s.toString());
        }
        return values;
    }

    private static String requireText(String value, String field) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException(field + " must be non-empty");
        }
        return value;
    }

    private static List<String> immutable(List<String> input) {
        return Collections.unmodifiableList(new ArrayList<>(input == null
                ? Collections.emptyList() : input));
    }
}
