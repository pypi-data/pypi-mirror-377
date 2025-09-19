"""Test EmpiricalUnary model."""

import pytest

from auxi.mpp.liquid_alloy.ρ._empirical_unary import EmpiricalUnary

from ..test_parameters.density._unary_testing_inputs import unary_error_test_inputs, unary_testing_inputs


# from ..test_parameters.


@pytest.mark.parametrize(
    "temperature, composition",
    unary_testing_inputs,
)
def test_empirical_unary(temperature: float, composition: dict[str, float]):
    """Test temperature limits."""
    model = EmpiricalUnary()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", unary_error_test_inputs)
def test_empirical_unary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = EmpiricalUnary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_empirical_unary_activity():
    """Test if invalid inputs will fail."""
    model = EmpiricalUnary()
    with pytest.raises(ValueError):
        model.calculate(T=1700, x={"Fe": 1.0}, a={"Fe_sat": {"Fe": 1.0}})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EmpiricalUnary()

    assert model.property == "Density"
    assert model.symbol == "ρ"
    assert model.display_symbol == "\\rho"
    assert model.units == "\\kilo\\gram\\per\\cubic\\meter"
    assert model.material == "Liquid Alloy"
    assert model.references == ["assael2006", "assael2010", "assael2012", "ntonti2024"]

    # assert model.molar_mass["SiO2"] == 60.08
    assert sorted(model.component_scope) == [
        "Ag",
        "Al",
        "Bi",
        "Cd",
        "Co",
        "Cr",
        "Cu",
        "Fe",
        "Ga",
        "Hf",
        "In",
        "Mo",
        "Nb",
        "Ni",
        "Pb",
        "Sb",
        "Si",
        "Sn",
        "Ta",
        "Ti",
        "Tl",
        "V",
        "W",
        "Zn",
        "Zr",
    ]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EmpiricalUnary()
    result1 = model.calculate(T=1900, x={"Fe": 1.0})
    result2 = model(T=1900, x={"Fe": 1.0})

    assert abs(result1 - result2) < 1e-9
