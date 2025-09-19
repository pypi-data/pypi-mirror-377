# from ...test_parameters._dummy_bff import dummy_bff


# multi systems -- positive tests
fe_cu_ni = [
    (1750, {"Fe": 0.65, "Cu": 0.20, "Ni": 0.15}),
    (1700, {"Fe": 0.13, "Cu": 0.70, "Ni": 0.17}),
    (1700, {"Fe": 0.1, "Cu": 0.2, "Ni": 0.7}),
    (1700, {"Fe": 0.3, "Cu": 0.5, "Ni": 0.20}),
    (1700, {"Fe": 0.24, "Cu": 0.6, "Ni": 0.16}),
    (1700, {"Fe": 0.48, "Cu": 0.20, "Ni": 0.32}),
    (1700, {"Fe": 0.35, "Cu": 0.40, "Ni": 0.25}),  # 8
]

# compilation of multi positive test parameters
composition_limits_multi = fe_cu_ni

# multi systems -- error tests
fe_cu_ni_err = [
    (1700, {"Fe": 1.01, "Cu": -0.01, "Ni": 0.0}),
    (1700, {"Fe": 0.0, "Cu": 1.01, "Ni": -0.01}),
    (1700, {"Fe": -0.01, "Cu": 0.0, "Ni": 1.01}),
    (1700, {"Fe": 1.01, "Cu": 0.0, "Ni": -0.01}),
    (1700, {"Fe": -0.01, "Cu": 1.01, "Ni": 0.0}),
    (1700, {"Fe": 0.0, "Cu": -0.01, "Ni": 1.01}),
]

# compilation of multi positive test parameters
composition_limits_multi_err = fe_cu_ni_err
