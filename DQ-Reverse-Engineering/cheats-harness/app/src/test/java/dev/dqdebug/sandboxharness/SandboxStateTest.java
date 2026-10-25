package dev.dqdebug.sandboxharness;

import org.junit.Test;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

public class SandboxStateTest {
    private static CatalogEntry entry(String id, String label, String category, String control,
            String defaultValue, double min, double max, double step, List<String> options) {
        return new CatalogEntry(id, label, category, "test catalog entry", control, defaultValue,
                "", "medium", "requires_game_adapter", min, max, step,
                options, Collections.emptyList(), Collections.emptyList());
    }

    private static List<CatalogEntry> fixture() {
        return Arrays.asList(
            entry("player.god_mode", "God mode", "Player & Survival", "toggle", "false",
                    Double.NaN, Double.NaN, Double.NaN, Collections.emptyList()),
            entry("economy.gold_multiplier", "Gold multiplier", "Economy Lab", "slider", "1",
                    0, 100, 1, Collections.emptyList()),
            entry("combat.damage_randomization", "Damage randomization", "Combat Lab", "range", "0.9:1.1",
                    0, 5, 0.05, Collections.emptyList()),
            entry("player.resource_policy", "Resource policy", "Player & Survival", "select", "normal",
                    Double.NaN, Double.NaN, Double.NaN, Arrays.asList("normal", "half_cost", "free")),
            entry("inventory.grant_item", "Grant item", "Inventory & Gear", "action", "",
                    Double.NaN, Double.NaN, Double.NaN, Collections.emptyList())
        );
    }

    @Test public void defaultsAreSafeAndAdapterIsDisconnected() {
        SandboxState s = new SandboxState(fixture());
        assertEquals("false", s.get("player.god_mode"));
        assertEquals("1", s.get("economy.gold_multiplier"));
        assertEquals("0.9:1.1", s.get("combat.damage_randomization"));
        assertFalse(s.isGameAdapterConnected());
        assertEquals(5, s.catalogCount());
        assertEquals(0, s.stagedCount());
    }

    @Test public void undoRestoresOnlyTheLastLocalPreviewSnapshot() {
        SandboxState s = new SandboxState(fixture());
        s.set("player.god_mode", "true");
        s.set("economy.gold_multiplier", "12");
        assertTrue(s.undo());
        assertEquals("1", s.get("economy.gold_multiplier"));
        assertEquals("true", s.get("player.god_mode"));
        assertTrue(s.undo());
        assertEquals("false", s.get("player.god_mode"));
        assertFalse(s.undo());
    }

    @Test public void presetsResetAndUndoAreDeterministic() {
        SandboxState s = new SandboxState(fixture());
        s.applyPreset(SandboxState.Preset.POWER_PREVIEW);
        assertEquals("true", s.get("player.god_mode"));
        assertEquals("65", s.get("economy.gold_multiplier"));
        assertEquals("free", s.get("player.resource_policy"));
        assertEquals(3, s.stagedCount());

        s.applyPreset(SandboxState.Preset.DIAGNOSTICS);
        assertEquals("false", s.get("player.god_mode"));
        assertEquals("1", s.get("economy.gold_multiplier"));
        assertEquals("0.9:1.1", s.get("combat.damage_randomization"));
        s.reset();
        assertEquals(0, s.stagedCount());
        assertEquals("normal", s.get("player.resource_policy"));
    }

    @Test public void rejectsUnknownOutOfBoundsOffStepAndInvalidRangeValues() {
        SandboxState s = new SandboxState(fixture());
        expectIllegal(() -> s.set("unknown.setting", "1"));
        expectIllegal(() -> s.set("economy.gold_multiplier", "101"));
        expectIllegal(() -> s.set("economy.gold_multiplier", "12.5"));
        expectIllegal(() -> s.set("player.god_mode", "2"));
        expectIllegal(() -> s.set("combat.damage_randomization", "1.5:1.1"));
        expectIllegal(() -> s.set("combat.damage_randomization", "0.91:1.1"));
        expectIllegal(() -> s.set("player.resource_policy", "not-a-policy"));
    }

    @Test public void actionsArePreviewRequestsAndNeverSettingWrites() {
        SandboxState s = new SandboxState(fixture());
        expectIllegal(() -> s.set("inventory.grant_item", "true"));
        s.recordActionPreview("inventory.grant_item");
        assertTrue(s.recentEvents(5).get(s.recentEvents(5).size() - 1).contains("gameplay"));
        assertEquals(0, s.stagedCount());
    }

    @Test public void exportClearlyMarksLocalScopeAndContainsStableIds() {
        SandboxState s = new SandboxState(fixture());
        s.set("player.god_mode", "true");
        String json = s.exportJson();
        assertTrue(json.contains("\"scope\": \"local-ui-preview-only\""));
        assertTrue(json.contains("\"gameAdapterConnected\": false"));
        assertTrue(json.contains("\"catalogItemCount\": 5"));
        assertTrue(json.contains("\"player.god_mode\""));
        assertTrue(json.contains("\"value\": true"));
    }

    private static void expectIllegal(Runnable action) {
        try {
            action.run();
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException expected) {
            // Expected fail-closed validation.
        }
    }
}
