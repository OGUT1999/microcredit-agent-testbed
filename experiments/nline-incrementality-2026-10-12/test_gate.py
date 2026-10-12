import unittest
from dataclasses import replace
from gate import Case, evaluate, demo

class GateTests(unittest.TestCase):
    def test_advertised_wage_three_to_five_days(self):
        self.assertEqual(evaluate(Case(field_days=3))['field_incremental_net_per_induced_hire_NLe'],3000)
        self.assertEqual(evaluate(Case(field_days=5))['field_incremental_net_per_induced_hire_NLe'],5000)
    def test_low_cost(self):
        self.assertAlmostEqual(evaluate(Case(cost_per_applicant=50))['minimum_absolute_extra_hire_share_to_beat_M_1'],0.0125)
    def test_training_cost_not_assumed_for_unchanged_training(self):
        a=Case(cost_per_applicant=100,worker_alternative_earnings_over_training=1000)
        self.assertEqual(evaluate(a)['minimum_absolute_extra_hire_share_to_beat_M_1'],0.025)
    def test_training_downside_only_for_incremental_training(self):
        a=Case(cost_per_applicant=100,worker_alternative_earnings_over_training=1000,additional_training_share=.5)
        self.assertEqual(evaluate(a)['minimum_absolute_extra_hire_share_to_beat_M_1'],.15)
    def test_net_earnings_exclude_allowances(self):
        self.assertEqual(evaluate(Case(field_days=4))['field_incremental_net_per_induced_hire_NLe'],4000)
    def test_cash_and_alternative_income_are_real_costs(self):
        c=Case(field_days=4,worker_extra_field_cash_per_day=50,worker_alternative_earnings_per_field_day=100)
        self.assertEqual(evaluate(c)['field_incremental_net_per_induced_hire_NLe'],3400)
    def test_harm_reduces_benefit(self):
        a=Case(additional_hire_share=.2,cost_per_applicant=100)
        self.assertEqual(evaluate(replace(a,displacement_and_harm_per_applicant=200))['net_benefit_per_applicant_NLe_given_assumed_delta'],600)
    def test_multiplier_separates_salary_and_attribution(self):
        a=Case(additional_hire_share=.1,cost_per_applicant=100)
        self.assertEqual(evaluate(a)['sponsor_multiplier_given_assumed_delta'],4)
    def test_unmeasured_lift_never_marked_passed(self):
        self.assertIn('NOT ESTABLISHED',evaluate(Case(cost_per_applicant=10))['disposition'])
    def test_unattainable(self):
        self.assertIn('UNATTAINABLE',demo()[3]['result']['disposition'])
    def test_zero_or_negative_field_value_rejected(self):
        self.assertIsNone(evaluate(Case(worker_alternative_earnings_per_field_day=1200))['minimum_absolute_extra_hire_share_to_beat_M_1'])
    def test_cost_monotonicity(self):
        for x in range(0,900,30):
            a=evaluate(Case(cost_per_applicant=x))
            b=evaluate(Case(cost_per_applicant=x+10))
            self.assertLessEqual(a['minimum_absolute_extra_hire_share_to_beat_M_1'],b['minimum_absolute_extra_hire_share_to_beat_M_1'])
    def test_extra_training_monotonicity(self):
        a=Case(cost_per_applicant=100,worker_alternative_earnings_over_training=800)
        self.assertLessEqual(evaluate(replace(a,additional_training_share=.2))['minimum_absolute_extra_hire_share_to_beat_M_1'],evaluate(replace(a,additional_training_share=.3))['minimum_absolute_extra_hire_share_to_beat_M_1'])
    def test_negative_rejected(self):
        with self.assertRaises(ValueError): Case(cost_per_applicant=-1)
    def test_prob_outside_unit_interval_rejected(self):
        with self.assertRaises(ValueError): Case(additional_hire_share=1.01)
    def test_nan_rejected(self):
        with self.assertRaises(ValueError): Case(cost_per_applicant=float('nan'))
    def test_days_outside_range_rejected(self):
        with self.assertRaises(ValueError): Case(field_days=6)
    def test_zero_denominator_explicit(self):
        self.assertIsNone(evaluate(Case(cost_per_applicant=0,additional_hire_share=.2))['sponsor_multiplier_given_assumed_delta'])
    def test_not_income_what_employer_spends(self):
        self.assertEqual(evaluate(Case())['net_benefit_per_applicant_NLe_given_assumed_delta'],0)

if __name__=='__main__': unittest.main()
