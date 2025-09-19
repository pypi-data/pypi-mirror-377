from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..ρ import MillsCommercial as MillsCommercialDensity
from ._model import Model


class MillsCommercial(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Liquid alloy molar volume model for commercial iron-based alloys.

    The model expects the composition dictionary `x` to contain a single key
    identifying the commercial alloy by its name (e.g., {"grey_cast_iron": 1.0}).

    Returns:
       Molar volume in [m³/mol].

    References:
        mills2002
    """

    data: ClassVar[dict[str, dict[str, Any]]] = MillsCommercialDensity.data

    references: ClassVar[list[strNotEmpty]] = MillsCommercialDensity.references

    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    composition_wt_pct: dict[str, dict[str, float]] = Field(default_factory=dict)

    density_commercial: MillsCommercialDensity = Field(default_factory=MillsCommercialDensity)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.density_commercial = MillsCommercialDensity()

        self.compound_scope: list[strCompoundFormula] = self.density_commercial.compound_scope

        self.composition_wt_pct = self.density_commercial.composition_wt_pct

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate commercial alloy molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary, used to specify the alloy.
               It must contain exactly one key which is the alloy identifier.
               E.g., {"grey_cast_iron": 1.0}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Molar volume in [m³/mol].
        """
        ρ = self.density_commercial.calculate(T=T, p=p, x=x, a=a)

        # get the molar mass of the specified compound
        compound_molar_mass: float = 0.0
        compound = list(x.keys())
        compound = compound[0]

        compound_composition_wt_pct = self.composition_wt_pct[compound]
        compound_composition = stoic.amount_fractions(compound_composition_wt_pct)

        compound_molar_mass: float = 0.0
        for component, comp in compound_composition.items():
            molar_mass: float = stoic.molar_mass(component)
            compound_molar_mass += comp * molar_mass

        # scale to units of m-3/mol
        Vm = (compound_molar_mass / ρ) * 1e-3

        return Vm
