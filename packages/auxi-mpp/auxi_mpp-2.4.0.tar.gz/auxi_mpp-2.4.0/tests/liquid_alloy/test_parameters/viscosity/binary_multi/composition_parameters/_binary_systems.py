# binary systems -- positive tests
fe_c = [
    (1700.0, {"Fe": 1.0, "C": 0.0}),
    (1700.0, {"Fe": 0.0, "C": 1.0}),
    (1700.0, {"Fe": 0.5, "C": 0.5}),
]


# compilation of binary positive test parameters
composition_limits_binary: list[tuple[float, dict[str, float]]] = fe_c

# binary systems -- error tests
fe_c_err = [(1700.0, {"Fe": 1.01, "C": -0.01}), (1700.0, {"Fe": -0.01, "C": 1.01})]
ni_c_err = [
    (1700.0, {"Ni": 0.8, "C": 0.2}),
]

# compilation of binary error test parameters
composition_limits_binary_err = fe_c_err + ni_c_err
