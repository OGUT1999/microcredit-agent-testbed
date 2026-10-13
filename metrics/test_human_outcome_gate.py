"""Synthetic adversarial records test readiness guards, not human outcomes."""
from copy import deepcopy
import unittest

from human_outcome_gate import classify, COST_CATEGORIES, READY, UNKNOWN


def reference(name="synthetic-evidence"):
    return {"source": "fixture:" + name, "observed_at": "2026-10-13T14:00:00Z"}


def packet():
    # Every receipt and assertion here is fictional. READY means structurally ready
    # for human review; never treat these fixtures as real observed outcomes.
    def welfare(start, end, value):
        return {"household_id": "synthetic-household", "population_scope": "whole_household",
                "measure": "consumption", "unit": "local_currency_per_person_day", "currency": "NLE",
                "price_basis": "local_constant_2026", "amount": value,
                "period_start": start, "period_end": end, "household_size": 2,
                "person_days": "60", "household_size_evidence": reference("household"),
                "evidence": reference("welfare")}
    return {
        "context": {"locality": "synthetic-locality", "local_currency": "NLE"},
        "job": {"id": "synthetic-job", "worker_id": "synthetic-worker",
                "client_id": "synthetic-client", "client_independence_evidence": reference("independence"),
                "consent_evidence": reference("consent"),
                "household_id": "synthetic-household", "evidence_kind": "observed_real_value",
                "independent_client": True, "useful_work_accepted": True, "consent": True,
                "acceptance_evidence": reference("acceptance"), "time_hours": "8",
                "time_evidence": reference("worker-time"),
                "payout": {"kind": "earned_wage", "amount": "1000", "currency": "NLE",
                           "settled": True, "spendable_locally": True, "evidence": reference("payout")},
                "worker_costs": {key: {"amount": "0", "currency": "NLE", "evidence": reference(key),
                                      "already_deducted_from_payout": False}
                                 for key in COST_CATEGORIES}},
        "baseline": welfare("2026-06-01", "2026-06-30", "15"),
        "followup": welfare("2026-09-01", "2026-09-30", "30"),
        "poverty_line": {"kind": "authoritative_local", "authority": "synthetic-statistics-office",
                         "locality": "synthetic-locality", "measure": "consumption",
                         "unit": "local_currency_per_person_day", "currency": "NLE",
                         "price_basis": "local_constant_2026", "amount": "20",
                         "valid_from": "2026-01-01", "valid_to": "2026-12-31", "evidence": reference("line")},
        "counterfactual": {"design": "randomized_comparison", "outcome_unit": "household", "assignment_unit": "client",
                           "estimand": "Incremental household welfare, after displacement and harms",
                           "assumptions": ["Comparable measurement; randomization intact"],
                           "limitations": ["Small sample and bounded followup"],
                           "protocol": reference("protocol"), "comparison_evidence": reference("comparison"),
                           "credible_basis": reference("design-review")},
        "harms": {key: reference(key) for key in
                  ("displacement", "worker_welfare", "costs_and_time", "adverse_events")},
    }


