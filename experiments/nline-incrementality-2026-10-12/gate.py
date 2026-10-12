"""Pre-specified, conservative sponsor multiplier gate for a published nLine vacancy.

No empirical probability is asserted; all inputs other than 1000 NLe/day wages
and the 3-5 day advertised fieldwork duration are hypothetical scenario values.
Training/field expense per diems are NOT earnings in this model.
"""
from dataclasses import dataclass, asdict
import argparse
import json
import math

ADVERTISED_FIELD_WAGE_NLE_PER_DAY = 1000
ADVERTISED_FIELD_DAYS_MIN = 3
ADVERTISED_FIELD_DAYS_MAX = 5


def finite_nonnegative(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")


@dataclass(frozen=True)
class Case:
    field_days: int = 4
    worker_extra_field_cash_per_day: float = 0
    worker_alternative_earnings_per_field_day: float = 0
    worker_extra_training_cash: float = 0
    worker_alternative_earnings_over_training: float = 0
    additional_training_share: float = 0
    cost_per_applicant: float = 0
    displacement_and_harm_per_applicant: float = 0
    additional_hire_share: float = 0

    def __post_init__(self):
        if not isinstance(self.field_days, int) or not 3 <= self.field_days <= 5:
            raise ValueError('field_days must be exactly 3, 4, or 5')
        for field, val in asdict(self).items():
            if field != 'field_days':
                finite_nonnegative(field, val)
        for field in ('additional_training_share', 'additional_hire_share'):
            if getattr(self, field) > 1:
                raise ValueError(f'{field} must not exceed one')


def evaluate(c: Case) -> dict:
    """Benefit attributable to intervention, not all wages paid by employer.

    Additional hire share is the causal percentage-point lift versus no assistance,
    not an observed employment rate. Additional training share is the causal increase
    in training attendance due to assistance. Field unreimbursed cash and alternative
    earnings are deducted; training allowances only offset expenses if observed.
    """
    field_incremental_net_per_induced_hire = c.field_days * (
        ADVERTISED_FIELD_WAGE_NLE_PER_DAY -
        c.worker_extra_field_cash_per_day -
        c.worker_alternative_earnings_per_field_day)
    training_downside_per_extra_trainee = (
        c.worker_extra_training_cash + c.worker_alternative_earnings_over_training)
    fixed_harm_and_cost = (
        c.additional_training_share * training_downside_per_extra_trainee +
        c.displacement_and_harm_per_applicant)
    estimated_incremental_benefit = (
        c.additional_hire_share * field_incremental_net_per_induced_hire -
        fixed_harm_and_cost)
    if field_incremental_net_per_induced_hire <= 0:
        threshold = None
        classification = 'FAIL: fieldwork has no positive net marginal benefit'
    else:
        threshold = (c.cost_per_applicant + fixed_harm_and_cost) / field_incremental_net_per_induced_hire
        classification = ('UNATTAINABLE: more than 100% incremental hires needed' if threshold > 1
                          else 'NOT ESTABLISHED: causal incremental hiring rate is unmeasured')
    sponsor_multiplier = (estimated_incremental_benefit / c.cost_per_applicant
                          if c.cost_per_applicant > 0 else None)
    return {
        'field_incremental_net_per_induced_hire_NLe': field_incremental_net_per_induced_hire,
        'training_downside_per_extra_trainee_NLe': training_downside_per_extra_trainee,
        'net_benefit_per_applicant_NLe_given_assumed_delta': estimated_incremental_benefit,
        'cost_per_applicant_NLe': c.cost_per_applicant,
        'minimum_absolute_extra_hire_share_to_beat_M_1': threshold,
        'sponsor_multiplier_given_assumed_delta': sponsor_multiplier,
        'disposition': classification,
        'evidence_label': 'SYNTHETIC assumptions; advertised salary is not an outcome',
    }


def demo() -> list[dict]:
    # All scenario magnitudes other than field wage and field days are synthetic.
    cases = [
        ('low-cost', Case(field_days=4, cost_per_applicant=50)),
        ('moderate', Case(field_days=4, worker_extra_field_cash_per_day=50,
                          worker_alternative_earnings_per_field_day=100,
                          worker_alternative_earnings_over_training=750,
                          additional_training_share=0.2, cost_per_applicant=250)),
        ('high-friction', Case(field_days=4, worker_extra_field_cash_per_day=150,
                              worker_alternative_earnings_per_field_day=250,
                              worker_alternative_earnings_over_training=1500,
                              additional_training_share=0.6, cost_per_applicant=600)),
        ('unattainable', Case(field_days=3, worker_extra_field_cash_per_day=300,
                             worker_alternative_earnings_per_field_day=300,
                             worker_alternative_earnings_over_training=1000,
                             additional_training_share=0.5, cost_per_applicant=1400)),
    ]
    return [{'name': name, 'input': asdict(c), 'result': evaluate(c)} for name, c in cases]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='show labelled synthetic scenario thresholds')
    args = parser.parse_args()
    print(json.dumps(demo() if args.demo else evaluate(Case()), indent=2))
