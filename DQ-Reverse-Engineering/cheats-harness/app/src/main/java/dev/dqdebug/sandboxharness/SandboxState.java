package dev.dqdebug.sandboxharness;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Local UI harness state. It intentionally has no API for reading or writing Dungeon Quest.
 * A future game adapter must be supplied separately and verified against the exact game build.
 */
public final class SandboxState {
    public enum Preset { BASELINE, POWER_PREVIEW, DIAGNOSTICS }

    private final LinkedHashMap<String, Integer> values = new LinkedHashMap<>();
    private final Deque<LinkedHashMap<String, Integer>> undo = new ArrayDeque<>();
    private final List<String> events = new ArrayList<>();
    private final LinkedHashMap<String, Integer> defaults = new LinkedHashMap<>();

    public SandboxState() {
        defaults.put("player.god_mode", 0);
        defaults.put("player.infinite_health", 0);
        defaults.put("player.infinite_mana", 0);
        defaults.put("combat.freeze_enemies", 0);
        defaults.put("combat.one_hit", 0);
        defaults.put("economy.gold_multiplier", 1);
        defaults.put("economy.xp_multiplier", 1);
        defaults.put("loot.drop_multiplier", 1);
        defaults.put("world.no_clip_preview", 0);
        defaults.put("world.freeze_timer_preview", 0);
        defaults.put("diagnostics.hitboxes_preview", 0);
        defaults.put("diagnostics.performance_overlay", 1);
        values.putAll(defaults);
        record("Local UI harness initialized; game adapter is not connected.");
    }

    public synchronized int get(String id) {
        Integer value = values.get(id);
        if (value == null) throw new IllegalArgumentException("Unknown setting id: " + id);
        return value;
    }

    public synchronized Map<String, Integer> snapshot() {
        return Collections.unmodifiableMap(new LinkedHashMap<>(values));
    }

    public synchronized List<String> recentEvents(int count) {
        int start = Math.max(0, events.size() - Math.max(0, count));
        return Collections.unmodifiableList(new ArrayList<>(events.subList(start, events.size())));
    }

    public synchronized void set(String id, int value) {
        Integer current = values.get(id);
        if (current == null) throw new IllegalArgumentException("Unknown setting id: " + id);
        int min = id.endsWith("_multiplier") ? 1 : 0;
        int max = id.endsWith("_multiplier") ? 100 : 1;
        if (value < min || value > max) {
            throw new IllegalArgumentException("Out-of-range value for " + id + ": " + value);
        }
        if (current == value) return;
        remember();
        values.put(id, value);
        record("Preview setting changed: " + id + " = " + value + " (local UI only)");
    }

    public synchronized boolean undo() {
        if (undo.isEmpty()) {
            record("Undo requested; no local change to revert.");
            return false;
        }
        values.clear();
        values.putAll(undo.removeLast());
        record("Last local preview edit reverted; no game state changed.");
        return true;
    }

    public synchronized void applyPreset(Preset preset) {
        if (preset == null) throw new IllegalArgumentException("Preset is required");
        remember();
        values.clear();
        values.putAll(defaults);
        if (preset == Preset.POWER_PREVIEW) {
            values.put("player.god_mode", 1);
            values.put("player.infinite_health", 1);
            values.put("player.infinite_mana", 1);
            values.put("combat.one_hit", 1);
            values.put("economy.gold_multiplier", 10);
            values.put("economy.xp_multiplier", 5);
            values.put("loot.drop_multiplier", 3);
            values.put("world.no_clip_preview", 1);
        } else if (preset == Preset.DIAGNOSTICS) {
            values.put("combat.freeze_enemies", 1);
            values.put("world.freeze_timer_preview", 1);
            values.put("diagnostics.hitboxes_preview", 1);
            values.put("diagnostics.performance_overlay", 1);
        }
        record("Loaded local preview preset: " + preset.name());
    }

    public synchronized void reset() {
        remember();
        values.clear();
        values.putAll(defaults);
        record("Local preview reset to baseline.");
    }

    /** Always false in this standalone app. Do not use this as a runtime game adapter. */
    public boolean isGameAdapterConnected() {
        return false;
    }

    public synchronized String exportJson() {
        StringBuilder out = new StringBuilder("{\n  \"scope\": \"local-ui-preview-only\",\n  \"gameAdapterConnected\": false,\n  \"settings\": {\n");
        int i = 0;
        for (Map.Entry<String, Integer> entry : values.entrySet()) {
            out.append("    \"").append(entry.getKey()).append("\": ").append(entry.getValue());
            if (++i < values.size()) out.append(',');
            out.append('\n');
        }
        out.append("  }\n}\n");
        return out.toString();
    }

    private void remember() {
        undo.addLast(new LinkedHashMap<>(values));
        while (undo.size() > 30) undo.removeFirst();
    }

    private void record(String message) {
        events.add(message);
        while (events.size() > 100) events.remove(0);
    }
}
