#include "dq_native_cheat_router_v84.h"

#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <unordered_map>
#include <unordered_set>

namespace {

std::unordered_map<std::string, dqprobe::AIFunctionView*> g_registry;
int g_failures = 0;
int g_passed = 0;

void check(bool condition, const char* label) {
    if (!condition) {
        ++g_failures;
        std::cerr << "FAIL: " << label << "\n";
    } else {
        ++g_passed;
        std::cout << "PASS: " << label << "\n";
    }
}

bool mock_register(const char* name, dqprobe::AIFunctionView* function) {
    if (name == nullptr || function == nullptr || function->pName == nullptr ||
        function->pCallback == nullptr || std::string(name) != function->pName) {
        return false;
    }
    return g_registry.emplace(name, function).second;
}

void mock_unregister(const char* name) {
    if (name != nullptr) {
        g_registry.erase(name);
    }
}

int mock_call(int argc, const dqprobe::AIVariableView* args,
              dqprobe::AIVariableView* outputs) {
    if (argc < 1 || args == nullptr || outputs == nullptr ||
        args[0].type != dqprobe::kStringType ||
        args[0].payload.string == nullptr) {
        return 0;
    }
    const auto it = g_registry.find(args[0].payload.string);
    if (it == g_registry.end() || it->second == nullptr ||
        it->second->pCallback == nullptr) {
        return 0;
    }
    return it->second->pCallback(argc - 1, args + 1, outputs);
}

dqprobe::AIVariableView number(double value) {
    dqprobe::AIVariableView v{};
    v.type = dqprobe::kNumberType;
    v.payload.number = value;
    return v;
}

}  // namespace

int main() {
    check(dqroute::spec_count() == 50, "exactly 50 stable IDs are registered");
    check(dqroute::static_route_candidate_count() == 11,
          "eleven static route candidates are tracked but not promoted");

    std::unordered_set<std::string> ids;
    for (std::size_t i = 0; i < dqroute::spec_count(); ++i) {
        const auto* spec = dqroute::spec_at(i);
        check(spec != nullptr, "spec index resolves");
        if (spec == nullptr) continue;
        check(ids.emplace(spec->id).second, "stable IDs are unique");
        check(!spec->runtime_enabled, "no unverified gameplay route is enabled");
    }
    check(dqroute::spec_at(50) == nullptr, "out-of-range spec lookup fails closed");
    check(dqroute::find_spec(nullptr) == nullptr, "null ID fails closed");
    check(dqroute::find_spec("not.a.real.cheat") == nullptr, "unknown ID is not mapped");

    check(dqroute::validate_request("player.god_mode", dqroute::ValueKind::Boolean, 1.0)
              == dqroute::Status::ValidatedOnly, "valid toggle value passes input validation");
    check(dqroute::route_request("player.god_mode", dqroute::ValueKind::Boolean, 1.0)
              == dqroute::Status::HandlerUnavailable, "valid request is not applied without a verified handler");
    check(dqroute::route_request("unknown.effect", dqroute::ValueKind::Number, 1.0)
              == dqroute::Status::UnknownEffect, "unknown effect never reaches a handler");
    check(dqroute::validate_request("player.god_mode", dqroute::ValueKind::Number, 1.0)
              == dqroute::Status::TypeMismatch, "wrong control type is rejected");
    check(dqroute::validate_request("player.god_mode", dqroute::ValueKind::Boolean, 2.0)
              == dqroute::Status::OutOfRange, "boolean is restricted to zero or one");
    check(dqroute::validate_request("player.health_multiplier", dqroute::ValueKind::Number, 1.1)
              == dqroute::Status::StepMismatch, "slider step is enforced");
    check(dqroute::validate_request("skills.cooldown_multiplier", dqroute::ValueKind::Number, 10.1)
              == dqroute::Status::OutOfRange, "numeric upper bound is enforced");
    check(dqroute::validate_request("enemy.boss_variant", dqroute::ValueKind::Select, 3.0)
              == dqroute::Status::ValidatedOnly, "last valid select index is accepted");
    check(dqroute::validate_request("enemy.boss_variant", dqroute::ValueKind::Select, 4.0)
              == dqroute::Status::OutOfRange, "select index past option count is rejected");
    check(dqroute::validate_request("progression.add_levels", dqroute::ValueKind::None, 0.0)
              == dqroute::Status::ValidatedOnly, "action request carries no value");
    check(dqroute::validate_request("progression.add_levels", dqroute::ValueKind::None, 1.0)
              == dqroute::Status::OutOfRange, "action with an unexpected value is rejected");
    check(dqroute::validate_request("economy.gold_balance_target", dqroute::ValueKind::Integer, 20000000.0)
              == dqroute::Status::ValidatedOnly, "20 million is exactly representable in binary64 and within the catalog range");
    check(dqroute::validate_request("progression.player_level", dqroute::ValueKind::Integer, 5.5)
              == dqroute::Status::OutOfRange, "fractional integer input is rejected");
    check(dqroute::validate_request("player.movement_multiplier", dqroute::ValueKind::Number,
                                    std::numeric_limits<double>::quiet_NaN())
              == dqroute::Status::InvalidRequest, "non-finite input is rejected");

    check(!dqroute::register_route_gate(nullptr), "null registration API fails closed");
    check(dqroute::register_route_gate(&mock_register), "route gate registers by stable name");
    check(g_registry.size() == 1, "registry contains only the route gate in this test");
    dqroute::Status self_test_status = dqroute::Status::InvalidRequest;
    check(dqroute::invoke_route_gate_self_test(&mock_call, &self_test_status),
          "named dispatcher reaches the route gate and returns blocked status");
    check(self_test_status == dqroute::Status::HandlerUnavailable,
          "self-test proves input validation only, not a gameplay effect");

    dqprobe::AIVariableView request[4]{};
    request[0].type = dqprobe::kStringType;
    request[0].payload.string = dqroute::kRouteGateFunctionName;
    request[1].type = dqprobe::kStringType;
    request[1].payload.string = "progression.add_levels";
    request[2] = number(static_cast<double>(dqroute::ValueKind::None));
    request[3] = number(0.0);
    dqprobe::AIVariableView result{};
    check(mock_call(4, request, &result) == 1, "registered route callback returns one status value");
    check(result.type == dqprobe::kNumberType &&
              result.payload.number == static_cast<double>(dqroute::Status::HandlerUnavailable),
          "native route callback never claims an unapplied effect succeeded");

    request[2].payload.number = 99.0;
    check(mock_call(4, request, &result) == 1 &&
              result.payload.number == static_cast<double>(dqroute::Status::InvalidRequest),
          "invalid native value-kind code fails closed");

    check(!dqroute::unregister_route_gate(nullptr), "null unregister API fails closed");
    check(dqroute::unregister_route_gate(&mock_unregister), "route gate unregisters by stable name");
    check(g_registry.empty(), "registry is empty after unregister");
    check(mock_call(4, request, &result) == 0, "call after unregister is not dispatched");

    std::cout << "Assertions passed: " << g_passed << ", failed: " << g_failures << "\n";
    return g_failures == 0 ? 0 : 1;
}
