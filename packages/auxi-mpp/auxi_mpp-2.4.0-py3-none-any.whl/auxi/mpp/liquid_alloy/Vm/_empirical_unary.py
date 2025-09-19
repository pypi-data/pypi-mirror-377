from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..ρ import EmpiricalUnary as EmpiricalUnaryDensity
from ._model import Model


class EmpiricalUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid metal molar volume model.

    Returns:
       Molar volume in [m³/mol].

    References:
        assael2006, assael2010, assael2012, ntonti2024
    """

    data: ClassVar[dict[str, dict[str, Any]]] = EmpiricalUnaryDensity.data

    references: ClassVar[list[strNotEmpty]] = EmpiricalUnaryDensity.references

    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    density_unary: EmpiricalUnaryDensity = Field(default_factory=EmpiricalUnaryDensity)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.density_unary = EmpiricalUnaryDensity()

        self.component_scope: list[strCompoundFormula] = self.density_unary.component_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate unary molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 1.0}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Molar volume in [m³/mol].
        """
        ρ = self.density_unary.calculate(T=T, p=p, x=x, a=a)

        compound = list(x.keys())
        compound = compound[0]

        # get the molar mass of the specified compound
        molar_mass: float = stoic.molar_mass(compound)

        # scale to units of m-3/mol
        Vm = (molar_mass / ρ) * 1e-3

        return Vm
