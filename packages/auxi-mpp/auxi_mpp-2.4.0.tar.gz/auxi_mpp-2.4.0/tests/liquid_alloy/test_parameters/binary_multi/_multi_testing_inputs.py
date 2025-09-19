from .composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (1000, {"Fe": 0.4, "C": 0.4, "Si": 0.2}),
    (2500, {"Fe": 0.5, "C": 0.25, "Si": 0.25}),
]

# compilation of multi tests
multi_testing_inputs = temperature_limits + composition_limits_multi

contain_fe_err = [(1700, {"Si": 0.2, "C": 0.8})]
temperature_limits_err = [
    (2501, {"Fe": 0.5, "Si": 0.25, "C": 0.25}),
    (999, {"Fe": 0.6, "Si": 0.2, "C": 0.2}),
]
add_to_unity_err = [
    (1700, {"Fe": 0.5, "C": 0.2, "Si": 0.2}),
    (1700, {"Fe": 0.7, "C": 0.2, "Si": 0.2}),
]
component_number_err = [(1700, {"Fe": 0.6, "C": 0.4}), (1700, {"Fe": 1.0})]
invalid_comp_err = [(1700, {"Fe": 0.4, "Mn": 0.4, "C": 0.2})]

# compilation of multi error tests
multi_error_test_inputs = (
    contain_fe_err
    + temperature_limits_err
    + composition_limits_multi_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)
