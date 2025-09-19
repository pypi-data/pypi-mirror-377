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
    Unary liquid metal density model.

    Returns:
       Density in [kg/m³].

    References:
        assael2006, assael2010, assael2012, ntonti2024
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["assael2006", "assael2010", "assael2012", "ntonti2024"]

    T_min: floatPositiveOrZero = 0.0
    T_max: floatPositiveOrZero = 0.0
    c1: floatPositiveOrZero = 0.0
    c2: floatPositiveOrZero = 0.0
    T_ref: floatPositiveOrZero = 0.0

    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.component_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate unary density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 1.0}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Density in [kg/m³].
        """
        if a != {}:
            raise ValueError("Specifying activities is not applicable to to liquid alloys.")

        data = EmpiricalUnary.data

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

        self.T_min = data[compound]["T_range_K"]["min"]
        self.T_max = data[compound]["T_range_K"]["max"]
        self.c1 = data[compound]["parameters"]["c1_kg_m3"]
        self.c2 = data[compound]["parameters"]["c2_kg_m3_K"]
        self.T_ref = data[compound]["parameters"]["T_ref_K"]

        if not (self.T_min <= T <= self.T_max):
            print(
                f"Warning: Temperature {T} K is outside the recommended range "
                f"({self.T_min} K to {self.T_max} K) for {compound}."
            )

        density = self.c1 - self.c2 * (T - self.T_ref)
        return density


EmpiricalUnary.load_data()
