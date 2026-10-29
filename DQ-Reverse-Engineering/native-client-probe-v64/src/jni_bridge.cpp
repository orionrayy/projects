#include "dq_native_probe_v64.h"
#include "dq_native_cheat_router_v84.h"

#include <jni.h>
#include <dlfcn.h>
#include <mutex>

namespace {

constexpr char kEngineLibrary[] = "libS3DClient.so";
constexpr char kRegisterSymbol[] = "S3DClient_RegisterFunction";
constexpr char kUnregisterSymbol[] = "S3DClient_UnregisterFunction";
constexpr char kCallSymbol[] =
    "_Z42S3DX_AIScriptAPI_system_callClientFunctioniPKN4S3DX10AIVariableEPS0_";

struct EngineApi {
    void* handle = nullptr;
    dqprobe::RegisterFunctionFn register_function = nullptr;
    dqprobe::UnregisterFunctionFn unregister_function = nullptr;
    dqprobe::CallClientFunctionFn call_client_function = nullptr;
};

EngineApi g_api;
std::mutex g_api_mutex;
bool g_registered = false;

bool resolve_engine_api() {
    if (g_api.handle == nullptr) {
        // This prototype must run only inside an authorized development app
        // process in which the target engine has already loaded its library.
        g_api.handle = dlopen(kEngineLibrary, RTLD_NOW);
        if (g_api.handle == nullptr) {
            return false;
        }
    }

    if (g_api.register_function == nullptr) {
        g_api.register_function =
            reinterpret_cast<dqprobe::RegisterFunctionFn>(
                dlsym(g_api.handle, kRegisterSymbol));
    }
    if (g_api.unregister_function == nullptr) {
        g_api.unregister_function =
            reinterpret_cast<dqprobe::UnregisterFunctionFn>(
                dlsym(g_api.handle, kUnregisterSymbol));
    }
    if (g_api.call_client_function == nullptr) {
        g_api.call_client_function =
            reinterpret_cast<dqprobe::CallClientFunctionFn>(
                dlsym(g_api.handle, kCallSymbol));
    }

    return g_api.register_function != nullptr &&
           g_api.unregister_function != nullptr &&
           g_api.call_client_function != nullptr;
}

}  // namespace

extern "C" JNIEXPORT jboolean JNICALL
Java_com_shinybox_smash_DqNativeProbe_nativeRegisterProbe(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_api_mutex);
    if (g_registered) {
        return JNI_TRUE;
    }
    if (!resolve_engine_api()) {
        return JNI_FALSE;
    }

    // Register the no-op ABI probe first. If the v84 route gate cannot be
    // registered, roll the first registration back rather than leaving a
    // partially initialized registry behind.
    if (!dqprobe::register_probe(g_api.register_function)) {
        return JNI_FALSE;
    }
    if (!dqroute::register_route_gate(g_api.register_function)) {
        dqprobe::unregister_probe(g_api.unregister_function);
        return JNI_FALSE;
    }

    g_registered = true;
    return JNI_TRUE;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_shinybox_smash_DqNativeProbe_nativeInvokeProbe(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_api_mutex);
    if (!g_registered || !resolve_engine_api()) {
        return JNI_FALSE;
    }

    // First exercise the inert 21 -> 42 callback; then exercise lookup,
    // typed argument marshalling and fail-closed status return for the
    // native v84 route gate. Neither path mutates game state.
    if (!dqprobe::invoke_probe(g_api.call_client_function)) {
        return JNI_FALSE;
    }
    dqroute::Status status = dqroute::Status::InvalidRequest;
    const bool gate_ok =
        dqroute::invoke_route_gate_self_test(g_api.call_client_function, &status);
    return gate_ok && status == dqroute::Status::HandlerUnavailable
        ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_shinybox_smash_DqNativeProbe_nativeUnregisterProbe(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_api_mutex);
    if (!g_registered) {
        return JNI_TRUE;
    }
    if (!resolve_engine_api()) {
        return JNI_FALSE;
    }

    const bool gate_ok =
        dqroute::unregister_route_gate(g_api.unregister_function);
    const bool probe_ok =
        dqprobe::unregister_probe(g_api.unregister_function);
    if (gate_ok && probe_ok) {
        g_registered = false;
    }
    return gate_ok && probe_ok ? JNI_TRUE : JNI_FALSE;
}
