# binary systems -- positive tests
fe_cu = [
    (1900.0, {"Fe": 1.0, "Cu": 0.0}),
    (1400.0, {"Fe": 0.0, "Cu": 1.0}),
    (1850.0, {"Fe": 0.5, "Cu": 0.5}),
]
fe_al = [
    (1700.0, {"Fe": 0.3, "Al": 0.7}),
    (1700.0, {"Fe": 0.2, "Al": 0.8}),
    (1700.0, {"Fe": 0.25, "Al": 0.75}),
]
fe_cr = [
    (1850.0, {"Fe": 1.0, "Cr": 0.0}),
    (1750.0, {"Fe": 0.8, "Cr": 0.2}),
    (1750.0, {"Fe": 0.5, "Cr": 0.5}),  # 8
]
fe_ni = [
    (1850.0, {"Fe": 1.0, "Ni": 0.0}),
    (1750.0, {"Fe": 0.0, "Ni": 1.0}),
    (1750.0, {"Fe": 0.5, "Ni": 0.5}),
]

# compilation of binary positive test parameters
composition_limits_binary: list[tuple[float, dict[str, float]]] = fe_cu + fe_al + fe_cr + fe_ni

# binary systems -- error tests
fe_cu_err = [
    (1700.0, {"Fe": 1.01, "Cu": -0.01}),
    (1700.0, {"Fe": -0.01, "Cu": 1.01}),
]
fe_al_err = [(1700.0, {"Fe": 1.01, "Al": -0.01}), (1700.0, {"Fe": -0.01, "Al": 1.01})]
fe_cr_err = [(1700.0, {"Fe": 1.01, "Cr": -0.01}), (1700.0, {"Fe": -0.01, "Cr": 1.01})]
fe_ni_err = [(1700.0, {"Fe": 1.01, "Ni": -0.01}), (1700.0, {"Fe": -0.01, "Ni": 1.01})]
al_ni_err = [
    (1700.0, {"Al": 1.01, "Ni": -0.01}),
    (1700.0, {"Al": -0.01, "Ni": 1.01}),
    ((1700.0, {"Al": 0.05, "Ni": 0.95})),
]  # 4
# Cu0.95Si0.05:

# compilation of binary error test parameters
composition_limits_binary_err = fe_cu_err + fe_al_err + fe_cr_err + fe_ni_err
