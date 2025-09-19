from collections.abc import Callable

from ...binary_multi.composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)
from .._dummy_esf import dummy_esf


# normal tests
composition_limits_multi_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in composition_limits_multi:
    tup_esf = (*tup, dummy_esf)
    composition_limits_multi_esf.append(tup_esf)

# reuse original name
composition_limits_multi = composition_limits_multi_esf


# tests that should fail
composition_limits_multi_err_esf: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in composition_limits_multi_err:
    tup_esf = (*tup, dummy_esf)
    composition_limits_multi_err_esf.append(tup_esf)

# reuse original name
composition_limits_multi_err = composition_limits_multi_err_esf
