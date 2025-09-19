"""Test PolynomialBinary model."""

import pytest

from auxi.mpp.liquid_alloy.σ._polynomial_binary import PolynomialBinary

from ..test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)


# tests that should pass
# degree = 1
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_polynomial_binary_degree1(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = PolynomialBinary(degree=1)
    result = model.calculate(T=temperature, x=composition)

    assert abs(result) > 0


# degree = 2
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_polynomial_binary_degree2(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = PolynomialBinary(degree=2)
    result = model.calculate(T=temperature, x=composition)

    assert abs(result) > 0


# degree = 3
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_polynomial_binary_degree3(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = PolynomialBinary(degree=3)
    result = model.calculate(T=temperature, x=composition)

    assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", binary_error_test_inputs)
def test_polynomial_binary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = PolynomialBinary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = PolynomialBinary()

    assert model.property == "Electrical Conductivity"
    assert model.symbol == "σ"
    assert model.display_symbol == "\\sigma"
    assert model.units == "\\siemens\\per\\meter"
    assert model.material == "Liquid Alloy"
    assert model.references == [
        "ono1976",
        "hixson1990",
        "zytveld1980",
        "baum1971",
        "ono1972",
        "kita1984",
        "chikova2021",
        "seydel1977",
        "kita1978",
        "cagran2007",
        "sasaki1995",
    ]

    assert sorted(model.component_scope) == ["C", "Fe", "Mn", "Ni", "Si"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = PolynomialBinary()
    result1 = model.calculate(T=1700, x={"Fe": 0.5, "C": 0.5})
    result2 = model(T=1700, x={"Fe": 0.5, "C": 0.5})

    assert abs(result1 - result2) < 1e-9
