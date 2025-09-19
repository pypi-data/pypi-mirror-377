# from ...test_parameters._dummy_esf import dummy_esf


# multi systems -- positive tests
fe_c_si = [
    (1700, {"Fe": 1.0, "C": 0.0, "Si": 0.0}),
    (1700, {"Fe": 0.0, "C": 1.0, "Si": 0.0}),
    (1700, {"Fe": 0.0, "C": 0.0, "Si": 1.0}),
    (1700, {"Fe": 0.5, "C": 0.5, "Si": 0.0}),
    (1700, {"Fe": 0.0, "C": 0.5, "Si": 0.5}),
    (1700, {"Fe": 0.5, "C": 0.0, "Si": 0.5}),
    (1700, {"Fe": 0.34, "C": 0.33, "Si": 0.33}),  # 8
]

# compilation of multi positive test parameters
composition_limits_multi = fe_c_si

# multi systems -- error tests
fe_c_si_err = [
    (1700, {"Fe": 1.01, "C": -0.01, "Si": 0.0}),
    (1700, {"Fe": 0.0, "C": 1.01, "Si": -0.01}),
    (1700, {"Fe": -0.01, "C": 0.0, "Si": 1.01}),
    (1700, {"Fe": 1.01, "C": 0.0, "Si": -0.01}),
    (1700, {"Fe": -0.01, "C": 1.01, "Si": 0.0}),
    (1700, {"Fe": 0.0, "C": -0.01, "Si": 1.01}),
]

# compilation of multi positive test parameters
composition_limits_multi_err = fe_c_si_err
