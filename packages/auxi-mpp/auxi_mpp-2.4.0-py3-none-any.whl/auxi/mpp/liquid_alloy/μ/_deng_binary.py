from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._ferrous_liquid_alloy_binary_tpx_state import FerrousLiquidAlloyBinaryTpxState
from ._model import Model


class DengBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid alloy viscosity model.

    Returns:
       Viscosity in [Pa·s].

    References:
        deng2018
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}
    references: ClassVar[list[strNotEmpty]] = ["deng2018"]

    # Model parameters to be loaded from the YAML file
    T_min: floatPositiveOrZero = Field(default_factory=float)
    T_max: floatPositiveOrZero = Field(default_factory=float)
    component_wt_pct_min: dict[str, float] = Field(default_factory=dict)
    component_wt_pct_max: dict[str, float] = Field(default_factory=dict)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)

    # The scope of elements supported by this model
    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = sorted(["Fe-C"])

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = DengBinary.data
        self.component_scope = sorted(list(data.keys()))
        # Load parameters for each component
        self.T_min = data["Fe"]["T_range_K"]["min"]
        self.T_max = data["Fe"]["T_range_K"]["max"]
        self.component_wt_pct_min = {c: data[c]["wt_pct_range"]["min"] for c in self.component_scope if c != "Fe"}
        self.component_wt_pct_max = {c: data[c]["wt_pct_range"]["max"] for c in self.component_scope if c != "Fe"}
        self.parameters = {c: data[c]["parameters"] for c in self.component_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.5, "Si": 0.5}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Viscosity in [Pa.s].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to to liquid alloys.")

        # # Validate input
        state = FerrousLiquidAlloyBinaryTpxState(T=T, p=p, x=x)
        for component in state.x:
            if component not in self.component_scope:
                raise ValueError(
                    f"{component} is not a valid system component. Valid options are '{' '.join(self.component_scope)}'."
                )

        # The model uses weight pct, but the state is in mole fraction.
        y = stoic.mass_fractions(x)
        composition_wt_pct = {k: v * 100 for k, v in y.items()}

        # Validate composition ranges
        composition_wt_pct_fe_max = 100 - self.component_wt_pct_min["C"]
        composition_wt_pct_fe_min = 100 - self.component_wt_pct_max["C"]
        x_limit_1 = stoic.amount_fractions({"Fe": composition_wt_pct_fe_max, "C": self.component_wt_pct_min["C"]})
        x_limit_2 = stoic.amount_fractions({"Fe": composition_wt_pct_fe_min, "C": self.component_wt_pct_max["C"]})
        if not (x_limit_1["C"] <= x["C"] <= x_limit_2["C"]):
            print(
                f"Warning: Composition of C ({x['C']:.4f}) is outside the valid range  of {x_limit_1['C']:.4f} to {x_limit_2['C']:.4f} mole fraction) for Fe-C model."
            )

        eta_mPas: float = 0.0
        # Add the contribution from each solute.
        for element, wt_pct in composition_wt_pct.items():
            if element == "Fe":
                eta_mPas += self.parameters["Fe"]["const"] + self.parameters["Fe"]["T_K"] * T
                continue
            if element == "C":
                eta_mPas += self.parameters["C"]["component_coefficient"] * wt_pct
                continue
        # Convert result from mPa·s to final value in Pa·s.
        viscosity_pa_s = eta_mPas / 1000.0

        return viscosity_pa_s


DengBinary.load_data()
