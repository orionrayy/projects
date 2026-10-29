#include "dq_native_probe_v64.h"

#include <iostream>
#include <string>
#include <type_traits>
#include <unordered_map>

namespace {

std::unordered_map<std::string, dqprobe::AIFunctionView*> g_registry;
int failures = 0;

bool mock_register(const char* name, dqprobe::AIFunctionView* function) {
    if (name == nullptr || function == nullptr || function->pCallback == nullptr ||
        function->pName == nullptr || std::string(name) != function->pName) {
        return false;
    }
    return g_registry.emplace(name, function).second;
}

void mock_unregister(const char* name) {
    if (name != nullptr) {
        g_registry.erase(name);
    }
}

int mock_call_client_function(int argument_count,
                              const dqprobe::AIVariableView* arguments,
                              dqprobe::AIVariableView* outputs) {
    if (argument_count < 1 || arguments == nullptr ||
        arguments[0].type != dqprobe::kStringType ||
        arguments[0].payload.string == nullptr) {
        return 0;
    }
    const auto found = g_registry.find(arguments[0].payload.string);
    if (found == g_registry.end() || found->second == nullptr ||
        found->second->pCallback == nullptr) {
        return 0;
    }
    return found->second->pCallback(argument_count - 1, arguments + 1, outputs);
}

void check(bool condition, const char* label) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << label << "\n";
    } else {
        std::cout << "PASS: " << label << "\n";
    }
}

}  // namespace

int main() {
    static_assert(sizeof(dqprobe::AIVariableView) == 16);
    static_assert(std::is_same_v<decltype(dqprobe::AIVariableView::Payload::number), double>);
    static_assert(sizeof(dqprobe::AIFunctionView) == 48);
    static_assert(offsetof(dqprobe::AIFunctionView, pCallback) == 8);

    g_registry.clear();
    check(!dqprobe::register_probe(nullptr), "null register API fails closed");
    check(!dqprobe::invoke_probe(nullptr), "null dispatcher fails closed");
    check(!dqprobe::unregister_probe(nullptr), "null unregister API fails closed");

    check(dqprobe::register_probe(&mock_register), "register stable side-effect-free function name");
    check(g_registry.size() == 1, "registry contains exactly one function");
    auto* function = dqprobe::probe_function();
    check(function != nullptr && function->pName != nullptr &&
              std::string(function->pName) == dqprobe::kProbeFunctionName,
          "static function name and storage remain stable");
    check(dqprobe::invoke_probe(&mock_call_client_function),
          "binary64 numeric input reaches callback and 21 returns as 42");

    dqprobe::AIVariableView bad_input{};
    bad_input.type = dqprobe::kStringType;
    dqprobe::AIVariableView bad_output{};
    check(dqprobe::probe_callback(0, nullptr, nullptr) == 0,
          "callback rejects absent inputs and outputs");
    check(dqprobe::probe_callback(1, &bad_input, &bad_output) == 0,
          "callback rejects wrong input type");

    check(dqprobe::unregister_probe(&mock_unregister), "unregister function by stable name");
    check(g_registry.empty(), "registry empty after unregister");
    check(!dqprobe::invoke_probe(&mock_call_client_function),
          "dispatch after unregister fails closed");

    if (failures != 0) {
        std::cerr << failures << " test(s) failed\n";
        return 1;
    }
    std::cout << "All side-effect-free probe tests passed\n";
    return 0;
}
