from .composition_parameters._binary_systems import composition_limits_binary, composition_limits_binary_err


# positive test temperature and composition tests
temperature_limits = [(1000, {"Fe": 0.85, "C": 0.15}), (2500, {"Fe": 0.85, "C": 0.15})]

# compilation of binary tests
binary_testing_inputs = temperature_limits + composition_limits_binary

# error tests
contain_fe_err = [
    (1700, {"Si": 0.5, "C": 0.5}),
    (1700, {"Ni": 0.5, "Si": 0.5}),
    (1700, {"C": 0.5, "Ni": 0.5}),
    (1700, {"C": 0.5, "Mn": 0.5}),
]
temperature_limits_err = [(2501, {"Fe": 0.85, "C": 0.15}), (999, {"Fe": 0.85, "Si": 0.15})]
add_to_unity_err = [(1700, {"Fe": 0.4, "C": 0.4}), (1700, {"Fe": 0.6, "C": 0.6})]
component_number_err = [(1700, {"Fe": 1.0}), (1700, {"Fe": 0.4, "Si": 0.4, "C": 0.15})]
invalid_comp_err = [(1700, {"Fe": 0.5, "Na2O": 0.5}), (1700, {"Ni": 0.5, "Na2O": 0.5})]

# compilation of binary error tests
binary_error_test_inputs = (
    contain_fe_err
    + temperature_limits_err
    + composition_limits_binary_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)
