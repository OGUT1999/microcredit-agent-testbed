import math
import unittest
from refund_guard import validate_refund

class RefundGuardTests(unittest.TestCase):
    def test_exact_fare(self):
        self.assertEqual(validate_refund(400,400,800),800)
    def test_partial_and_zero(self):
        self.assertEqual(validate_refund(400,400,350),350)
        self.assertEqual(validate_refund(400,400,0),0)
    def test_overrefund_rejected(self):
        with self.assertRaises(ValueError):
            validate_refund(400,400,1400)
    def test_no_travel_must_not_create_income(self):
        with self.assertRaises(ValueError):
            validate_refund(0,0,1)
    def test_invalid_values_rejected(self):
        for x in (float("nan"),float("inf"),-1):
            with self.assertRaises(ValueError):
                validate_refund(10,20,x)

if __name__ == "__main__":
    unittest.main()
