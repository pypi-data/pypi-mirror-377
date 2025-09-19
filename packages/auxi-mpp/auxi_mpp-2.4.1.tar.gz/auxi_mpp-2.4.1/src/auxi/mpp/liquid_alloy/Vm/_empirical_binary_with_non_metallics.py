from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..ρ import EmpiricalBinaryWithNonMetallics as EmpiricalBinaryWithNonMetallicsDensity
from ._model import Model


class EmpiricalBinaryWithNonMetallics(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid alloy molar volume model for metallic alloys containing non-metals.

    Returns:
       Molar volume in [m³/mol].

    References:
        amore2013, assael2012, brillo2016.
    """

    data: ClassVar[dict[str, dict[str, Any]]] = EmpiricalBinaryWithNonMetallicsDensity.data

    references: ClassVar[list[strNotEmpty]] = EmpiricalBinaryWithNonMetallicsDensity.references

    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    density_binary_with_non_metallics: EmpiricalBinaryWithNonMetallicsDensity = Field(
        default_factory=EmpiricalBinaryWithNonMetallicsDensity
    )

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.density_binary_with_non_metallics = EmpiricalBinaryWithNonMetallicsDensity()

        self.component_scope: list[strCompoundFormula] = self.density_binary_with_non_metallics.component_scope
        self.system_scope: list[strNotEmpty] = self.density_binary_with_non_metallics.system_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate molar volume of binary system containing non-metallics.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.9, "C": 0.1}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Molar volume in [m³/mol].
        """
        ρ = self.density_binary_with_non_metallics.calculate(T=T, p=p, x=x, a=a)

        # get the molar mass of the specified compound
        compound_molar_mass: float = 0.0

        for component, comp in x.items():
            molar_mass: float = stoic.molar_mass(component)
            compound_molar_mass += comp * molar_mass

        # scale to units of m-3/mol
        Vm = (compound_molar_mass / ρ) * 1e-3

        return Vm