class HumanOutcomeGateTests(unittest.TestCase):
    def test_empty_packet_never_zero_outcome(self):
        result = classify({})
        for key in ("earned_income_packet", "household_comparison_packet", "poverty_impact_evaluation_packet"):
            self.assertEqual(result[key]["state"], UNKNOWN)
            self.assertTrue(result[key]["gaps"])
        self.assertNotIn("reported_earnings_arithmetic", result)

    def test_complete_fixture_only_ready_not_verified_or_causal(self):
        result = classify(packet())
        self.assertEqual(result["poverty_impact_evaluation_packet"]["state"], READY)
        self.assertEqual(result["reported_earnings_arithmetic"]["net_cash"], "1000")
        self.assertEqual(set(result), {"scope", "earned_income_packet", "household_comparison_packet",
                                      "poverty_impact_evaluation_packet", "reported_earnings_arithmetic"})
        self.assertIn("no authentication", result["scope"])

    def test_wage_without_household_baseline_is_not_poverty_packet(self):
        case = packet()
        del case["baseline"]
        result = classify(case)
        self.assertEqual(result["earned_income_packet"]["state"], READY)
        self.assertEqual(result["poverty_impact_evaluation_packet"]["state"], UNKNOWN)

    def test_valid_individual_wage_does_not_require_household_collection(self):
        case = packet()
        del case["job"]["household_id"]
        del case["baseline"]
        del case["followup"]
        result = classify(case)
        self.assertEqual(result["earned_income_packet"]["state"], READY)
        self.assertEqual(result["household_comparison_packet"]["state"], UNKNOWN)
        self.assertEqual(result["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        self.assertEqual(result["reported_earnings_arithmetic"]["net_cash"], "1000")

    def test_assignment_unit_is_distinct_from_household_outcome_unit(self):
        for assignment in ("household", "worker", "noncompeting_job", "client", "community"):
            case = packet()
            case["counterfactual"]["assignment_unit"] = assignment
            self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], READY)
        for assignment in (None, "competing_application", "application", "unreported"):
            case = packet()
            case["counterfactual"]["assignment_unit"] = assignment
            self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        case = packet()
        case["counterfactual"]["outcome_unit"] = "worker"
        self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)

    def test_models_testnet_and_reimbursements_are_not_earnings(self):
        for kind in ("synthetic", "modeled", "testnet"):
            case = packet()
            case["job"]["evidence_kind"] = kind
            result = classify(case)
            self.assertEqual(result["earned_income_packet"]["state"], UNKNOWN)
            self.assertNotIn("reported_earnings_arithmetic", result)
        for kind in ("returned_principal", "expense_reimbursement", "mixed_unsegregated_transfer"):
            case = packet()
            case["job"]["payout"]["kind"] = kind
            self.assertEqual(classify(case)["earned_income_packet"]["state"], UNKNOWN)

    def test_known_zero_cost_requires_evidence_unknown_is_not_zero(self):
        self.assertEqual(classify(packet())["earned_income_packet"]["state"], READY)
        for field in ("amount", "evidence", "already_deducted_from_payout"):
            case = packet()
            del case["job"]["worker_costs"]["payout_fees"][field]
            result = classify(case)
            self.assertEqual(result["earned_income_packet"]["state"], UNKNOWN)
            self.assertNotIn("reported_earnings_arithmetic", result)

    def test_withheld_costs_not_subtracted_twice(self):
        case = packet()
        case["job"]["payout"]["amount"] = "900"
        case["job"]["worker_costs"]["taxes"].update(amount="100", already_deducted_from_payout=True)
        case["job"]["worker_costs"]["work_expenses"].update(amount="50", already_deducted_from_payout=False)
        arithmetic = classify(case)["reported_earnings_arithmetic"]
        self.assertEqual(arithmetic["settled_wage_received"], "900")
        self.assertEqual(arithmetic["worker_costs_already_deducted"], "100")
        self.assertEqual(arithmetic["additional_worker_cash_costs"], "50")
        self.assertEqual(arithmetic["net_cash"], "850")
        self.assertNotIn("gross", arithmetic)
        case["job"]["worker_costs"]["taxes"]["already_deducted_from_payout"] = False
        case["job"]["worker_costs"]["work_expenses"]["amount"] = "0"
        self.assertEqual(classify(case)["reported_earnings_arithmetic"]["net_cash"], "800")
        for flag in ("true", "false", 1, 0, [], {}):
            case["job"]["worker_costs"]["taxes"]["already_deducted_from_payout"] = flag
            with self.assertRaises(ValueError):
                classify(case)

    def test_negative_reported_cash_is_retained_not_success(self):
        case = packet()
        case["job"]["worker_costs"]["other"]["amount"] = "1200"
        result = classify(case)
        self.assertEqual(result["reported_earnings_arithmetic"]["net_cash"], "-200")
        self.assertEqual(result["earned_income_packet"]["state"], READY)

    def test_household_income_is_not_consumption(self):
        case = packet()
        case["followup"]["measure"] = "income"
        self.assertEqual(classify(case)["household_comparison_packet"]["state"], UNKNOWN)
        case = packet()
        for key in ("baseline", "followup"):
            case[key]["measure"] = "income"
        self.assertEqual(classify(case)["household_comparison_packet"]["state"], READY)
        self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)

    def test_worker_wage_is_not_household_welfare(self):
        case = packet()
        case["followup"]["population_scope"] = "individual_worker"
        self.assertEqual(classify(case)["household_comparison_packet"]["state"], UNKNOWN)

    def test_ppp_and_nominal_fx_cannot_be_local_constant_welfare(self):
        for basis in ("2021_PPP_USD", "nominal_USD_FX", "local_nominal"):
            case = packet()
            for key in ("baseline", "followup", "poverty_line"):
                case[key]["price_basis"] = basis
            self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        case = packet()
        case["poverty_line"].update(kind="international_PPP", currency="USD", amount="3")
        self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)

    def test_unrelated_household_or_person_days_blocks_comparison(self):
        for updates in ({"household_id": "other-household"}, {"household_size": 4}, {"person_days": "30"}):
            case = packet()
            case["followup"].update(updates)
            self.assertEqual(classify(case)["household_comparison_packet"]["state"], UNKNOWN)

    def test_above_line_after_below_line_before_is_not_causal(self):
        case = packet()
        del case["counterfactual"]
        result = classify(case)
        self.assertEqual(result["household_comparison_packet"]["state"], READY)
        self.assertEqual(result["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        case = packet()
        case["counterfactual"]["design"] = "before_after"
        self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)

    def test_missing_harms_or_independent_client_is_not_evaluation_ready(self):
        for key in ("displacement", "worker_welfare", "costs_and_time", "adverse_events"):
            case = packet()
            del case["harms"][key]
            self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        case = packet()
        case["job"]["independent_client"] = False
        self.assertEqual(classify(case)["earned_income_packet"]["state"], UNKNOWN)
        for change in ("same-client", "missing-independence", "missing-consent"):
            case = packet()
            if change == "same-client":
                case["job"]["client_id"] = case["job"]["worker_id"]
            else:
                del case["job"]["client_independence_evidence" if change == "missing-independence" else "consent_evidence"]
            self.assertEqual(classify(case)["earned_income_packet"]["state"], UNKNOWN)

    def test_unsettled_locked_or_wrong_currency_not_spendable(self):
        for updates in ({"settled": False}, {"spendable_locally": False}, {"currency": "USD"}):
            case = packet()
            case["job"]["payout"].update(updates)
            self.assertEqual(classify(case)["earned_income_packet"]["state"], UNKNOWN)

    def test_stale_line_and_overlapping_periods_are_gaps(self):
        case = packet()
        case["poverty_line"]["valid_to"] = "2026-07-01"
        self.assertEqual(classify(case)["poverty_impact_evaluation_packet"]["state"], UNKNOWN)
        case = packet()
        case["followup"].update(period_start="2026-06-01", period_end="2026-06-30")
        self.assertEqual(classify(case)["household_comparison_packet"]["state"], UNKNOWN)

    def test_invalid_types_and_unrecognized_fields_fail_loudly(self):
        for value in (True, 0.5, "NaN", "Infinity", "-1", "garbage"):
            case = packet()
            case["job"]["payout"]["amount"] = value
            with self.assertRaises(ValueError):
                classify(case)
        for mutate in (
            lambda c: c.update(poverty_eliminated=True),
            lambda c: c["job"].update(independent_client="true"),
            lambda c: c["baseline"].update(household_size=True),
            lambda c: c["job"]["payout"]["evidence"].update(observed_at="2026-10-13T14:00:00"),
            lambda c: c["baseline"].update(period_end="2026-05-31"),
        ):
            case = deepcopy(packet())
            mutate(case)
            with self.assertRaises(ValueError):
                classify(case)


if __name__ == "__main__":
    unittest.main()
