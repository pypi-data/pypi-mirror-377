"""Test WiedemannFranzMulti model."""

import pytest

from auxi.mpp.liquid_alloy.κ._wiedemann_franz_multi import WiedemannFranzMulti

from ..test_parameters.binary_multi._multi_testing_inputs import (
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
# degree = 2
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_wiedemann_franz_multi_degree2(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = WiedemannFranzMulti(degree=2)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# degree = 3
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_wiedemann_franz_multi_degree3(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = WiedemannFranzMulti(degree=3)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# degree = 4
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_ec_wiedemann_franz_multi_degree4(
    temperature: float,
    composition: dict[str, float],
):
    """Test temperature and composition limits."""
    model = WiedemannFranzMulti(degree=4)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", multi_error_test_inputs)
def test_ec_wiedemann_franz_multi_errors(
    temperature: float,
    composition: dict[str, float],
):
    """Test if invalid inputs will fail."""
    model = WiedemannFranzMulti(degree=2)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = WiedemannFranzMulti()

    assert model.property == "Thermal Conductivity"
    assert model.symbol == "κ"
    assert model.display_symbol == "\\kappa"
    assert model.units == "\\watt\\per\\meter\\per\\kelvin"
    assert model.material == "Liquid Alloy"
    assert model.references == ["ono1976", "sasaki1995", "hixson1990", "zytveld1980"]

    assert sorted(model.component_scope) == ["C", "Fe", "Si"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = WiedemannFranzMulti(degree=2)
    result1 = model.calculate(T=1700, x={"Fe": 0.5, "C": 0.25, "Si": 0.25})
    result2 = model(T=1700, x={"Fe": 0.5, "C": 0.25, "Si": 0.25})

    assert abs(result1 - result2) < 1e-9
