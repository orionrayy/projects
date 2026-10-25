package dev.dqdebug.runtime;

/** Dependency-free contract tests; these do not execute inside the Dungeon Quest game. */
public final class PauseOptionsCheatsBridgeSelfTest {
    private static int passed;
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
        passed++;
    }
    private static PauseOptionsCheatsBridge.GateSnapshot ready() {
        return new PauseOptionsCheatsBridge.GateSnapshot(true, true, true, false,
                false, false, false, true, false);
    }
    private static final class FakeHook implements PauseOptionsCheatsBridge.OptionsUiHook {
        boolean routeAvailable = true;
        boolean acceptRegistration = true;
        int registrations;
        String parent;
        PauseOptionsCheatsBridge.MenuEntry entry;
        public boolean hasRoute(String routeId) {
            return routeAvailable && PauseOptionsCheatsBridge.PAUSE_OPTIONS_ROUTE_ID.equals(routeId);
        }
        public boolean registerEntry(String parentRouteId, PauseOptionsCheatsBridge.MenuEntry entry) {
            registrations++;
            parent = parentRouteId;
            this.entry = entry;
            return acceptRegistration;
        }
    }
    private static final class FakePage implements PauseOptionsCheatsBridge.PagePresenter {
        int opens;
        PauseOptionsCheatsBridge.LaunchState last;
        public void open(PauseOptionsCheatsBridge.LaunchState state) { opens++; last = state; }
    }

    public static void main(String[] args) {
        FakeHook hook1 = new FakeHook(); hook1.routeAvailable = false;
        FakePage page1 = new FakePage();
        PauseOptionsCheatsBridge b1 = new PauseOptionsCheatsBridge(hook1, () -> ready(), page1);
        check(b1.install().getStatus() == PauseOptionsCheatsBridge.InstallStatus.ROUTE_HOOK_UNAVAILABLE,
                "Missing native route must fail closed");
        check(!b1.isInstalled() && hook1.registrations == 0, "No entry may be claimed without a route");

        FakeHook hook2 = new FakeHook(); FakePage page2 = new FakePage();
        PauseOptionsCheatsBridge b2 = new PauseOptionsCheatsBridge(hook2, () -> ready(), page2);
        check(b2.install().getStatus() == PauseOptionsCheatsBridge.InstallStatus.INSTALLED,
                "Valid UI hook should register");
        check(PauseOptionsCheatsBridge.ENTRY_ID.equals(hook2.entry.getId()), "Stable route ID");
        check(PauseOptionsCheatsBridge.ENTRY_LABEL.equals(hook2.entry.getLabel()), "Stable user label");
        check(PauseOptionsCheatsBridge.PAUSE_OPTIONS_ROUTE_ID.equals(hook2.parent), "Must nest inside Options");
        hook2.entry.select();
        check(page2.opens == 1 && page2.last.getStatus() == PauseOptionsCheatsBridge.PageStatus.READY,
                "Click must route to page with ready gate state");

        check(b2.install().getStatus() == PauseOptionsCheatsBridge.InstallStatus.ALREADY_INSTALLED,
                "Install must be idempotent");
        check(hook2.registrations == 1, "No duplicate route registrations");

        FakeHook hook3 = new FakeHook(); hook3.acceptRegistration = false;
        PauseOptionsCheatsBridge b3 = new PauseOptionsCheatsBridge(hook3, () -> ready(), new FakePage());
        check(b3.install().getStatus() == PauseOptionsCheatsBridge.InstallStatus.REGISTRATION_REJECTED,
                "Rejected callback binding must not be reported as installed");
        check(!b3.isInstalled(), "Rejected binding state");

        FakePage page4 = new FakePage();
        FakeHook hook4 = new FakeHook();
        PauseOptionsCheatsBridge.GateSnapshot online = new PauseOptionsCheatsBridge.GateSnapshot(
                true, true, true, true, true, false, false, true, false);
        PauseOptionsCheatsBridge b4 = new PauseOptionsCheatsBridge(hook4, () -> online, page4);
        check(b4.install().isInstalled(), "Route installs independently from gameplay readiness");
        hook4.entry.select();
        check(page4.last.getStatus() == PauseOptionsCheatsBridge.PageStatus.READ_ONLY,
                "Online state should only open read-only page");
        check(!page4.last.areMutationsAllowed() && !page4.last.getReasons().isEmpty(),
                "Unsafe state must deny mutation and explain why");

        FakePage page5 = new FakePage();
        PauseOptionsCheatsBridge b5 = new PauseOptionsCheatsBridge(new FakeHook(), () ->
                new PauseOptionsCheatsBridge.GateSnapshot(true, true, true, false,
                        false, false, false, true, true), page5);
        b5.install();
        // Use the hook that received the entry to trigger the path below.
        FakeHook hook5 = new FakeHook();
        PauseOptionsCheatsBridge b5a = new PauseOptionsCheatsBridge(hook5, () ->
                new PauseOptionsCheatsBridge.GateSnapshot(true, true, true, false,
                        false, false, false, true, true), page5);
        b5a.install(); hook5.entry.select();
        check(page5.last.getStatus() == PauseOptionsCheatsBridge.PageStatus.RECOVERY_REQUIRED,
                "Recovery lock must take precedence over all other statuses");
        check(!page5.last.areMutationsAllowed(), "Recovery lock must deny mutations");

        PauseOptionsCheatsBridge.LaunchState missing =
                PauseOptionsCheatsBridge.evaluate(null);
        check(missing.getStatus() == PauseOptionsCheatsBridge.PageStatus.READ_ONLY
                        && !missing.areMutationsAllowed(),
                "Unknown runtime state must fail closed");

        PauseOptionsCheatsBridge b6 = new PauseOptionsCheatsBridge(null, () -> ready(), new FakePage());
        check(b6.install().getStatus() == PauseOptionsCheatsBridge.InstallStatus.INVALID_CONFIGURATION,
                "Missing host adapters must fail closed");

        System.out.println("PASS: " + passed + " PauseOptionsCheatsBridge assertions");
    }
}
