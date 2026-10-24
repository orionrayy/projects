package dev.dqdebug.sandboxharness;

import org.junit.Test;
import static org.junit.Assert.*;

public class SandboxStateTest {
    @Test public void defaultsAreSafeAndAdapterIsDisconnected() {
        SandboxState s = new SandboxState();
        assertEquals(0, s.get("player.god_mode"));
        assertEquals(1, s.get("economy.gold_multiplier"));
        assertFalse(s.isGameAdapterConnected());
    }

    @Test public void undoRestoresOnlyTheLastLocalPreviewSnapshot() {
        SandboxState s = new SandboxState();
        s.set("player.god_mode", 1);
        s.set("economy.gold_multiplier", 12);
        assertTrue(s.undo());
        assertEquals(1, s.get("player.god_mode"));
        assertEquals(1, s.get("economy.gold_multiplier"));
        assertTrue(s.undo());
        assertEquals(0, s.get("player.god_mode"));
    }

    @Test public void presetsAndResetAreDeterministic() {
        SandboxState s = new SandboxState();
        s.applyPreset(SandboxState.Preset.POWER_PREVIEW);
        assertEquals(1, s.get("player.god_mode"));
        assertEquals(10, s.get("economy.gold_multiplier"));
        s.applyPreset(SandboxState.Preset.DIAGNOSTICS);
        assertEquals(0, s.get("player.god_mode"));
        assertEquals(1, s.get("diagnostics.hitboxes_preview"));
        s.reset();
        assertEquals(0, s.get("diagnostics.hitboxes_preview"));
        assertEquals(1, s.get("diagnostics.performance_overlay"));
    }

    @Test public void unknownAndOutOfRangeValuesAreRejected() {
        SandboxState s = new SandboxState();
        try { s.set("unknown.setting", 1); fail("unknown setting should be rejected"); }
        catch (IllegalArgumentException expected) {}
        try { s.set("economy.gold_multiplier", 101); fail("range should be enforced"); }
        catch (IllegalArgumentException expected) {}
        try { s.set("player.god_mode", 2); fail("boolean range should be enforced"); }
        catch (IllegalArgumentException expected) {}
    }

    @Test public void exportAndEventsClearlyMarkLocalOnlyScope() {
        SandboxState s = new SandboxState();
        String json = s.exportJson();
        assertTrue(json.contains("\"scope\": \"local-ui-preview-only\""));
        assertTrue(json.contains("\"gameAdapterConnected\": false"));
        assertTrue(s.recentEvents(5).get(0).contains("adapter is not connected"));
    }
}
