from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..ρ import EmpiricalBinary as EmpiricalBinaryDensity
from ._model import Model


class EmpiricalBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid alloy molar volume model.

    Returns:
       Molar volume in [m³/mol].

    References:
        amore2013, assael2012, brillo2016.
    """

    data: ClassVar[dict[str, dict[str, Any]]] = EmpiricalBinaryDensity.data

    references: ClassVar[list[strNotEmpty]] = EmpiricalBinaryDensity.references

    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    density_binary: EmpiricalBinaryDensity = Field(default_factory=EmpiricalBinaryDensity)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.density_binary = EmpiricalBinaryDensity()

        self.compound_scope: list[strCompoundFormula] = self.density_binary.compound_scope
        self.system_scope: list[strNotEmpty] = self.density_binary.system_scope
        self.component_scope: list[strCompoundFormula] = self.density_binary.component_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.8,"Ni":0.2}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Molar volume in [m³/mol].
        """
        ρ = self.density_binary.calculate(T=T, p=p, x=x, a=a)

        # get the molar mass of the specified compound
        compound_molar_mass: float = 0.0

        for component, comp in x.items():
            molar_mass: float = stoic.molar_mass(component)
            compound_molar_mass += comp * molar_mass

        # scale to units of m-3/mol
        Vm = (compound_molar_mass / ρ) * 1e-3

        return Vm
