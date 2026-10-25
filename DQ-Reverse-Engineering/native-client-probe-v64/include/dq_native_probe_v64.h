#pragma once
#include <cstddef>
#include <cstdint>

namespace dqprobe {

// Minimal layout view for an isolated no-side-effect probe.
// AIVariable stores numeric values as float32 in the legacy ShiVa header.
struct alignas(8) AIVariableView {
    std::uint8_t type;
    std::uint8_t reserved[7];
    union Payload {
        float number;
        const char* string;
        std::uint64_t bits;
    } payload;
};

using AICallback = int (*)(int input_count, const AIVariableView* inputs,
                           AIVariableView* outputs);

struct AIFunctionView {
    const char* pName;
    AICallback pCallback;
    const char* pReturns;
    const char* pArguments;
    const char* pDescription;
    std::uint32_t iReserved;
};

using RegisterFunctionFn = bool (*)(const char* name, AIFunctionView* function);
using UnregisterFunctionFn = void (*)(const char* name);
using CallClientFunctionFn = int (*)(int argument_count,
                                     const AIVariableView* arguments,
                                     AIVariableView* outputs);

inline constexpr std::uint8_t kNumberType = 1;
inline constexpr std::uint8_t kStringType = 2;
inline constexpr const char* kProbeFunctionName = "dq_native_probe_roundtrip_v64";
inline constexpr float kProbeInput = 21.0f;
inline constexpr float kProbeExpectedOutput = 42.0f;

static_assert(sizeof(void*) == 8, "This ABI probe is intentionally 64-bit only");
static_assert(offsetof(AIVariableView, type) == 0, "AIVariable type offset changed");
static_assert(offsetof(AIVariableView, payload) == 8, "AIVariable payload offset changed");
static_assert(sizeof(AIVariableView) == 16, "AIVariable stride assumption changed");
static_assert(offsetof(AIFunctionView, pName) == 0, "AIFunction name offset changed");
static_assert(offsetof(AIFunctionView, pCallback) == 8, "AIFunction callback offset changed");
static_assert(sizeof(AIFunctionView) == 48, "Legacy ARM64 AIFunction size assumption changed");

int probe_callback(int input_count, const AIVariableView* inputs,
                   AIVariableView* outputs);
AIFunctionView* probe_function();
bool register_probe(RegisterFunctionFn register_function);
bool invoke_probe(CallClientFunctionFn call_client_function);
bool unregister_probe(UnregisterFunctionFn unregister_function);

}  // namespace dqprobe
