#include "dq_native_probe_v64.h"

#include <cmath>

namespace dqprobe {
namespace {

AIVariableView make_number(float value) {
    AIVariableView result{};
    result.type = kNumberType;
    result.payload.number = value;
    return result;
}

AIFunctionView g_probe_function{
    kProbeFunctionName,
    &probe_callback,
    "nResult",
    "nInput",
    "Side-effect-free ABI roundtrip probe; returns input multiplied by two",
    0,
};

}  // namespace

int probe_callback(int input_count, const AIVariableView* inputs,
                   AIVariableView* outputs) {
    // No game-state access, file I/O, network calls, or mutation.
    if (input_count != 1 || inputs == nullptr || outputs == nullptr) {
        return 0;
    }
    if (inputs[0].type != kNumberType ||
        !std::isfinite(inputs[0].payload.number) ||
        inputs[0].payload.number != kProbeInput) {
        return 0;
    }
    outputs[0] = make_number(kProbeExpectedOutput);
    return 1;
}

AIFunctionView* probe_function() {
    return &g_probe_function;
}

bool register_probe(RegisterFunctionFn register_function) {
    if (register_function == nullptr) {
        return false;
    }
    return register_function(kProbeFunctionName, &g_probe_function);
}

bool invoke_probe(CallClientFunctionFn call_client_function) {
    if (call_client_function == nullptr) {
        return false;
    }

    // The target script dispatcher treats argument zero as the registered name.
    AIVariableView arguments[2]{};
    arguments[0].type = kStringType;
    arguments[0].payload.string = kProbeFunctionName;
    arguments[1] = make_number(kProbeInput);

    AIVariableView output{};
    const int output_count = call_client_function(2, arguments, &output);
    return output_count == 1 && output.type == kNumberType &&
           std::isfinite(output.payload.number) &&
           output.payload.number == kProbeExpectedOutput;
}

bool unregister_probe(UnregisterFunctionFn unregister_function) {
    if (unregister_function == nullptr) {
        return false;
    }
    unregister_function(kProbeFunctionName);
    return true;
}

}  // namespace dqprobe
