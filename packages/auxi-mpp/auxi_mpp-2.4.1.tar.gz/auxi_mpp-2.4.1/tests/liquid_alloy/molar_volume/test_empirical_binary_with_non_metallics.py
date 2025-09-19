"""Test EmpiricalBinaryWithNonMetallics model."""

import pytest

from auxi.mpp.liquid_alloy.Vm._empirical_binary_with_non_metallics import EmpiricalBinaryWithNonMetallics

from ..test_parameters.density.binary_multi._binary_with_non_metallics_testing_inputs import (
    binary_with_non_metallics_error_test_inputs,
    binary_with_non_metallics_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", binary_with_non_metallics_testing_inputs)
def test_empirical_binary_with_non_metallics(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = EmpiricalBinaryWithNonMetallics()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", binary_with_non_metallics_error_test_inputs)
def test_empirical_binary_with_non_metallics_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = EmpiricalBinaryWithNonMetallics()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EmpiricalBinaryWithNonMetallics()

    assert model.property == "Molar Volume"
    assert model.symbol == "Vm"
    assert model.display_symbol == "\\bar{V}"
    assert model.units == "\\cubic\\meter\\per\\mol"
    assert model.material == "Liquid Alloy"
    assert model.references == ["tesfaye2010", "miettinen1997", "nagamori1969", "jimbocramb1993"]

    assert set(model.component_scope) == {"Fe", "Ni", "Cu", "C", "S"}


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EmpiricalBinaryWithNonMetallics()
    result1 = model.calculate(T=1600, x={"Fe": 0.97, "C": 0.03})
    result2 = model(T=1600, x={"Fe": 0.97, "C": 0.03})

    assert abs(result1 - result2) < 1e-9
