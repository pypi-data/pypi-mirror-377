from .composition_parameters._commercial_systems import (
    composition_limits_commercial,
    composition_limits_commercial_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (1463.15, {"grey_cast_iron": 1.0}),
    (1773.15, {"grey_cast_iron": 1.0}),
]

# compilation of_commercialtests
commercial_testing_inputs = temperature_limits + composition_limits_commercial

temperature_limits_err = [
    (2501, {"grey_cast_iron": 1.0}),
    (999, {"grey_cast_iron": 1.0}),
    (1200, {"grey_cast_iron": 1.0}),
]
add_to_unity_err = [
    (1700, {"grey_cast_iron": 1.1}),
    (1700, {"grey_cast_iron": 0.9}),
]
component_number_err = [(1700, {"grey_cast_iron": 0.6, "Cu": 0.4}), (1700, {"Fe": 1.0})]
invalid_comp_err = [(1700, {"inconel_718": 1.0})]

# compilation of_commercial error tests
commercial_error_test_inputs = (
    temperature_limits_err
    + composition_limits_commercial_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)
