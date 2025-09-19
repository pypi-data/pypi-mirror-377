from typing import Any, ClassVar

import numpy as np
from pydantic import Field

from auxi.chemistry import stoichiometry as stoic
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._liquid_alloy_binary_tpxa_state import LiquidAlloyBinaryTpxaState
from ._model import Model


class EmpiricalBinaryWithNonMetallics(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid alloy density model for metallic alloys containing non-metals.

    Returns:
       Density in [kg/m³].

    References:
        tesfaye2010, miettinen1997, nagamori1969, jimbocramb1993
    """

    data: ClassVar[dict[str, Any]] = {}

    references: ClassVar[list[strNotEmpty]] = ["tesfaye2010", "miettinen1997", "nagamori1969", "jimbocramb1993"]

    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    non_metallic_scope: dict[str, str] = Field(default_factory=dict)
    models: dict[str, str] = Field(default_factory=dict)
    models_parameters: dict[str, dict[str, float]] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = EmpiricalBinaryWithNonMetallics.data
        self.system_scope = list(data.keys())

        unique_components: set[str] = set()
        for system in self.system_scope:
            components = system.split("-")
            unique_components.update(components)

        self.component_scope = sorted(list(unique_components))

        self.non_metallic_scope = {c: data[c]["non-metallic"] for c in self.system_scope}
        self.models = {c: data[c]["method"] for c in self.system_scope}
        self.models_parameters = {c: data[c]["parameters"] for c in self.system_scope}

    # define different models for use for different compositions
    def _rho_Fe_S_Miettinen(self, T_K: float, x_S: float, params: dict[str, float]) -> float:
        """Density of liquid Fe-S melts (Miettinen et al.)."""
        T_min_K = params["T_min_C"] + 273.15
        T_max_K = params["T_max_C"] + 273.15
        if not (T_min_K <= T_K <= T_max_K):
            raise ValueError(
                f"Error: Temperature ({T_K:.2f} K) is outside the valid range for the Miettinen Fe-S model."
            )

        x_S_min = stoic.amount_fractions({"Fe": 100 - params["wt_pct_s_min"], "S": params["wt_pct_s_min"]})["S"]
        x_S_max = stoic.amount_fractions({"Fe": 100 - params["wt_pct_s_max"], "S": params["wt_pct_s_max"]})["S"]
        if not (x_S_min <= x_S <= x_S_max):
            raise ValueError(
                f"Error: Composition ({x_S:.2f} S) is outside the valid range of {x_S_min:.2f} and {x_S_max:.2f} for the Miettinen Fe-S model."
            )

        T_C = T_K - 273.15
        C_s: float = stoic.mass_fractions({"Fe": 1 - x_S, "S": x_S})["S"] * 100
        a_s: float = params["a0"] + params["a1"] * T_C - params["a2"] * C_s

        rho_kg_m3: float = params["b0"] - params["b1"] * T_C + a_s * C_s
        return rho_kg_m3

    def _rho_Fe_S_Nagamori(self, T_K: float, x_S: float, params: dict[str, float]) -> float:
        """Density of molten Fe-S melts at 1473.15 K (Nagamori)."""
        if not np.isclose(T_K, params["T_K"]):
            raise ValueError(
                f"Error: Temperature ({T_K:.2f} K) is only valid at {params['T_K']} K for the Nagamori Fe-S model."
            )

        x_S_min = stoic.amount_fractions({"Fe": 100 - params["wt_pct_s_min"], "S": params["wt_pct_s_min"]})["S"]
        x_S_max = stoic.amount_fractions({"Fe": 100 - params["wt_pct_s_max"], "S": params["wt_pct_s_max"]})["S"]
        if not (x_S_min <= x_S <= x_S_max):
            raise ValueError(
                f"Error: Composition ({x_S:.2f} S) is outside the valid range of {x_S_min:.2f} and {x_S_max:.2f} for the Nagamori Fe-S model."
            )

        wt_percent_S = stoic.mass_fractions({"Fe": 1 - x_S, "S": x_S})["S"] * 100
        rho_g_cm3 = params["c0"] - params["c1"] * wt_percent_S - params["c2"] * (wt_percent_S**2)
        rho_kg_m3 = rho_g_cm3 * 1000
        return rho_kg_m3

    def _rho_Ni_S_Nagamori(self, T_K: float, x_S: float, params: dict[str, float]) -> float:
        """Density of Ni-S melts (Nagamori)."""
        T_min_K = params["T_min_C"] + 273.15
        T_max_K = params["T_max_C"] + 273.15
        if not (T_min_K <= T_K <= T_max_K):
            raise ValueError(
                f"Error: Temperature ({T_K:.2f} K) is outside the valid range for the Nagamori Ni-S model."
            )

        x_S_min = stoic.amount_fractions({"Ni": 100 - params["wt_pct_s_min"], "S": params["wt_pct_s_min"]})["S"]
        x_S_max = stoic.amount_fractions({"Ni": 100 - params["wt_pct_s_max"], "S": params["wt_pct_s_max"]})["S"]
        if not (x_S_min <= x_S <= x_S_max):
            raise ValueError(
                f"Error: Composition ({x_S:.2f} S) is outside the valid range of {x_S_min:.2f} and {x_S_max:.2f} for the Nagamori Ni-S model."
            )

        T_C = T_K - 273.15
        wt_percent_S = stoic.mass_fractions({"Ni": 1 - x_S, "S": x_S})["S"] * 100
        rho_at_1200C = params["c0"] - params["c1"] * wt_percent_S - params["c2"] * (wt_percent_S**2)
        d_rho_dT = params["d0"] + params["d1"] * wt_percent_S
        rho_g_cm3 = rho_at_1200C + d_rho_dT * (T_C - 1200)

        return rho_g_cm3 * 1000

    def _rho_Cu_S_Nagamori(self, T_K: float, x_S: float, params: dict[str, float]) -> float:
        """Density of molten Cu-S melts at 1473.15 K (Nagamori)."""
        if not np.isclose(T_K, params["T_K"]):
            raise ValueError(
                f"Error: Temperature ({T_K:.2f} K) is only valid at {params['T_K']} K for the Nagamori Cu-S model."
            )

        x_S_min = stoic.amount_fractions({"Cu": 100 - params["wt_pct_s_min"], "S": params["wt_pct_s_min"]})["S"]
        x_S_max = stoic.amount_fractions({"Cu": 100 - params["wt_pct_s_max"], "S": params["wt_pct_s_max"]})["S"]
        if not (x_S_min <= x_S <= x_S_max):
            raise ValueError(
                f"Error: Composition ({x_S:.2f} S) is outside the valid range of {x_S_min:.2f} and {x_S_max:.2f} for the Nagamori Cu-S model."
            )

        wt_percent_S = stoic.mass_fractions({"Cu": 1 - x_S, "S": x_S})["S"] * 100
        rho_g_cm3 = params["c0"] - params["c1"] * wt_percent_S
        return rho_g_cm3 * 1000

    def _rho_Fe_C_jimbo_cramb(self, T_K: float, x_C: float, params: dict[str, float]) -> float:
        """
        Calculate the density of liquid Fe-C alloys (Jimbo and Cramb).
        """
        T_min_K = params["T_min_C"] + 273.15
        T_max_K = params["T_max_C"] + 273.15
        if not (T_min_K <= T_K <= T_max_K):
            raise ValueError(f"Error: Temperature ({T_K:.2f} K) is outside the model's valid range.")

        x_C_min = stoic.amount_fractions({"Fe": 100 - params["wt_pct_c_min"], "C": params["wt_pct_c_min"]})["C"]
        x_C_max = stoic.amount_fractions({"Fe": 100 - params["wt_pct_c_max"], "C": params["wt_pct_c_max"]})["C"]
        if not (x_C_min <= x_C <= x_C_max):
            raise ValueError(
                f"Error: Carbon content ({x_C:.2f} C) is outside valid range of {x_C_min:.2f} and {x_C_max:.2f} for the Jimbo and Cramb Fe-C model."
            )

        wt_pct_C: float = stoic.mass_fractions({"Fe": 1 - x_C, "C": x_C})["C"] * 100
        rho_g_cm3 = (params["a0"] - params["a1"] * wt_pct_C) - (params["b0"] - params["b1"] * wt_pct_C) * 1e-4 * (
            T_K - 1823
        )
        return rho_g_cm3 * 1000

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate density of binary system containing non-metallics.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.9, "C": 0.1}.
            a: Phase constituent activity dictionary. Not applicable for liquid alloys.

        Returns:
            Density in [kg/m³].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        state = LiquidAlloyBinaryTpxaState(T=T, p=p, x=x, a={})

        system_key = "-".join(sorted(state.x.keys()))

        if system_key not in self.system_scope:
            raise ValueError(
                f"System '{system_key}' is not currently supported. Supported systems are: {self.system_scope}"
            )

        # Get the parameters for the system's model
        system_model_params = self.models_parameters[system_key]
        system_non_metallic_component = self.non_metallic_scope[system_key]

        method_name = self.models[system_key]
        calculation_method = getattr(self, f"_{method_name}")

        return calculation_method(T, state.x[system_non_metallic_component], system_model_params)


EmpiricalBinaryWithNonMetallics.load_data()
