import unittest
from decimal import (Decimal, DefaultContext, localcontext, ROUND_UP, Inexact,
                     Rounded, InvalidOperation)
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
    def test_confirmation_flags_require_literal_boolean_true(self):
        invalid = ("yes", "no", "false", 1, 0, None, [], {})
        for value in invalid:
            with self.subTest(flag="employer_confirmed", value=value):
                self.assertEqual(
                    classify_assistance(OK, 100, 0, value, True)['finance'],
                    'UNKNOWN_COSTS_NO_LOAN')
            with self.subTest(flag="actual_worker_cost_known", value=value):
                self.assertEqual(
                    classify_assistance(OK, 100, 0, True, value)['finance'],
                    'UNKNOWN_COSTS_NO_LOAN')
    def test_decimal_exact(self):
        self.assertEqual(str(first_day_cash_gap('0.30','0.20')),'0.10')
    def test_cash_gap_independent_of_caller_context(self):
        for precision in (1, 3, 28, 80):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                ctx.rounding = ROUND_UP
                ctx.Emin, ctx.Emax = -1, 1
                ctx.traps[Inexact] = ctx.traps[Rounded] = True
                ctx.clear_flags()
                self.assertEqual(first_day_cash_gap('123.45', '1.00'), Decimal('122.45'))
                self.assertEqual(str(first_day_cash_gap('0.30', '0.20')), '0.10')
                self.assertEqual(first_day_cash_gap('1', '2'), Decimal(0))
                self.assertFalse(any(ctx.flags.values()))
                self.assertEqual(ctx.prec, precision)
                self.assertEqual(ctx.rounding, ROUND_UP)
                self.assertEqual((ctx.Emin, ctx.Emax), (-1, 1))
    def test_invalid_parser_does_not_touch_caller_flags(self):
        for trapped in (False, True):
            with localcontext() as ctx:
                ctx.traps[InvalidOperation] = trapped
                ctx.clear_flags()
                for value in ('not-money', 'NaN', 'sNaN', 'Infinity', '-Infinity'):
                    self.assertIsNone(first_day_cash_gap(value, '0'))
                self.assertFalse(any(ctx.flags.values()))
    def test_all_caller_traps_and_preexisting_flags_preserved(self):
        with localcontext() as ctx:
            ctx.prec = 1
            ctx.Emin = ctx.Emax = 0
            ctx.clamp = 1
            for signal in ctx.traps:
                ctx.traps[signal] = True
            ctx.flags[Inexact] = True
            before = ctx.copy()
            self.assertEqual(first_day_cash_gap('123.45', '1.00'), Decimal('122.45'))
            self.assertIsNone(first_day_cash_gap('not-money', 0))
            self.assertEqual(dict(ctx.flags), dict(before.flags))
            self.assertEqual(dict(ctx.traps), dict(before.traps))
            for attr in ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp'):
                self.assertEqual(getattr(ctx, attr), getattr(before, attr))
    def test_maximum_supported_amount_and_smallest_scale_exact(self):
        biggest = '9' * 32 + '.' + '9' * 12
        expected = '9' * 32 + '.' + '9' * 11 + '8'
        with localcontext() as ctx:
            ctx.prec = 1
            ctx.Emax = 1
            self.assertEqual(str(first_day_cash_gap(biggest, '0.000000000001')), expected)
            self.assertEqual(str(first_day_cash_gap(Decimal('1E-12'), 0)), '1E-12')
    def test_out_of_bounds_inputs_fail_closed_in_either_position(self):
        bad = ('1E32', '1E-13', '1E999999999', '0E-999999999',
               '9' * 97, '0.' + '0' * 13, 10 ** 32, 10 ** 5000,
               Decimal('1E32'), Decimal('1E-13'), [], {}, b'1', object())
        for value in bad:
            # Do not echo arbitrary supplied values in diagnostic labels.
            self.assertIsNone(first_day_cash_gap(value, '0'))
            self.assertIsNone(first_day_cash_gap('1', value))
            self.assertEqual(classify_assistance(OK, value, 0, True, True),
                             {'admission': 'ELIGIBLE_TO_CONSIDER_VOLUNTARY_APPLICATION',
                              'finance': 'UNKNOWN_COSTS_NO_LOAN', 'gap': None})
    def test_supported_numeric_api_and_exact_output_preserved(self):
        for fare, cash in ((100, 1), (123.45, 1.0), (Decimal('123.45'), Decimal('1.00'))):
            result = first_day_cash_gap(fare, cash)
            self.assertIsInstance(result, Decimal)
            self.assertEqual(result, Decimal('99') if fare == 100 else Decimal('122.45'))
        self.assertEqual(classify_assistance(OK, '123.45', '1.00', True, True)['gap'], '122.45')
    def test_mutable_default_context_does_not_change_calculation(self):
        saved = DefaultContext.copy()
        try:
            DefaultContext.prec = 1
            DefaultContext.rounding = ROUND_UP
            DefaultContext.Emin, DefaultContext.Emax = -1, 1
            DefaultContext.clamp = 1
            DefaultContext.traps[Inexact] = DefaultContext.traps[Rounded] = True
            self.assertEqual(first_day_cash_gap('123.45', '1.00'), Decimal('122.45'))
            biggest = '9' * 32 + '.' + '9' * 12
            self.assertEqual(str(first_day_cash_gap(biggest, '0.000000000001')),
                             '9' * 32 + '.' + '9' * 11 + '8')
        finally:
            for attr in ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp', 'flags', 'traps'):
                setattr(DefaultContext, attr, getattr(saved, attr))
    def test_repaired_arithmetic_does_not_bypass_consent_or_authorize_finance(self):
        args = dict(OK.__dict__)
        args['consent'] = False
        self.assertEqual(classify_assistance(Eligibility(**args), '123.45', '1.00', True, True),
                         {'admission': 'NO_CONTACT_NO_APPLICATION',
                          'finance': 'NO_LOAN_NO_GUARANTEE', 'gap': None})
        self.assertEqual(classify_assistance(OK, '123.45', '1.00', True, True)['finance'],
                         'VERIFY_EMPLOYER_PREPAY_OR_DIRECT_TICKET_BEFORE_ANY_SPONSORSHIP')
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
