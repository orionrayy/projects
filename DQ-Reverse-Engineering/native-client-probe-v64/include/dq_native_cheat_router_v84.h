#pragma once

#include "dq_native_probe_v64.h"

#include <cstddef>

namespace dqroute {

enum class ValueKind : int {
    None = 0,
    Number = 1,
    Integer = 2,
    Boolean = 3,
    Select = 4,
};

enum class Status : int {
    ValidatedOnly = 0,
    UnknownEffect = 1,
    InvalidRequest = 2,
    TypeMismatch = 3,
    OutOfRange = 4,
    StepMismatch = 5,
    PrecisionLoss = 6,
    HandlerUnavailable = 7,
    BackendUnavailable = 8,
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
// Conservative upper limit for consecutive exact integers in IEEE-754 binary64.
inline constexpr double kMaxExactDoubleInteger = 9007199254740991.0;

std::size_t spec_count();
const CheatSpec* spec_at(std::size_t index);
const CheatSpec* find_spec(const char* id);
std::size_t static_route_candidate_count();
Status validate_request(const char* id, ValueKind actual_kind, double value);
Status route_request(const char* id, ValueKind actual_kind, double value);

int route_gate_callback(int input_count, const dqprobe::AIVariableView* inputs,
                        dqprobe::AIVariableView* outputs);
dqprobe::AIFunctionView* route_gate_function();
bool register_route_gate(dqprobe::RegisterFunctionFn register_function);
bool unregister_route_gate(dqprobe::UnregisterFunctionFn unregister_function);

// Calls the registered name through the engine's script dispatcher with a
// harmless request and succeeds only when the callback returns
// HandlerUnavailable (proving validation/dispatch without applying an effect).
bool invoke_route_gate_self_test(
    dqprobe::CallClientFunctionFn call_client_function, Status* status_out);

}  // namespace dqroute
