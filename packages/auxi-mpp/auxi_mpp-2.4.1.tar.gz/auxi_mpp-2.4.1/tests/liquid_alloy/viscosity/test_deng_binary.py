"""Test DengBinary model."""

import pytest

from auxi.mpp.liquid_alloy.μ._deng_binary import DengBinary

from ..test_parameters.viscosity.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_deng_binary(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = DengBinary()
    result = model.calculate(T=temperature, x=composition)

    assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", binary_error_test_inputs)
def test_deng_binary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = DengBinary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_viscosity_binary_activity():
    """Test if invalid inputs will fail."""
    model = DengBinary()
    with pytest.raises(ValueError):
        model.calculate(T=1700, x={"Fe": 0.8, "C": 0.2}, a={"Fe_sat": {"Fe": 1.0}})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = DengBinary()

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Liquid Alloy"
    assert model.references == ["deng2018"]

    assert sorted(model.component_scope) == ["C", "Fe"]
    assert model.parameters["Fe"]["const"] == 34.42973
    assert model.T_min == 1463.0
    assert model.parameters["C"]["component_coefficient"] == -0.00349


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = DengBinary()
    result1 = model.calculate(T=1700, x={"Fe": 0.8, "C": 0.2})
    result2 = model(T=1700, x={"Fe": 0.8, "C": 0.2})

    assert abs(result1 - result2) < 1e-9
