from collections.abc import Callable

from ..binary_multi._multi_testing_inputs import (
    activity_error_test_inputs,
    activity_tests,
    multi_error_test_inputs,
    multi_testing_inputs,
)
from ._dummy_esf import dummy_esf


# positive test temperature and composition tests
multi_testing_inputs_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in multi_testing_inputs:
    tup_esf = (*tup, dummy_esf)
    multi_testing_inputs_esf.append(tup_esf)

# reuse original name
multi_testing_inputs = multi_testing_inputs_esf


# tests that should fail
multi_error_test_inputs_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in multi_error_test_inputs:
    tup_esf = (*tup, dummy_esf)
    multi_error_test_inputs_esf.append(tup_esf)

# reuse original name
multi_error_test_inputs = multi_error_test_inputs_esf

# test activity inputs
activity_tests_esf: list[
    tuple[
        float,
        dict[str, float],
        dict[str, dict[str, float]],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in activity_tests:
    tup_esf = (*tup, dummy_esf)
    activity_tests_esf.append(tup_esf)

# reuse original name
activity_tests = activity_tests_esf

# activity error tests
activity_error_test_inputs_esf: list[
    tuple[
        float,
        dict[str, float],
        dict[str, dict[str, float]],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in activity_error_test_inputs:
    tup_esf = (*tup, dummy_esf)
    activity_error_test_inputs_esf.append(tup_esf)

# reuse original name
activity_error_test_inputs = activity_error_test_inputs_esf

# temperature limits for binary vs multi
temperature_limits_binary_vs_multi = [(1000, {"SiO2": 0.5, "Al2O3": 0.5}), (2500, {"SiO2": 0.5, "CaO": 0.5})]
