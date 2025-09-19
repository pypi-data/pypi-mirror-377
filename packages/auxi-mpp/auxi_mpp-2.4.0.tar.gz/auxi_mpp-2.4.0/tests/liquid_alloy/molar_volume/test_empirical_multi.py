"""Test EmpiricalMulti model."""

import pytest

from auxi.mpp.liquid_alloy.Vm._empirical_multi import EmpiricalMulti

from ..test_parameters.density.binary_multi._multi_testing_inputs import (
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_empirical_multi(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = EmpiricalMulti()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", multi_error_test_inputs)
def test_empirical_multi_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = EmpiricalMulti()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EmpiricalMulti()

    assert model.property == "Molar Volume"
    assert model.symbol == "Vm"
    assert model.display_symbol == "\\bar{V}"
    assert model.units == "\\cubic\\meter\\per\\mol"
    assert model.material == "Liquid Alloy"
    assert model.references == ["brillo2006, brillo2016, kobatake2013"]

    assert set(model.compound_scope) == {
        "Ag0.10Al0.0Cu0.90",
        "Ag0.10Al0.20Cu0.70",
        "Ag0.10Al0.40Cu0.50",
        "Ag0.10Al0.50Cu0.40",
        "Ag0.10Al0.60Cu0.30",
        "Ag0.10Al0.80Cu0.10",
        "Ag0.10Al0.90Cu0.0",
        "Al0.0Cu0.50Si0.50",
        "Al0.30Cu0.40Si0.30",
        "Al0.34Cu0.33Si0.33",
        "Al0.40Cu0.20Si0.40",
        "Al0.60Cu0.20Si0.20",
        "Al0.80Cu0.10Si0.10",
        "Al0.90Cu0.05Si0.05",
        "Al1.0Cu0.00Si0.00",
        "Co0.05Cu0.90Fe0.05",
        "Co0.0Cu0.0Ni1.0",
        "Co0.0Cu0.80Ni0.20",
        "Co0.0Cu1.0Fe0.0",
        "Co0.10Cu0.10Ni0.80",
        "Co0.10Cu0.70Ni0.20",
        "Co0.10Cu0.80Fe0.10",
        "Co0.15Cu0.15Ni0.70",
        "Co0.15Cu0.70Fe0.15",
        "Co0.20Cu0.20Fe0.60",
        "Co0.20Cu0.20Ni0.60",
        "Co0.20Cu0.40Fe0.40",
        "Co0.20Cu0.60Fe0.20",
        "Co0.30Cu0.30Ni0.40",
        "Co0.30Cu0.40Fe0.30",
        "Co0.30Cu0.50Ni0.20",
        "Co0.35Cu0.35Ni0.30",
        "Co0.40Cu0.20Fe0.40",
        "Co0.40Cu0.40Ni0.20",
        "Co0.50Cu0.0Fe0.50",
        "Co0.50Cu0.30Ni0.20",
        "Co0.50Cu0.50Ni0.0",
        "Co0.60Cu0.20Fe0.20",
        "Co0.70Cu0.10Ni0.20",
        "Co0.80Cu0.0Ni0.20",
        "Cr0.10Fe0.0Ni0.90",
        "Cr0.10Fe0.18Ni0.72",
        "Cr0.10Fe0.36Ni0.54",
        "Cr0.10Fe0.54Ni0.36",
        "Cr0.10Fe0.63Ni0.27",
        "Cr0.10Fe0.72Ni0.18",
        "Cr0.10Fe0.90Ni0.0",
        "Cr0.20Fe0.0Ni0.80",
        "Cr0.20Fe0.16Ni0.64",
        "Cr0.20Fe0.32Ni0.48",
        "Cr0.20Fe0.48Ni0.32",
        "Cr0.20Fe0.56Ni0.24",
        "Cr0.20Fe0.64Ni0.16",
        "Cr0.20Fe0.80Ni0.0",
        "Cr0.40Fe0.0Ni0.60",
        "Cr0.40Fe0.12Ni0.48",
        "Cr0.40Fe0.24Ni0.36",
        "Cr0.40Fe0.36Ni0.24",
        "Cr0.40Fe0.48Ni0.12",
        "Cu0.13Fe0.54Ni0.33",
        "Cu0.20Co0.20Fe0.60",
        "Cu0.20Co0.60Fe0.20",
        "Cu0.20Fe0.10Ni0.70",
        "Cu0.20Fe0.20Ni0.60",
        "Cu0.20Fe0.35Ni0.45",
        "Cu0.20Fe0.48Ni0.32",
        "Cu0.20Fe0.65Ni0.15",
        "Cu0.40Fe0.35Ni0.25",
        "Cu0.50Fe0.30Ni0.20",
        "Cu0.60Fe0.24Ni0.16",
        "Cu0.70Fe0.13Ni0.17",
    }


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EmpiricalMulti()
    result1 = model.calculate(T=1700, x={"Fe": 0.2, "Cu": 0.6, "Ni": 0.2})
    result2 = model(T=1700, x={"Fe": 0.2, "Cu": 0.6, "Ni": 0.2})

    assert abs(result1 - result2) < 1e-9
