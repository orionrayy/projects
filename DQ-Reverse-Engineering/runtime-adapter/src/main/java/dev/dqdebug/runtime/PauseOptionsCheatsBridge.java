package dev.dqdebug.runtime;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Source integration seam for adding Cheats (Sandbox) inside the existing Pause -> Options route.
 *
 * This bridge deliberately does not pretend to patch the proprietary S3D HUD. The authorized
 * game-source adapter must implement OptionsUiHook against the real Options menu and register
 * the provided callback. Until then install() reports the missing route hook and never claims
 * that the entry exists in-game.
 */
public final class PauseOptionsCheatsBridge {
    public static final String PAUSE_OPTIONS_ROUTE_ID = "pause.options";
    public static final String ENTRY_ID = "pause.options.cheats_sandbox";
    public static final String ENTRY_LABEL = "Cheats (Sandbox)";

    public interface OptionsUiHook {
        /** True only if the actual game UI can resolve this parent route at runtime. */
        boolean hasRoute(String routeId);
        /** Add an entry inside the existing Options view; return true only after binding its callback. */
        boolean registerEntry(String parentRouteId, MenuEntry entry);
    }

    public interface RuntimeGate {
        /** Read current state from the game-owned host; must not synthesize defaults. */
        GateSnapshot snapshot() throws Exception;
    }

    public interface PagePresenter {
        /** Open the page, with mutation disabled unless LaunchState permits it. */
        void open(LaunchState state);
    }

    public enum InstallStatus {
        INSTALLED, ALREADY_INSTALLED, ROUTE_HOOK_UNAVAILABLE,
        REGISTRATION_REJECTED, INVALID_CONFIGURATION
    }

    public enum PageStatus { READY, READ_ONLY, RECOVERY_REQUIRED }

    public static final class InstallResult {
        private final InstallStatus status;
        private final String message;
        InstallResult(InstallStatus status, String message) {
            this.status = status;
            this.message = message;
        }
        public InstallStatus getStatus() { return status; }
        public String getMessage() { return message; }
        public boolean isInstalled() {
            return status == InstallStatus.INSTALLED || status == InstallStatus.ALREADY_INSTALLED;
        }
    }

    public static final class MenuEntry {
        private final String id;
        private final String label;
        private final Runnable onSelected;
        MenuEntry(String id, String label, Runnable onSelected) {
            this.id = id;
            this.label = label;
            this.onSelected = onSelected;
        }
        public String getId() { return id; }
        public String getLabel() { return label; }
        public void select() { onSelected.run(); }
    }

    /** Immutable snapshot of sandbox gates reported by the host/controller. */
    public static final class GateSnapshot {
        public final boolean sandboxProfileActive;
        public final boolean saveIsolated;
        public final boolean offlineSandbox;
        public final boolean onlineSession;
        public final boolean cloudSyncEnabled;
        public final boolean leaderboardSubmissionEnabled;
        public final boolean achievementSubmissionEnabled;
        public final boolean runtimeStateHydrated;
        public final boolean mutationRecoveryRequired;

        public GateSnapshot(boolean sandboxProfileActive, boolean saveIsolated,
                boolean offlineSandbox, boolean onlineSession, boolean cloudSyncEnabled,
                boolean leaderboardSubmissionEnabled, boolean achievementSubmissionEnabled,
                boolean runtimeStateHydrated, boolean mutationRecoveryRequired) {
            this.sandboxProfileActive = sandboxProfileActive;
            this.saveIsolated = saveIsolated;
            this.offlineSandbox = offlineSandbox;
            this.onlineSession = onlineSession;
            this.cloudSyncEnabled = cloudSyncEnabled;
            this.leaderboardSubmissionEnabled = leaderboardSubmissionEnabled;
            this.achievementSubmissionEnabled = achievementSubmissionEnabled;
            this.runtimeStateHydrated = runtimeStateHydrated;
            this.mutationRecoveryRequired = mutationRecoveryRequired;
        }
    }

