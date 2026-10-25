package com.shinybox.smash;

/**
 * Source-only integration stub for the v64 side-effect-free native probe.
 * It is not wired into the packaged Dungeon Quest application.
 *
 * A separately authorized development build must call these methods from the
 * engine-owning thread after native initialization and before engine shutdown.
 */
public final class DqNativeProbe {
    static {
        System.loadLibrary("dqbridge");
    }

    private DqNativeProbe() {
        throw new AssertionError("no instances");
    }

    public static native boolean nativeRegisterProbe();
    public static native boolean nativeInvokeProbe();
    public static native boolean nativeUnregisterProbe();
}
