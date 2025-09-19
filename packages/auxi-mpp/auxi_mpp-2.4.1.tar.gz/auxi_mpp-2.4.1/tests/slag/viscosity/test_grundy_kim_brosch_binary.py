"""Test GrundyKimBroschBinary model."""

from collections.abc import Callable

import pytest

from auxi.mpp.slag.μ._grundy_kim_brosch_binary import GrundyKimBroschBinary
from auxi.mpp.slag.μ._grundy_kim_brosch_unary import GrundyKimBroschUnary

from ..test_parameters.binary_multi._binary_testing_inputs import unary_vs_binary_test_inputs
from ..test_parameters.binary_multi_esf_dependent._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)
from ..test_parameters.binary_multi_esf_dependent._dummy_bff import dummy_bff
from ..test_parameters.binary_multi_esf_dependent._dummy_esf import dummy_esf


# tests that should pass
@pytest.mark.parametrize("temperature, composition, esf", binary_testing_inputs)
def test_grundy_kim_brosch_binary(
    temperature: float,
    composition: dict[str, float],
    esf: Callable[
        [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
    ],
):
    """Test temperature and composition limits."""
    model = GrundyKimBroschBinary(esf=esf)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition, esf", binary_error_test_inputs)
def test_grundy_kim_brosch_binary_errors(
    temperature: float,
    composition: dict[str, float],
    esf: Callable[
        [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
    ],
):
    """Test if invalid inputs will fail."""
    model = GrundyKimBroschBinary(esf=esf)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, composition", unary_vs_binary_test_inputs)
def test_viscosity_unary_vs_binary(temperature: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    unary_model = GrundyKimBroschUnary()
    binary_model = GrundyKimBroschBinary(esf=dummy_esf)

    compound = next(iter(composition.keys()))
    if compound != "SiO2":
        two_comps = {"SiO2": 0.0, f"{compound}": 1.0}
    else:
        two_comps = {"SiO2": 1.0, "Al2O3": 0.0}

    unary_result = unary_model.calculate(T=temperature, x=composition)
    binary_result = binary_model.calculate(T=temperature, x=two_comps)

    assert abs(binary_result - unary_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = GrundyKimBroschBinary(esf=dummy_esf)

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Slag"
    assert model.references == ["grundy2008-part1", "grundy2008-part2", "kim2012-part3"]

    assert model.esf == dummy_esf
    assert model.names["AlO15"] == "Al2O3"
    assert model.cation["SiO2"] == "Si"
    assert model.struc_unit["Al2O3"] == "AlO15"
    assert model.struc_ox_count["CaO"] == 1
    assert model.parameters["MgO"]["A"] == -10.58
    assert model.cation_count["Al2O3"] == 2
    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]

    model.calculate(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})

    assert sorted(list(model.structural_x.keys())) == ["AlO15", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = GrundyKimBroschBinary(esf=dummy_esf)
    result1 = model.calculate(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})
    result2 = model(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})

    assert abs(result1 - result2) < 1e-9


def test_normalise_fractions():
    """Test if the function normalises."""
    model = GrundyKimBroschBinary(esf=dummy_esf)

    composition = {"SiO2": 2, "Al2O3": 2}
    normalised_comp = model._normalise_fractions(composition)  # type: ignore
    assert abs(normalised_comp["SiO2"] - 0.5) < 1e-9

    composition = {"SiO2": 0.1, "MgO": 0.6, "Al2O3": 0.1}
    normalised_comp = model._normalise_fractions(composition)  # type: ignore
    assert abs(normalised_comp["MgO"] - 0.75) < 1e-9


def test_count_oxygens():
    """Test if the oxygens per mole is counted correctly."""
    model = GrundyKimBroschBinary(esf=dummy_esf)

    n_oxygens = model._count_oxygens({"SiO2": 0.5, "AlO15": 0.5})  # type: ignore

    assert n_oxygens == 1.75


# test for backwards compatibility
def test_backward_compatibility_with_bff():
    """Test backward compatibility."""
    with pytest.warns(
        DeprecationWarning,
        match="'bff' is deprecated and will be removed in a future version. Please use 'esf' instead.",
    ):
        model = GrundyKimBroschBinary(bff=dummy_bff)
    result = model.calculate(T=1800, x={"SiO2": 0.5, "MgO": 0.5})

    assert result >= 0


def test_raises_error_when_both_bff_and_esf_provided():
    """Raise error when both esf and bff is provided."""
    with pytest.raises(ValueError, match="Cannot provide both 'esf' and 'bff'"):
        GrundyKimBroschBinary(bff=dummy_bff, esf=dummy_esf)


def test_raises_error_when_neither_bff_nor_esf_provided():
    """Raise error when neither esf nor bff is provided."""
    with pytest.raises(ValueError, match="Please provide either 'esf' or 'bff'."):
        GrundyKimBroschBinary()