    public static final class LaunchState {
        private final PageStatus status;
        private final boolean mutationsAllowed;
        private final List<String> reasons;
        LaunchState(PageStatus status, boolean mutationsAllowed, List<String> reasons) {
            this.status = status;
            this.mutationsAllowed = mutationsAllowed;
            this.reasons = Collections.unmodifiableList(new ArrayList<String>(reasons));
        }
        public PageStatus getStatus() { return status; }
        public boolean areMutationsAllowed() { return mutationsAllowed; }
        public List<String> getReasons() { return reasons; }
    }

    private final OptionsUiHook uiHook;
    private final RuntimeGate runtimeGate;
    private final PagePresenter pagePresenter;
    private boolean installed;

    public PauseOptionsCheatsBridge(OptionsUiHook uiHook, RuntimeGate runtimeGate,
                                    PagePresenter pagePresenter) {
        this.uiHook = uiHook;
        this.runtimeGate = runtimeGate;
        this.pagePresenter = pagePresenter;
    }

    public synchronized InstallResult install() {
        if (installed) return new InstallResult(InstallStatus.ALREADY_INSTALLED,
                "Cheats entry was already registered by this bridge");
        if (uiHook == null || runtimeGate == null || pagePresenter == null) {
            return new InstallResult(InstallStatus.INVALID_CONFIGURATION,
                    "UI hook, game-owned runtime gate, and page presenter are all required");
        }
        if (!uiHook.hasRoute(PAUSE_OPTIONS_ROUTE_ID)) {
            return new InstallResult(InstallStatus.ROUTE_HOOK_UNAVAILABLE,
                    "The actual Pause -> Options route hook is unavailable; no UI entry was registered");
        }
        MenuEntry entry = new MenuEntry(ENTRY_ID, ENTRY_LABEL, new Runnable() {
            @Override public void run() { onEntrySelected(); }
        });
        if (!uiHook.registerEntry(PAUSE_OPTIONS_ROUTE_ID, entry)) {
            return new InstallResult(InstallStatus.REGISTRATION_REJECTED,
                    "The Options host did not confirm callback registration");
        }
        installed = true;
        return new InstallResult(InstallStatus.INSTALLED,
                "Cheats entry callback registered through the supplied Options UI hook");
    }

    public synchronized boolean isInstalled() { return installed; }

    private void onEntrySelected() {
        GateSnapshot snapshot = null;
        try {
            if (runtimeGate != null) snapshot = runtimeGate.snapshot();
        } catch (Exception ignored) {
            // Failure is fail-closed: the page may open read-only, never mutation-enabled.
        }
        if (pagePresenter != null) pagePresenter.open(evaluate(snapshot));
    }

    public static LaunchState evaluate(GateSnapshot s) {
        List<String> reasons = new ArrayList<String>();
        if (s == null) {
            reasons.add("Game-owned runtime gate snapshot unavailable");
            return new LaunchState(PageStatus.READ_ONLY, false, reasons);
        }
        if (s.mutationRecoveryRequired) {
            reasons.add("RECOVERY_REQUIRED: reconcile the runtime state before applying changes");
            return new LaunchState(PageStatus.RECOVERY_REQUIRED, false, reasons);
        }
        if (!s.sandboxProfileActive) reasons.add("Sandbox profile is not active");
        if (!s.saveIsolated) reasons.add("Sandbox save is not isolated");
        if (!s.offlineSandbox) reasons.add("Offline sandbox mode is not confirmed");
        if (s.onlineSession) reasons.add("Online session detected");
        if (s.cloudSyncEnabled) reasons.add("Cloud synchronization must be disabled");
        if (s.leaderboardSubmissionEnabled) reasons.add("Leaderboard submission must be disabled");
        if (s.achievementSubmissionEnabled) reasons.add("Achievement submission must be disabled");
        if (!s.runtimeStateHydrated) reasons.add("Runtime settings snapshot has not been hydrated");
        boolean ready = reasons.isEmpty();
        return new LaunchState(ready ? PageStatus.READY : PageStatus.READ_ONLY, ready, reasons);
    }
}
