"""Test WiedemannFranzUnary model."""

import pytest

from auxi.mpp.liquid_alloy.κ._wiedemann_franz_unary import WiedemannFranzUnary

from ..test_parameters._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


# tests that should pass
# degree = 1
@pytest.mark.parametrize(
    "temperature, composition",
    unary_testing_inputs,
)
def test_ec_wiedemann_franz_unary_degree1(temperature: float, composition: dict[str, float]):
    """Test temperature limits."""
    model = WiedemannFranzUnary(degree=1)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# degree = 2
@pytest.mark.parametrize(
    "temperature, composition",
    unary_testing_inputs,
)
def test_ec_wiedemann_franz_unary_degree2(temperature: float, composition: dict[str, float]):
    """Test temperature limits."""
    model = WiedemannFranzUnary(degree=2)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", unary_error_test_inputs)
def test_ec_wiedemann_franz_unary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = WiedemannFranzUnary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = WiedemannFranzUnary()

    assert model.property == "Thermal Conductivity"
    assert model.symbol == "κ"
    assert model.display_symbol == "\\kappa"
    assert model.units == "\\watt\\per\\meter\\per\\kelvin"
    assert model.material == "Liquid Alloy"
    assert model.references == [
        "hixson1990",
        "zytveld1980",
        "ono1976",
        "sasaki1995",
        "seydel1977",
        "kita1978",
        "cagran2007",
    ]

    assert sorted(model.component_scope) == ["Fe", "Ni", "Si"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = WiedemannFranzUnary()
    result1 = model.calculate(T=1900, x={"Fe": 1.0})
    result2 = model(T=1900, x={"Fe": 1.0})

    assert abs(result1 - result2) < 1e-9
