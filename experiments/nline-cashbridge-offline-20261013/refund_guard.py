"""Conservative check for hypothetical reimbursement inputs. No external calls."""
from math import isfinite

def validate_refund(outbound, return_fare, reimbursement):
    vals = (outbound, return_fare, reimbursement)
    if not all(isfinite(v) and v >= 0 for v in vals):
        raise ValueError('All values must be finite and nonnegative')
    if reimbursement > outbound + return_fare:
        raise ValueError('Expected reimbursement exceeds entered fares')
    return reimbursement
