from collections.abc import Callable

from ..binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)
from ._dummy_esf import dummy_esf


# normal tests
binary_testing_inputs_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in binary_testing_inputs:
    tup_esf = (*tup, dummy_esf)
    binary_testing_inputs_esf.append(tup_esf)

# reuse original name
binary_testing_inputs = binary_testing_inputs_esf

# error tests
binary_error_test_inputs_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in binary_error_test_inputs:
    tup_esf = (*tup, dummy_esf)
    binary_error_test_inputs_esf.append(tup_esf)

# reuse original name
binary_error_test_inputs = binary_error_test_inputs_esf
