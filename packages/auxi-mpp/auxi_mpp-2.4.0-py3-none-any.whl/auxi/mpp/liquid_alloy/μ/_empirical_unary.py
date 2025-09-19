from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._liquid_metal_tpx_state import LiquidMetalTpxState
from ._model import Model


class EmpiricalUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid metal viscosity model.

    Returns:
       Viscosity in [Pa.s].

    References:
        assael2006, assael2010, assael2012
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["assael2006", "assael2010", "assael2012"]

    T_min: dict[str, float] = Field(default_factory=dict)
    T_max: dict[str, float] = Field(default_factory=dict)
    a1: dict[str, float] = Field(default_factory=dict)
    a2: dict[str, float] = Field(default_factory=dict)

    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = EmpiricalUnary.data
        self.component_scope = list(self.data.keys())

        self.T_min = {c: data[c]["T_range_K"]["min"] for c in self.component_scope}
        self.T_max = {c: data[c]["T_range_K"]["max"] for c in self.component_scope}
        self.a1 = {c: data[c]["parameters"]["a1_dimensionless"] for c in self.component_scope}
        self.a2 = {c: data[c]["parameters"]["a2_K"] for c in self.component_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate unary viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 1.0}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Viscosity in [Pa.s].
        """
        if a != {}:
            raise ValueError("Specifying activities is not applicable to to liquid alloys.")

        # validate input
        state = LiquidMetalTpxState(T=T, p=p, x=x)

        # ensure only one compound is given
        compound = list(state.x.keys())
        if len(compound) > 1:
            raise ValueError("Only one compound should be specified.")
        compound = compound[0]

        # validate input
        if compound not in self.component_scope:
            raise ValueError(
                f"{compound} is not a valid formula. Valid options are '{' '.join(self.component_scope)}'."
            )

        if not (self.T_min[compound] <= T <= self.T_max[compound]):
            print(
                f"Warning: Temperature {T} K is outside the recommended range "
                f"({self.T_min[compound]} K to {self.T_max[compound]} K) for {compound}."
            )

        viscosity = 10 ** (-self.a1[compound] + self.a2[compound] / T)
        return viscosity / 1000


EmpiricalUnary.load_data()
