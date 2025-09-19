from .composition_parameters._binary_with_non_metallics_systems import (
    composition_limits_binary_with_non_metallics,
    composition_limits_binary_with_non_metallics_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (1523.15, {"Fe": 0.97, "C": 0.03}),
    (1823.15, {"Fe": 0.97, "C": 0.03}),
    (1473.15, {"Fe": 0.55, "S": 0.45}),
    (1473.15, {"Fe": 0.55, "S": 0.45}),
    (1473.15, {"Cu": 0.67, "S": 0.33}),
]

# compilation of binary tests
binary_with_non_metallics_testing_inputs = temperature_limits + composition_limits_binary_with_non_metallics

# error tests

temperature_limits_err = [
    (2501, {"Fe": 0.97, "C": 0.03}),
    (1900, {"Fe": 0.97, "C": 0.03}),
    (999, {"Fe": 0.97, "C": 0.003}),
    (1800, {"Fe": 0.55, "S": 0.45}),
    (1800, {"Ni": 0.55, "S": 0.45}),
    (1573.15, {"Cu": 0.67, "S": 0.33}),
]
add_to_unity_err = [(1400, {"Fe": 0.4, "S": 0.4}), (1400, {"Fe": 0.6, "S": 0.6})]
component_number_err = [(1400, {"Fe": 1.0}), (1600, {"Fe": 0.4, "Al": 0.4, "Cu": 0.2})]
invalid_comp_err = [(1700, {"Fe": 0.5, "Na2O": 0.5})]

# compilation of binary error tests
binary_with_non_metallics_error_test_inputs = (
    temperature_limits_err
    + composition_limits_binary_with_non_metallics_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)
