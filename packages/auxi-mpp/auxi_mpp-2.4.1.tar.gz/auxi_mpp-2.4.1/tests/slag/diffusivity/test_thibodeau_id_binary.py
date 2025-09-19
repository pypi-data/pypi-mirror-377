"""Test ThibodeauIDBinary model."""

from collections.abc import Callable

import pytest

from auxi.mpp.slag.D._thibodeau_id_binary import ThibodeauIDBinary
from auxi.mpp.slag.D._thibodeau_id_unary import ThibodeauIDUnary

from ..test_parameters.binary_multi._binary_testing_inputs import unary_vs_binary_test_inputs
from ..test_parameters.binary_multi_esf_dependent._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)
from ..test_parameters.binary_multi_esf_dependent._dummy_bff import dummy_bff
from ..test_parameters.binary_multi_esf_dependent._dummy_esf import dummy_esf


# tests that should pass
@pytest.mark.parametrize("temperature, composition, esf", binary_testing_inputs)
def test_thibodeau_id_binary(
    temperature: float,
    composition: dict[str, float],
    esf: Callable[
        [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
    ],
):
    """Test temperature and composition limits."""
    model = ThibodeauIDBinary(esf=esf)
    result = model.calculate(T=temperature, x=composition)

    comp_list = list(composition.keys())

    for comp in comp_list:
        assert result[comp] > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition, esf", binary_error_test_inputs)
def test_thibodeau_binary_id_errors(
    temperature: float,
    composition: dict[str, float],
    esf: Callable[
        [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
    ],
):
    """Test if invalid inputs will fail."""
    model = ThibodeauIDBinary(esf=esf)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, composition", unary_vs_binary_test_inputs)
def test_diffusivity_unary_vs_binary(temperature: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    unary_model = ThibodeauIDUnary()
    binary_model = ThibodeauIDBinary(esf=dummy_esf)

    compound = next(iter(composition.keys()))
    if compound != "SiO2":
        two_comps = {"SiO2": 0.0, f"{compound}": 1.0}
    else:
        two_comps = {"SiO2": 1.0, "Al2O3": 0.0}

    unary_result = unary_model.calculate(T=temperature, x=composition)
    binary_result = binary_model.calculate(T=temperature, x=two_comps)

    assert abs(binary_result[compound] - unary_result[compound]) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = ThibodeauIDBinary(esf=dummy_esf)

    assert model.property == "Diffusivity"
    assert model.symbol == "D"
    assert model.display_symbol == "D"
    assert model.units == "\\meter\\squared\\per\\second"
    assert model.material == "Slag"
    assert model.references == ["thibodeau2016-ec", "thibodeau2016-ec-disseration"]

    assert model.esf == dummy_esf
    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = ThibodeauIDBinary(esf=dummy_esf)
    composition = {"SiO2": 0.5, "Al2O3": 0.5}

    result1 = model.calculate(T=1700, x=composition)
    result2 = model(T=1700, x=composition)

    comp_list = list(composition.keys())

    for comp in comp_list:
        assert abs(result1[comp] - result2[comp]) < 1e-9


# test for backwards compatibility
def test_backward_compatibility_with_bff():
    """Test backward compatibility."""
    with pytest.warns(
        DeprecationWarning,
        match="'bff' is deprecated and will be removed in a future version. Please use 'esf' instead.",
    ):
        model = ThibodeauIDBinary(bff=dummy_bff)
    result = model.calculate(T=1800, x={"SiO2": 0.5, "MgO": 0.5})

    for comp in result:
        assert result[comp] >= 0


def test_raises_error_when_both_bff_and_esf_provided():
    """Raise error when both esf and bff is provided."""
    with pytest.raises(ValueError, match="Cannot provide both 'esf' and 'bff'"):
        ThibodeauIDBinary(bff=dummy_bff, esf=dummy_esf)


def test_raises_error_when_neither_bff_nor_esf_provided():
    """Raise error when neither esf nor bff is provided."""
    with pytest.raises(ValueError, match="Please provide either 'esf' or 'bff'."):
        ThibodeauIDBinary()
