from typing import Any, ClassVar

from pydantic import Field

from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

# from ..state._liquid_alloy_tpxa_state import LiquidAlloyTpxaState
from ...core.material_state import TpxState
from ._model import Model


class MillsCommercial(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Liquid alloy density model for commercial iron-based alloys.

    The model expects the composition dictionary `x` to contain a single key
    identifying the commercial alloy by its name (e.g., {"grey_cast_iron": 1.0}).

    Returns:
       Density in [kg/m³].

    References:
        mills2002
    """

    # Class variable to hold the raw data loaded from the YAML file.
    data: ClassVar[dict[str, dict[str, Any]]] = {}

    # Class variable for literature references.
    references: ClassVar[list[strNotEmpty]] = ["mills2002"]

    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    T_min: dict[str, float] = Field(default_factory=dict)
    T_max: dict[str, float] = Field(default_factory=dict)
    composition_wt_pct: dict[str, dict[str, float]] = Field(default_factory=dict)
    A: dict[str, float] = Field(default_factory=dict)
    B: dict[str, float] = Field(default_factory=dict)
    T_ref_C: dict[str, float] = Field(default_factory=dict)
    C_si: dict[str, float] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = MillsCommercial.data
        self.compound_scope = list(data.keys())

        # Populate the parameter dictionaries for each alloy
        for alloy in self.compound_scope:
            self.T_min[alloy] = data[alloy]["T_range_K"]["min"]
            self.T_max[alloy] = data[alloy]["T_range_K"]["max"]
            self.composition_wt_pct[alloy] = data[alloy]["composition_wt_pct"]

            params = data[alloy]["parameters"]
            self.A[alloy] = params["A_kg_m3"]
            self.B[alloy] = params["B_kg_m3_C"]
            self.T_ref_C[alloy] = params["T_ref_C"]
            if "C_si_kg_m3_wt" in params:
                self.C_si[alloy] = params["C_si_kg_m3_wt"]

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate commercial alloy density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa] (Not used in this model)
            x: Chemical composition dictionary, used to specify the alloy.
               It must contain exactly one key which is the alloy identifier.
               E.g., {"grey_cast_iron": 1.0}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Density in [kg/m³].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")
        if len(x) != 1:
            raise ValueError(
                f"Composition dict `x` must contain exactly one key specifying the alloy. Found {len(x)} keys."
            )

        alloy_name = next(iter(x))

        if alloy_name not in self.compound_scope:
            raise ValueError(
                f"Alloy '{alloy_name}' is not supported. Supported alloys are: {', '.join(self.compound_scope)}"
            )

        # Validate input state
        state = TpxState(T=T, p=p, x=x)

        # Check if temperature is within the model's valid range
        if not (self.T_min[alloy_name] <= state.T <= self.T_max[alloy_name]):
            print(
                f"Warning: Temperature {state.T:.2f} K is outside the recommended range "
                f"({self.T_min[alloy_name]:.2f} - {self.T_max[alloy_name]:.2f} K) for {alloy_name}."
            )

        if state.T < self.T_min[alloy_name]:
            raise ValueError(
                f"Temperature ({state.T:.2f} K) is below the liquidus temperature ({self.T_min[alloy_name]:.2f} K)."
            )

        # Convert temperature to Celsius for the calculation, as the original formulas use it
        T_C = state.T - 273.15

        # Base density calculation using the original equation form
        density = self.A[alloy_name] - self.B[alloy_name] * (T_C - self.T_ref_C[alloy_name])

        # Add silicon-dependent term if applicable for the alloy
        if alloy_name in self.C_si:
            si_content = self.composition_wt_pct[alloy_name]["Si"]
            density -= self.C_si[alloy_name] * si_content

        return density


MillsCommercial.load_data()
