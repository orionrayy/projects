package com.shinybox.smash.reconstruction;

/**
 * Source-level snapshot of constant-like values encoded in com.shinybox.smash.Globals.
 * This preserves observed values, but not the original package owner or implementation layout.
 */
public final class GlobalsSnapshot {
    public static boolean bUseGLES2 = true;
    public static int iNativeScreenOrientation = 6;
    public static String sApplicationName = "Smash";
    public static String sPackageName = "com.shinybox.smash";

    public GlobalsSnapshot() { }
}
