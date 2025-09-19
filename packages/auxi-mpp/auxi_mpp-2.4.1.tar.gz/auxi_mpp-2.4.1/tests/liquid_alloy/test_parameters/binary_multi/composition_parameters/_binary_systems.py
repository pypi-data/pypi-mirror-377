# binary systems -- positive tests
fe_c = [
    (1700.0, {"Fe": 1.0, "C": 0.0}),
    (1700.0, {"Fe": 0.0, "C": 1.0}),
    (1700.0, {"Fe": 0.5, "C": 0.5}),
]
fe_si = [
    (1700.0, {"Fe": 1.0, "Si": 0.0}),
    (1700.0, {"Fe": 0.0, "Si": 1.0}),
    (1700.0, {"Fe": 0.5, "Si": 0.5}),
]
fe_mn = [
    (1700.0, {"Fe": 1.0, "Mn": 0.0}),
    (1700.0, {"Fe": 0.0, "Mn": 1.0}),
    (1700.0, {"Fe": 0.5, "Mn": 0.5}),  # 8
]
fe_ni = [
    (1700.0, {"Fe": 1.0, "Ni": 0.0}),
    (1700.0, {"Fe": 0.0, "Ni": 1.0}),
    (1700.0, {"Fe": 0.5, "Ni": 0.5}),
]

# compilation of binary positive test parameters
composition_limits_binary: list[tuple[float, dict[str, float]]] = fe_c + fe_si + fe_mn + fe_ni

# binary systems -- error tests
fe_c_err = [(1700.0, {"Fe": 1.01, "C": -0.01}), (1700.0, {"Fe": -0.01, "C": 1.01})]
fe_si_err = [(1700.0, {"Fe": 1.01, "Si": -0.01}), (1700.0, {"Fe": -0.01, "Si": 1.01})]
fe_mn_err = [(1700.0, {"Fe": 1.01, "Mn": -0.01}), (1700.0, {"Fe": -0.01, "Mn": 1.01})]
fe_ni_err = [(1700.0, {"Fe": 1.01, "Ni": -0.01}), (1700.0, {"Fe": -0.01, "Ni": 1.01})]

# compilation of binary error test parameters
composition_limits_binary_err = fe_c_err + fe_si_err + fe_mn_err + fe_ni_err
