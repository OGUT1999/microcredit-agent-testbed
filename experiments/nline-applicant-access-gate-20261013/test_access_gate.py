import unittest
from access_gate import Eligibility, application_gate, first_day_cash_gap, classify_assistance

OK = Eligibility(True, True, True, True, True, True, True, True)

class GateTests(unittest.TestCase):
    def test_no_consent_no_action(self):
        self.assertEqual(application_gate(Eligibility(False, True, True, True, True)), 'NO_CONTACT_NO_APPLICATION')
    def test_consent_requires_explicit_boolean_true(self):
        for v in ("yes", "no", 1, 0, None, [], {}):
            e = Eligibility(v, True, True, True, True)
            self.assertEqual(application_gate(e), 'NO_CONTACT_NO_APPLICATION')
    def test_unknowns_fail_closed(self):
        self.assertEqual(application_gate(Eligibility(True, True, None, True, True)), 'VERIFY_ELIGIBILITY_OR_OPEN_STATUS')
    def test_unsuitable_device_stop(self):
        self.assertEqual(application_gate(Eligibility(True, True, False, True, True)), 'DO_NOT_SUGGEST_APPLICATION')
    def test_published_application_window_required(self):
        self.assertEqual(application_gate(Eligibility(True, True, True, True, False, True, True, True)), 'DO_NOT_SUGGEST_APPLICATION')
    def test_known_eligibility_only_allows_consideration(self):
        self.assertEqual(application_gate(OK), 'ELIGIBLE_TO_CONSIDER_VOLUNTARY_APPLICATION')
    def test_unknown_payment_and_cost_never_create_loan(self):
        self.assertEqual(classify_assistance(OK)['finance'],'UNKNOWN_COSTS_NO_LOAN')
    def test_hypothetical_cost_gap_cannot_by_itself_authorize_loan(self):
        x=classify_assistance(OK, 100, 0, True, True)
        self.assertEqual(x['gap'],'100')
        self.assertTrue(x['finance'].startswith('VERIFY_EMPLOYER_PREPAY'))
    def test_no_cost_gap_has_no_financing(self):
        self.assertEqual(classify_assistance(OK, 100, 100, True, True)['finance'], 'NO_LOAN_NO_GUARANTEE')
    def test_unknown_cash_fails_closed(self):
        self.assertIsNone(first_day_cash_gap(100, None))
    def test_no_negative_nonfinite_or_boolean_amount(self):
        for v in ('nan','Infinity',-2,True):
            self.assertIsNone(first_day_cash_gap(v,0))
    def test_decimal_exact(self):
        self.assertEqual(str(first_day_cash_gap('0.30','0.20')),'0.10')
    def test_mandatory_cv_and_cover_letter(self):
        for field in ('cv_ready', 'cover_letter_ready'):
            args = dict(OK.__dict__)
            args[field] = False
            self.assertEqual(application_gate(Eligibility(**args)), 'DO_NOT_SUGGEST_APPLICATION')
            args[field] = None
            self.assertEqual(application_gate(Eligibility(**args)), 'VERIFY_ELIGIBILITY_OR_OPEN_STATUS')
    def test_training_and_fieldwork_availability(self):
        args = dict(OK.__dict__)
        args['available_for_full_training_and_fieldwork'] = False
        self.assertEqual(application_gate(Eligibility(**args)), 'DO_NOT_SUGGEST_APPLICATION')
        args['available_for_full_training_and_fieldwork'] = None
        self.assertEqual(application_gate(Eligibility(**args)), 'VERIFY_ELIGIBILITY_OR_OPEN_STATUS')
    def test_backward_compatible_call_fails_closed(self):
        self.assertEqual(application_gate(Eligibility(True, True, True, True, True)),
                         'VERIFY_ELIGIBILITY_OR_OPEN_STATUS')
    def test_no_personal_identifiers_in_inputs(self):
        fields=set(Eligibility.__dataclass_fields__)
        self.assertFalse(fields.intersection({'name','email','address','phone','wallet','id_number'}))
if __name__=='__main__':unittest.main()
