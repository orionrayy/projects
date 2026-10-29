#include "dq_native_cheat_router_v84.h"

#include <cmath>
#include <cstring>

namespace dqroute {
namespace {

constexpr CheatSpec kSpecs[] = {
    {"player.god_mode", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"player.infinite_mana", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"player.ignore_debuffs", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"player.no_knockback", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"player.auto_heal_threshold", ValueKind::Number, 1, 100, 1, 0, false, false},
    {"player.auto_heal", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"player.health_multiplier", ValueKind::Number, 1, 50, 0.25, 0, false, false},
    {"player.movement_multiplier", ValueKind::Number, 0.5, 5, 0.1, 0, false, false},
    {"player.attack_speed_multiplier", ValueKind::Number, 0.5, 5, 0.1, 0, false, false},
    {"combat.damage_multiplier", ValueKind::Number, 0, 100, 0.25, 0, false, false},
    {"combat.crit_chance", ValueKind::Number, 0, 100, 1, 0, false, false},
    {"combat.crit_damage_multiplier", ValueKind::Number, 1, 20, 0.25, 0, false, false},
    {"combat.armor_multiplier", ValueKind::Number, 0, 50, 0.25, 0, false, false},
    {"combat.lifesteal", ValueKind::Number, 0, 100, 1, 0, false, false},
    {"enemy.health_multiplier", ValueKind::Number, 0.01, 100, 0.25, 0, false, false},
    {"enemy.damage_multiplier", ValueKind::Number, 0, 10, 0.1, 0, false, false},
    {"enemy.move_speed_multiplier", ValueKind::Number, 0, 5, 0.1, 0, false, false},
    {"enemy.freeze_ai", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"enemy.boss_variant", ValueKind::Select, 0, 0, 0, 4, false, false},
    {"loot.drop_multiplier", ValueKind::Number, 0, 100, 0.25, 0, false, false},
    {"loot.rarity_floor", ValueKind::Select, 0, 0, 0, 4, false, false},
    {"loot.guaranteed_drop", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"economy.gold_reward_multiplier", ValueKind::Number, 0, 100, 0.25, 0, false, false},
    {"economy.gold_balance_target", ValueKind::Integer, 0, 2147483647, 1, 0, false, false},
    {"economy.gold_reward_amount", ValueKind::Integer, 1, 100000000, 1, 0, false, false},
    {"economy.dust_reward_amount", ValueKind::Integer, 1, 10000000, 1, 0, false, false},
    {"progression.player_level", ValueKind::Integer, 1, 1000, 1, 0, true, false},
    {"progression.floor_target", ValueKind::Integer, 1, 9999, 1, 0, true, false},
    {"progression.xp_multiplier", ValueKind::Number, 0, 100, 0.25, 0, false, false},
    {"progression.add_levels", ValueKind::None, 0, 0, 0, 0, true, false},
    {"progression.difficulty_override", ValueKind::Select, 0, 0, 0, 5, false, false},
    {"skills.cooldown_multiplier", ValueKind::Number, 0, 10, 0.1, 0, false, false},
    {"skills.mana_cost_multiplier", ValueKind::Number, 0, 10, 0.1, 0, false, false},
    {"skills.damage_multiplier", ValueKind::Number, 0, 100, 0.25, 0, false, false},
    {"skills.free_points", ValueKind::Integer, 0, 1000, 1, 0, false, false},
    {"inventory.capacity_bonus", ValueKind::Integer, 0, 1000, 1, 0, false, false},
    {"inventory.auto_identify", ValueKind::Boolean, 0, 0, 0, 0, false, false},
    {"inventory.rarity_override", ValueKind::Select, 0, 0, 0, 4, false, false},
    {"inventory.affix_reroll_count", ValueKind::Integer, 0, 20, 1, 0, false, false},
    {"inventory.grant_legend_fixture", ValueKind::None, 0, 0, 0, 0, true, false},
    {"inventory.grant_mythstone_fixture", ValueKind::None, 0, 0, 0, 0, true, false},
    {"inventory.grant_character_stone_fixture", ValueKind::None, 0, 0, 0, 0, true, false},
    {"inventory.grant_feat_fixture", ValueKind::None, 0, 0, 0, 0, true, false},
    {"rewards.add_battle", ValueKind::None, 0, 0, 0, 0, true, false},
    {"rewards.add_heroic", ValueKind::None, 0, 0, 0, 0, true, false},
    {"rewards.add_crystal", ValueKind::None, 0, 0, 0, 0, true, false},
    {"rewards.add_eternal", ValueKind::None, 0, 0, 0, 0, true, false},
    {"debug.snapshot", ValueKind::None, 0, 0, 0, 0, false, false},
    {"debug.undo_last_action", ValueKind::None, 0, 0, 0, 0, false, false},
    {"progression.quest_stage_target", ValueKind::Integer, 1, 9999, 1, 0, false, false},
};

static_assert(sizeof(kSpecs) / sizeof(kSpecs[0]) == 50,
              "Native route gate must track exactly 50 registry IDs");

dqprobe::AIVariableView make_number(float value) {
    dqprobe::AIVariableView result{};
    result.type = dqprobe::kNumberType;
    result.payload.number = value;
    return result;
}

dqprobe::AIFunctionView g_route_gate_function{
    kRouteGateFunctionName,
    &route_gate_callback,
    "nStatus",
    "sStableId,nValueKind,nValue",
    "Validates a first-50 cheat request; intentionally does not apply gameplay effects",
    0,
};

Status validate_value(const CheatSpec& spec, ValueKind actual_kind, double value) {
    if (actual_kind != spec.kind) {
        return Status::TypeMismatch;
    }
    if (!std::isfinite(value)) {
        return Status::InvalidRequest;
    }

    switch (spec.kind) {
        case ValueKind::None:
            return value == 0.0 ? Status::ValidatedOnly : Status::OutOfRange;

        case ValueKind::Boolean:
            return (value == 0.0 || value == 1.0)
                ? Status::ValidatedOnly : Status::OutOfRange;

        case ValueKind::Select:
            if (std::floor(value) != value || value < 0.0 ||
                value >= static_cast<double>(spec.option_count)) {
                return Status::OutOfRange;
            }
            return Status::ValidatedOnly;

        case ValueKind::Integer:
            if (std::floor(value) != value || value < spec.min_value ||
                value > spec.max_value) {
                return Status::OutOfRange;
            }
            // AIVariable number payloads are float32. Above 2^24, consecutive
            // integers are not all representable, so never silently round them.
            if (std::abs(value) > kMaxExactFloat32Integer) {
                return Status::PrecisionLoss;
            }
            return Status::ValidatedOnly;

        case ValueKind::Number:
            if (value < spec.min_value || value > spec.max_value) {
                return Status::OutOfRange;
            }
            if (spec.step > 0.0) {
                const double steps = (value - spec.min_value) / spec.step;
                if (std::abs(steps - std::round(steps)) > 0.001) {
                    return Status::StepMismatch;
                }
            }
            return Status::ValidatedOnly;
    }
    return Status::InvalidRequest;
}

}  // namespace

std::size_t spec_count() {
    return sizeof(kSpecs) / sizeof(kSpecs[0]);
}

const CheatSpec* spec_at(std::size_t index) {
    return index < spec_count() ? &kSpecs[index] : nullptr;
}

const CheatSpec* find_spec(const char* id) {
    if (id == nullptr || id[0] == '\0') {
        return nullptr;
    }
    for (const auto& spec : kSpecs) {
        if (std::strcmp(spec.id, id) == 0) {
            return &spec;
        }
    }
    return nullptr;
}

std::size_t static_route_candidate_count() {
    std::size_t count = 0;
    for (const auto& spec : kSpecs) {
        if (spec.static_route_candidate) {
            ++count;
        }
    }
    return count;
}

Status validate_request(const char* id, ValueKind actual_kind, double value) {
    const CheatSpec* spec = find_spec(id);
    if (spec == nullptr) {
        return Status::UnknownEffect;
    }
    return validate_value(*spec, actual_kind, value);
}

Status route_request(const char* id, ValueKind actual_kind, double value) {
    const Status input_status = validate_request(id, actual_kind, value);
    if (input_status != Status::ValidatedOnly) {
        return input_status;
    }

    const CheatSpec* spec = find_spec(id);
    if (spec == nullptr) {
        return Status::UnknownEffect;
    }
    if (!spec->runtime_enabled) {
        return Status::HandlerUnavailable;
    }

    // No native gameplay backend is wired into this source-only prototype.
    // Even an accidentally promoted registry flag must not claim an effect.
    return Status::BackendUnavailable;
}

int route_gate_callback(int input_count, const dqprobe::AIVariableView* inputs,
                        dqprobe::AIVariableView* outputs) {
    if (outputs == nullptr) {
        return 0;
    }

    Status status = Status::InvalidRequest;
    if (input_count == 3 && inputs != nullptr &&
        inputs[0].type == dqprobe::kStringType &&
        inputs[0].payload.string != nullptr &&
        inputs[1].type == dqprobe::kNumberType &&
        inputs[2].type == dqprobe::kNumberType &&
        std::isfinite(inputs[1].payload.number) &&
        std::floor(inputs[1].payload.number) == inputs[1].payload.number &&
        inputs[1].payload.number >= static_cast<float>(ValueKind::None) &&
        inputs[1].payload.number <= static_cast<float>(ValueKind::Select)) {
        const auto kind = static_cast<ValueKind>(
            static_cast<int>(inputs[1].payload.number));
        status = route_request(inputs[0].payload.string, kind,
                               static_cast<double>(inputs[2].payload.number));
    }

    outputs[0] = make_number(static_cast<float>(status));
    return 1;
}

dqprobe::AIFunctionView* route_gate_function() {
    return &g_route_gate_function;
}

bool register_route_gate(dqprobe::RegisterFunctionFn register_function) {
    if (register_function == nullptr) {
        return false;
    }
    return register_function(kRouteGateFunctionName, &g_route_gate_function);
}

bool unregister_route_gate(dqprobe::UnregisterFunctionFn unregister_function) {
    if (unregister_function == nullptr) {
        return false;
    }
    unregister_function(kRouteGateFunctionName);
    return true;
}


bool invoke_route_gate_self_test(
    dqprobe::CallClientFunctionFn call_client_function, Status* status_out) {
    if (call_client_function == nullptr || status_out == nullptr) {
        return false;
    }

    dqprobe::AIVariableView arguments[4]{};
    arguments[0].type = dqprobe::kStringType;
    arguments[0].payload.string = kRouteGateFunctionName;
    arguments[1].type = dqprobe::kStringType;
    arguments[1].payload.string = "player.god_mode";
    arguments[2] = make_number(static_cast<float>(ValueKind::Boolean));
    arguments[3] = make_number(0.0f);

    dqprobe::AIVariableView output{};
    const int output_count = call_client_function(4, arguments, &output);
    if (output_count != 1 || output.type != dqprobe::kNumberType ||
        !std::isfinite(output.payload.number) ||
        std::floor(output.payload.number) != output.payload.number ||
        output.payload.number < static_cast<float>(Status::ValidatedOnly) ||
        output.payload.number > static_cast<float>(Status::BackendUnavailable)) {
        return false;
    }

    *status_out = static_cast<Status>(static_cast<int>(output.payload.number));
    // A valid request must still be blocked because no gameplay handler is
    // proven. A success-like result would fail this probe.
    return *status_out == Status::HandlerUnavailable;
}

}  // namespace dqroute
