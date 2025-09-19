# from ...test_parameters._dummy_bff import dummy_bff


# multi systems -- positive tests
fe_c_si = [
    (1700, {"Fe": 0.831, "C": 0.162, "Si": 0.007}),
]
fe_c_mn = [
    (1700, {"Fe": 0.833, "C": 0.162, "Mn": 0.005}),
]
fe_c_p = [
    (1700, {"Fe": 0.833, "C": 0.162, "P": 0.005}),
]
fe_c_s = [
    (1700, {"Fe": 0.837, "C": 0.162, "S": 0.001}),
]
fe_c_ti = [
    (1700, {"Fe": 0.836, "C": 0.162, "Ti": 0.002}),
]

# compilation of multi positive test parameters
composition_limits_multi = fe_c_si + fe_c_mn + fe_c_p + fe_c_s + fe_c_ti

# multi systems -- error tests
fe_c_si_err = [
    (1700, {"Fe": 1.01, "C": -0.01, "Si": 0.0}),
    (1700, {"Fe": 0.5, "C": 0.5, "Si": 0.1}),
]
fe_c_mn_err = [
    (1700, {"Fe": 1.01, "C": -0.1, "Mn": 0.0}),
    (1700, {"Fe": 0.5, "C": 0.5, "Mn": 0.1}),
]
fe_c_p_err = [
    (1700, {"Fe": 1.01, "C": -0.1, "P": 0.0}),
    (1700, {"Fe": 0.5, "C": 0.5, "P": 0.1}),
]
fe_c_s_err = [
    (1700, {"Fe": 1.01, "C": -0.1, "S": 0.0}),
    (1700, {"Fe": 0.5, "C": 0.5, "S": 0.1}),
]
fe_c_ti_err = [(1700, {"Fe": 1.01, "C": -0.1, "Ti": 0.0}), (1700, {"Fe": 0.5, "C": 0.5, "Ti": 0.1})]

# compilation of multi positive test parameters
composition_limits_multi_err = fe_c_si_err + fe_c_mn_err + fe_c_p_err + fe_c_s_err + fe_c_ti_err
