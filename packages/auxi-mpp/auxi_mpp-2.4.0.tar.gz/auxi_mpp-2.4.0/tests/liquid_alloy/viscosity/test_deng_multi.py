"""Test DengMulti model."""

import pytest

from auxi.mpp.liquid_alloy.μ._deng_multi import DengMulti

from ..test_parameters.viscosity.binary_multi._multi_testing_inputs import (
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_deng_binary(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = DengMulti()
    result = model.calculate(T=temperature, x=composition)

    assert abs(result) > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", multi_error_test_inputs)
def test_deng_binary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = DengMulti()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_viscosity_binary_activity():
    """Test if invalid inputs will fail."""
    model = DengMulti()
    with pytest.raises(ValueError):
        model.calculate(T=1700, x={"Fe": 0.831, "C": 0.162, "Si": 0.007}, a={"Fe_sat": {"Fe": 1.0}})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = DengMulti()

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Liquid Alloy"
    assert model.references == ["deng2018"]

    assert sorted(model.component_scope) == ["C", "Fe", "Mn", "P", "S", "Si", "Ti"]
    assert model.parameters["Fe"]["const"] == 34.42973
    assert model.T_min == 1463.0
    assert model.parameters["C"]["component_coefficient"] == -0.00349


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = DengMulti()
    result1 = model.calculate(T=1700, x={"Fe": 0.831, "C": 0.162, "Si": 0.007})
    result2 = model(T=1700, x={"Fe": 0.831, "C": 0.162, "Si": 0.007})

    assert abs(result1 - result2) < 1e-9
