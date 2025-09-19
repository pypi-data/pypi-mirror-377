"""Test MillsCommercial model."""

import pytest

from auxi.mpp.liquid_alloy.ρ._mills_commercial import MillsCommercial

from ..test_parameters.density.binary_multi._commercial_testing_inputs import (
    commercial_error_test_inputs,
    commercial_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", commercial_testing_inputs)
def test_density_commercial(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = MillsCommercial()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", commercial_error_test_inputs)
def test_density_commercial_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = MillsCommercial()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_density_commercial_activity():
    """Test if invalid inputs will fail."""
    model = MillsCommercial()
    with pytest.raises(ValueError):
        model.calculate(T=1800, x={"stainless_316": 1.0}, a={"Fe_sat": {"Fe": 1.0}})


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = MillsCommercial()

    assert model.property == "Density"
    assert model.symbol == "ρ"
    assert model.display_symbol == "\\rho"
    assert model.units == "\\kilo\\gram\\per\\cubic\\meter"
    assert model.material == "Liquid Alloy"
    assert model.references == ["mills2002"]

    assert set(model.compound_scope) == {"grey_cast_iron", "ductile_iron", "stainless_steel_304", "stainless_steel_316"}


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = MillsCommercial()
    result1 = model.calculate(T=1800, x={"stainless_steel_316": 1.0})
    result2 = model(T=1800, x={"stainless_steel_316": 1.0})

    assert abs(result1 - result2) < 1e-9
