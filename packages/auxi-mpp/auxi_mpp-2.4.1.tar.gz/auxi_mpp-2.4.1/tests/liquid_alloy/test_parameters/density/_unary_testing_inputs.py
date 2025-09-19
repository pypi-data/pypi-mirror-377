unary_testing_inputs = [
    # temperature limits
    (1000, {"Fe": 1.0}),
    (1900, {"Fe": 1.0}),
    (2500, {"Fe": 1.0}),
]

unary_error_test_inputs = [
    # inside T boundaries?
    (8001, {"Fe": 1.0}),
    (199, {"Fe": 1.0}),
    # inside x boundaries?
    (1900, {"Fe": 0.9}),
    (1900, {"Fe": 1.1}),
    # invalid compound provided
    (1900, {"Mn": 1.0}),
    # too many compounds provided
    (1900, {"Fe": 0.5, "C": 0.5}),
]
