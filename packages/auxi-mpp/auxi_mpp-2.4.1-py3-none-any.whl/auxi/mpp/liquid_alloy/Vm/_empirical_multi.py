from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..ρ import EmpiricalMulti as EmpiricalMultiDensity
from ._model import Model


class EmpiricalMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component liquid alloy molar volume model.

    Returns:
       Molar volume in [m³/mol].

    References:
        brillo2006, brillo2016, kobatake2013
    """

    data: ClassVar[dict[str, dict[str, Any]]] = EmpiricalMultiDensity.data

    references: ClassVar[list[strNotEmpty]] = EmpiricalMultiDensity.references

    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    density_multi: EmpiricalMultiDensity = Field(default_factory=EmpiricalMultiDensity)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.density_multi = EmpiricalMultiDensity()

        self.compound_scope: list[strCompoundFormula] = self.density_multi.compound_scope
        self.component_scope: list[strCompoundFormula] = self.density_multi.component_scope
        self.system_scope: list[strNotEmpty] = self.density_multi.system_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Ag": 0.1, "Al": 0.6, "Cu": 0.3}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Molar volume in [m³/mol].
        """
        ρ = self.density_multi.calculate(T=T, p=p, x=x, a=a)

        # get the molar mass of the specified compound
        compound_molar_mass: float = 0.0

        for component, comp in x.items():
            molar_mass: float = stoic.molar_mass(component)
            compound_molar_mass += comp * molar_mass

        # scale to units of m-3/mol
        Vm = (compound_molar_mass / ρ) * 1e-3

        return Vm
