"""Test PolynomialMulti model."""

import pytest

from auxi.mpp.liquid_alloy.σ._polynomial_multi import PolynomialMulti

from ..test_parameters.binary_multi._multi_testing_inputs import (
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
# degree = 2
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_polynomial_multi_degree2(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = PolynomialMulti(degree=2)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# degree = 3
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_polynomial_multi_degree3(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = PolynomialMulti(degree=3)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# degree = 4
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_polynomial_multi_degree4(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = PolynomialMulti(degree=4)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", multi_error_test_inputs)
def test_ec_polynomial_multi_errors(
    temperature: float,
    composition: dict[str, float],
):
    """Test if invalid inputs will fail."""
    model = PolynomialMulti(degree=2)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = PolynomialMulti()

    assert model.property == "Electrical Conductivity"
    assert model.symbol == "σ"
    assert model.display_symbol == "\\sigma"
    assert model.units == "\\siemens\\per\\meter"
    assert model.material == "Liquid Alloy"
    assert model.references == ["ono1976", "sasaki1995", "hixson1990", "zytveld1980"]

    assert sorted(model.component_scope) == ["C", "Fe", "Si"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = PolynomialMulti(degree=2)
    result1 = model.calculate(T=1700, x={"Fe": 0.5, "C": 0.25, "Si": 0.25})
    result2 = model(T=1700, x={"Fe": 0.5, "C": 0.25, "Si": 0.25})

    assert abs(result1 - result2) < 1e-9
