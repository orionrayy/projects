package com.shinybox.smash.reconstruction;

/**
 * Interface contract inferred from the native method descriptors in the supplied DEX.
 * It is a reference for analysis/reimplementation, not the original JNI owner class,
 * not an implementation of the engine, and not proof of ABI compatibility with any .so.
 * Parameter names are generic because original local/debug names were not preserved.
 */
public interface S3DNativeEngineContract {
    boolean engineDidPassFirstFrame();
    boolean engineGetCameraDeviceState();
    java.lang.String engineGetOverlayMovie();
    boolean engineGetOverlayMovieHasChanged();
    boolean engineGetWantSwapBuffers();
    boolean engineInitialize();
    void engineOnCameraDeviceFrame(byte[] arg0, int arg1, int arg2);
    void engineOnDeviceMove(float arg0, float arg1, float arg2);
    void engineOnHeadingChanged(float arg0);
    void engineOnKeyboardKeyDown(int arg0, int arg1);
    void engineOnKeyboardKeyUp(int arg0, int arg1);
    void engineOnLocationChanged(float arg0, float arg1, float arg2);
    void engineOnMouseButtonDown(float arg0, float arg1);
    void engineOnMouseButtonUp(float arg0, float arg1);
    void engineOnMouseMove(float arg0, float arg1);
    void engineOnOverlayMovieStopped();
    void engineOnSurfaceChanged(int arg0, int arg1);
    void engineOnSurfaceCreated();
    void engineOnTouchesChange(int arg0, float arg1, float arg2, int arg3, float arg4, float arg5, int arg6, float arg7, float arg8, int arg9, float arg10, float arg11, int arg12, float arg13, float arg14);
    void enginePause(boolean arg0);
    boolean engineRunOneFrame();
    void engineSetCameraDeviceCount(int arg0);
    void engineSetCameraDeviceName(int arg0, java.lang.String arg1);
    void engineSetDeviceIPAddress(java.lang.String arg0);
    void engineSetDeviceModel(java.lang.String arg0);
    void engineSetDeviceName(java.lang.String arg0);
    void engineSetDeviceUUID(java.lang.String arg0);
    void engineSetDirectories(java.lang.String arg0, java.lang.String arg1, java.lang.String arg2);
    void engineSetHeadingSupport(boolean arg0);
    void engineSetLocationSupport(boolean arg0);
    void engineSetPackFileDescriptor(java.io.FileDescriptor arg0, long arg1, long arg2);
    void engineSetSystemLanguage(java.lang.String arg0);
    void engineSetSystemVersion(java.lang.String arg0);
    void engineShutdown();
}
