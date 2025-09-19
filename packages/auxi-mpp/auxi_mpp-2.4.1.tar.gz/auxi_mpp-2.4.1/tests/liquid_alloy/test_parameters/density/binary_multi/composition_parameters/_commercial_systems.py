# from ...test_parameters._dummy_bff import dummy_bff


# commercial systems -- positive tests
commercial_alloys = [
    (1800, {"stainless_steel_304": 1.0}),
    (1600, {"grey_cast_iron": 1.0}),
    (1500, {"ductile_iron": 1.0}),
    (1800, {"stainless_steel_316": 1.0}),
    # 8
]

# compilation of commercial positive test parameters
composition_limits_commercial = commercial_alloys

# commercial systems -- error tests
commercial_alloys_err = [
    (1800, {"stainless_steel_304": -1.0}),
    (1600, {"grey_cast_iron": 1.01}),
    (1500, {"ductile_iron": 0.0}),
    (1800, {"stainless_steel_316": -0.01}),
    # 8
]

# compilation of commercial positive test parameters
composition_limits_commercial_err = commercial_alloys_err
