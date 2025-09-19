# binary systems -- positive tests
fe_c = [
    (1600.0, {"Fe": 0.97, "C": 0.03}),
]
fe_s = [
    (1473.15, {"Fe": 0.55, "S": 0.45}),
]
cu_s = [
    (1473.15, {"Cu": 0.67, "S": 0.33}),
]
ni_s = [
    (1300.0, {"Ni": 0.70, "S": 0.30}),
]

# compilation of binary positive test parameters
composition_limits_binary_with_non_metallics: list[tuple[float, dict[str, float]]] = fe_c + fe_s + cu_s + ni_s

# binary systems -- error tests
fe_c_err = [(1500.0, {"Fe": 1.01, "C": -0.01}), (1500.0, {"Fe": -0.01, "C": 1.01}), (1523.15, {"Fe": 0.5, "C": 0.5})]
fe_s_err = [(1473.15, {"Fe": 1.01, "S": -0.01}), (1473.15, {"Fe": -0.01, "S": 1.01}), (1473.15, {"Fe": 0.3, "S": 0.7})]
cu_s_err = [
    (1473.15, {"Cu": 1.01, "S": -0.01}),
    (1473.15, {"Cu": -0.01, "S": 1.01}),
    (1473.15, {"Cu": 0.8, "S": 0.20}),
]
ni_s_err = [(1300.0, {"Ni": 1.01, "S": -0.01}), (1300.0, {"Ni": -0.01, "S": 1.01}), (1300.0, {"Ni": 0.95, "S": 0.05})]

# compilation of binary error test parameters
composition_limits_binary_with_non_metallics_err = fe_c_err + fe_s_err + cu_s_err + ni_s_err
