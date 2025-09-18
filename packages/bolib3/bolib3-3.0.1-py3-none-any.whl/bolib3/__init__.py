__name__ = "BOLIB-3 (Bilevel Optimisation Library)"
__version__ = "3.0.1"
__author__ = "Samuel Ward"

# NumPy (note that if using autograd you need to import the autograd.numpy wrapper)
# import numpy as np
import autograd.numpy as np

# Import all the models that each correspond to a bilevel program
from bolib3.python import (
    adversarial_regression,
    bard511,
    bard721,
    bard722,
    bard851,
    bard871,
    basic_constrained,
    basic_unconstrained,
    brotcorne2001,
    dantzig_3_3,
    dempe_dutta_2_2,
    dempe_dutta_3_4,
    electricity_market_competitive,
    electricity_market_monopoly,
    linear_bilevel,
    lu_deb_sinha,
    outrata_1990_ex2,
    polynomial_bilevel,
    quadratic_bilevel,
    svm_linear,
    svm_ward2025,
    svr_bennett2006,
    text_based_adversarial
)

# This collection can be iterated over
collection = [
    adversarial_regression,
    bard511,
    bard721,
    bard722,
    bard851,
    bard871,
    basic_constrained,
    basic_unconstrained,
    brotcorne2001,
    dantzig_3_3,
    dempe_dutta_2_2,
    dempe_dutta_3_4,
    electricity_market_competitive,
    electricity_market_monopoly,
    linear_bilevel,
    lu_deb_sinha,
    outrata_1990_ex2,
    polynomial_bilevel,
    quadratic_bilevel,
    svm_linear,
    svm_ward2025,
    svr_bennett2006,
    text_based_adversarial
]

# Wildcard imports
__all__ = [
    'adversarial_regression',
    'bard511',
    'bard721',
    'bard722',
    'bard851',
    'bard871',
    'basic_constrained',
    'basic_unconstrained',
    'brotcorne2001',
    'collection',
    'dantzig_3_3',
    'dempe_dutta_2_2',
    'dempe_dutta_3_4',
    'electricity_market_competitive',
    'electricity_market_monopoly',
    'linear_bilevel',
    'lu_deb_sinha',
    'np',
    'outrata_1990_ex2',
    'polynomial_bilevel',
    'quadratic_bilevel',
    'svm_linear',
    'svm_ward2025',
    'svr_bennett2006',
    'text_based_adversarial'
]

# Print a welcome message
print(f"Welcome to {__name__} version {__version__}")
