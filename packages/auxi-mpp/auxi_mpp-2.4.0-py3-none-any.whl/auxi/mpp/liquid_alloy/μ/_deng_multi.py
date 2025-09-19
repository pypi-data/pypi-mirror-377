from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._ferrous_liquid_alloy_tpxa_state import FerrousLiquidAlloyTpxaState
from ._model import Model


class DengMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component liquid alloy viscosity model.

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
    system_scope: list[strNotEmpty] = sorted(["Fe-C-Si", "Fe-C-Mn", "Fe-C-P", "Fe-C-S", "Fe-C-Ti"])

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = DengMulti.data
        self.component_scope = list(data.keys())

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
        Calculate multi-component system viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.5, "Si": 0.25, "C": 0.25}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Viscosity in [Pa.s].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to to liquid alloys.")

        # Validate input state
        state = FerrousLiquidAlloyTpxaState(T=T, p=p, x=x, a={})

        for component in state.x:
            if component not in self.component_scope:
                raise ValueError(
                    f"{component} is not a valid system component. Valid options are '{' '.join(self.component_scope)}'."
                )

        # The model uses weight percent, but the state is in mole fraction.
        y = stoic.mass_fractions(x)
        composition_wt_pct = {k: v * 100 for k, v in y.items()}

        # Validate component composition ranges Fe-C-<element> system.
        if len(state.x) == 3:
            for component in state.x.keys():
                if component not in ["Fe", "C"]:
                    composition_wt_pct_fe_max = (
                        100 - self.component_wt_pct_max["C"] - self.component_wt_pct_min[component]
                    )
                    composition_wt_pct_fe_min = (
                        100 - self.component_wt_pct_max["C"] - self.component_wt_pct_max[component]
                    )
                    comp_1 = {
                        "Fe": composition_wt_pct_fe_max,
                        "C": self.component_wt_pct_max["C"],
                        component: self.component_wt_pct_min[component],
                    }
                    comp_2 = {
                        "Fe": composition_wt_pct_fe_min,
                        "C": self.component_wt_pct_max["C"],
                        component: self.component_wt_pct_max[component],
                    }
                    x_limit_1 = stoic.amount_fractions(comp_1)
                    x_limit_2 = stoic.amount_fractions(comp_2)
                    if not (x_limit_1[component] <= x[component] <= x_limit_2[component]):
                        print(
                            f"Warning: Composition of {component} ({x[component]:.4f}) is outside the valid range of {x_limit_1[component]:.4f} to {x_limit_2[component]:.4f} mole fraction for Fe-C-{component} model."
                        )

        eta_mPas: float = 0.0
        # Add the contribution from each solute.
        for element, wt_percent in composition_wt_pct.items():
            if element == "Fe":
                eta_mPas = self.parameters["Fe"]["const"] + self.parameters["Fe"]["T_k"] * T
                continue
            if element == "C":
                eta_mPas += self.parameters["C"]["component_coefficient"] * wt_percent
                continue
            if element in self.parameters:
                eta_mPas += self.parameters[element]["component_coefficient"] * wt_percent

        # Convert result from mPa·s to final value in Pa·s.
        viscosity_pa_s = eta_mPas / 1000.0

        return viscosity_pa_s


DengMulti.load_data()
