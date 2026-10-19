"""Synthetic review reform: adds 1000 to spm_unit_benefits on top of whatever is registered when applied."""
from policyengine_us.model_api import *


def create_synth() -> Reform:
    class reform(Reform):
        def apply(self):
            current = self.variables["spm_unit_benefits"]

            class spm_unit_benefits(Variable):
                value_type = float
                entity = SPMUnit
                label = "Benefits"
                definition_period = YEAR
                unit = USD

                def formula(spm_unit, period, parameters):
                    return current.get_formula(period)(spm_unit, period, parameters) + 1000

            self.update_variable(spm_unit_benefits)

    return reform


synth = create_synth()
