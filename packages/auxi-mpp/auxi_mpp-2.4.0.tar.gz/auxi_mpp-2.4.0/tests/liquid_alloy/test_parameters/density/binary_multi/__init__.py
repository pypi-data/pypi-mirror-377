"""Parameters for testing for testing."""

from ._binary_testing_inputs import binary_error_test_inputs, binary_testing_inputs
from ._binary_with_non_metallics_testing_inputs import (
    binary_with_non_metallics_error_test_inputs,
    binary_with_non_metallics_testing_inputs,
)
from ._commercial_testing_inputs import commercial_error_test_inputs, commercial_testing_inputs
from ._multi_testing_inputs import multi_error_test_inputs, multi_testing_inputs


__all__ = [
    "binary_error_test_inputs",
    "binary_testing_inputs",
    "binary_with_non_metallics_error_test_inputs",
    "binary_with_non_metallics_testing_inputs",
    "commercial_error_test_inputs",
    "commercial_testing_inputs",
    "multi_error_test_inputs",
    "multi_testing_inputs",
]
