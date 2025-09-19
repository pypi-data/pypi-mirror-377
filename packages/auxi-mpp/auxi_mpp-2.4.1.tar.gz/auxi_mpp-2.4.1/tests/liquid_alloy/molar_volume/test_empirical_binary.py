"""Test EmpiricalBinary model."""

import pytest

from auxi.mpp.liquid_alloy.Vm._empirical_binary import EmpiricalBinary

from ..test_parameters.density.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_empirical_binary(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = EmpiricalBinary()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", binary_error_test_inputs)
def test_empirical_binary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = EmpiricalBinary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = EmpiricalBinary()

    assert model.property == "Molar Volume"
    assert model.symbol == "Vm"
    assert model.display_symbol == "\\bar{V}"
    assert model.units == "\\cubic\\meter\\per\\mol"
    assert model.material == "Liquid Alloy"
    assert model.references == ["amore2013, assael2012, brillo2016"]

    assert set(model.compound_scope) == {
        "Ag0.10Al0.90",
        "Ag0.20Al0.80",
        "Ag0.20Cu0.80",
        "Ag0.25Au0.75",
        "Ag0.40Al0.60",
        "Ag0.40Cu0.60",
        "Ag0.50Au0.50",
        "Ag0.60Al0.40",
        "Ag0.60Cu0.40",
        "Ag0.75Au0.25",
        "Ag0.79Al0.21",
        "Ag0.80Cu0.20",
        "Al0.0Au1.0",
        "Al0.0Cu1.0",
        "Al0.10Ti0.90",
        "Al0.20Au0.80",
        "Al0.20Cu0.80",
        "Al0.20Ti0.80",
        "Al0.25Ni0.75",
        "Al0.27Au0.73",
        "Al0.30Cu0.70",
        "Al0.30Ti0.70",
        "Al0.33Au0.67",
        "Al0.40Cu0.60",
        "Al0.40Ti0.60",
        "Al0.50Au0.50",
        "Al0.50Cu0.50",
        "Al0.50Ni0.50",
        "Al0.50Ti0.50",
        "Al0.55Au0.45",
        "Al0.60Cu0.40",
        "Al0.60Fe0.40",
        "Al0.60Ni0.40",
        "Al0.60Ti0.40",
        "Al0.67Au0.33",
        "Al0.67Fe0.33",
        "Al0.70Cu0.30",
        "Al0.70Ni0.30",
        "Al0.70Ti0.30",
        "Al0.71Fe0.29",
        "Al0.75Fe0.25",
        "Al0.75Ni0.25",
        "Al0.80Au0.20",
        "Al0.80Cu0.20",
        "Al0.80Fe0.20",
        "Al0.80Ti0.20",
        "Al0.82Ni0.18",
        "Al0.85Au0.15",
        "Al0.8847Si0.1153",
        "Al0.90Fe0.10",
        "Al0.90Ti0.10",
        "Al1.0Au0.0",
        "Al1.0Cu0.0",
        "Au0.25Cu0.75",
        "Au0.50Cu0.50",
        "Au0.75Cu0.25",
        "Au1.0Cu0.0",
        "Co0.0Fe1.0",
        "Co0.0Cu1.0",
        "Co0.25Cu0.75",
        "Co0.25Fe0.75",
        "Co0.50Cu0.50",
        "Co0.50Fe0.50",
        "Co0.75Cu0.25",
        "Co0.75Fe0.25",
        "Co0.85Cu0.15",
        "Co1.0Cu0.0",
        "Co1.0Fe0.0",
        "Cr0.0Ni1.0",
        "Cr0.10Fe0.90",
        "Cr0.10Ni0.90",
        "Cr0.20Fe0.80",
        "Cr0.20Ni0.80",
        "Cr0.40Fe0.60",
        "Cr0.40Ni0.60",
        "Cu0.0Au1.0",
        "Cu0.0Fe1.0",
        "Cu0.0Ni1.0",
        "Cu0.0Ti1.0",
        "Cu0.10Ni0.90",
        "Cu0.1Ti0.9",
        "Cu0.2Ti0.8",
        "Cu0.25Au0.75",
        "Cu0.30Ni0.70",
        "Cu0.3Ti0.7",
        "Cu0.4Ti0.6",
        "Cu0.50Au0.50",
        "Cu0.50Ni0.50",
        "Cu0.50Si0.50",
        "Cu0.5Ti0.5",
        "Cu0.60Ni0.40",
        "Cu0.60Si0.40",
        "Cu0.6Ti0.4",
        "Cu0.65Si0.35",
        "Cu0.70Fe0.30",
        "Cu0.70Si0.30",
        "Cu0.7Ti0.3",
        "Cu0.725Si0.275",
        "Cu0.75Au0.25",
        "Cu0.75Si0.25",
        "Cu0.76Si0.24",
        "Cu0.775Si0.225",
        "Cu0.80Fe0.20",
        "Cu0.80Ni0.20",
        "Cu0.80Si0.20",
        "Cu0.84Si0.16",
        "Cu0.851Si0.149",
        "Cu0.834Si0.166",
        "Cu0.8Ti0.2",
        "Cu0.90Fe0.10",
        "Cu0.90Ni0.10",
        "Cu0.90Si0.10",
        "Cu0.95Si0.05",
        "Cu0.9Ti0.1",
        "Cu1.0Au0.0",
        "Cu1.0Fe0.0",
        "Cu1.0Ni0.0",
        "Cu1.0Ti0.0",
        "Fe0.0Ni1.0",
        "Fe0.20Ni0.80",
        "Fe0.40Ni0.60",
        "Fe0.50Cr0.50",
        "Fe0.50Ni0.50",
        "Fe0.60Cr0.40",
        "Fe0.60Ni0.40",
        "Fe0.70Cr0.30",
        "Fe0.80Cr0.20",
        "Fe0.80Ni0.20",
        "Fe0.90Cr0.10",
        "Fe1.0Cr0.0",
        "Fe1.0Ni0.0",
        "Pb0.261Sn0.739",
        "Pb0.4375Bi0.5625",
    }


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = EmpiricalBinary()
    result1 = model.calculate(T=1700, x={"Fe": 0.3, "Cu": 0.7})
    result2 = model(T=1700, x={"Fe": 0.3, "Cu": 0.7})

    assert abs(result1 - result2) < 1e-9
