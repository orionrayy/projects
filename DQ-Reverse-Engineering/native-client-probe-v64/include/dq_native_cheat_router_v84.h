#pragma once

#include "dq_native_probe_v64.h"

#include <cstddef>

namespace dqroute {

// Numeric codes cross the legacy AIVariable boundary as float32 values.
enum class ValueKind : int {
    None = 0,
    Number = 1,
    Integer = 2,
    Boolean = 3,
    Select = 4,
};

enum class Status : int {
    ValidatedOnly = 0,       // Input is valid; this is not an applied effect.
    UnknownEffect = 1,
    InvalidRequest = 2,
    TypeMismatch = 3,
    OutOfRange = 4,
    StepMismatch = 5,
    PrecisionLoss = 6,       // float32 cannot represent this integer exactly.
    HandlerUnavailable = 7,  // Current target has no verified handler for this ID.
    BackendUnavailable = 8,  // Reserved for a future verified handler with no executor.
};

struct CheatSpec {
    const char* id;
    ValueKind kind;
    double min_value;
    double max_value;
    double step;
    std::size_t option_count;
    bool static_route_candidate;
    bool runtime_enabled;
};

inline constexpr char kRouteGateFunctionName[] = "dq_cheat_route_gate_v84";
inline constexpr double kMaxExactFloat32Integer = 16777216.0; // 2^24

std::size_t spec_count();
const CheatSpec* spec_at(std::size_t index);
const CheatSpec* find_spec(const char* id);
std::size_t static_route_candidate_count();
Status validate_request(const char* id, ValueKind actual_kind, double value);
Status route_request(const char* id, ValueKind actual_kind, double value);

// Callback contract:
// inputs[0] = effect ID (string), inputs[1] = ValueKind numeric code,
// inputs[2] = requested value (number); outputs[0] = Status numeric code.
// This gate validates requests only. It never mutates game state.
int route_gate_callback(int input_count, const dqprobe::AIVariableView* inputs,
                        dqprobe::AIVariableView* outputs);
dqprobe::AIFunctionView* route_gate_function();
bool register_route_gate(dqprobe::RegisterFunctionFn register_function);
bool unregister_route_gate(dqprobe::UnregisterFunctionFn unregister_function);

}  // namespace dqroute
