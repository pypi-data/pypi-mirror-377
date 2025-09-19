import re
from re import Pattern
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._liquid_alloy_binary_tpxa_state import LiquidAlloyBinaryTpxaState
from ._model import Model


class EmpiricalBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid alloy density model.

    Returns:
       Density in [kg/m³].

    References:
        amore2013, assael2012, brillo2016
    """

    # TODO: create dedicated file for all constants used in auxi-mpp
    COMPOUND_PATTERN: Pattern[str] = re.compile(r"([A-Z][a-z]?)(\d+\.?\d*)")

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["amore2013, assael2012, brillo2016"]

    # model parameters loaded from data
    T_min: dict[str, float] = Field(default_factory=dict)
    T_max: dict[str, float] = Field(default_factory=dict)
    c1: dict[str, float] = Field(default_factory=dict)
    c2: dict[str, float] = Field(default_factory=dict)
    T_liquidus: dict[str, float] = Field(default_factory=dict)

    # processed data structures for calculation
    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    system_data: dict[str, dict[float, str]] = Field(default_factory=dict)
    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = EmpiricalBinary.data
        self.compound_scope = list(data.keys())

        # Load parameters for each compound
        self.T_min = {c: data[c]["T_range_K"]["min"] for c in self.compound_scope}
        self.T_max = {c: data[c]["T_range_K"]["max"] for c in self.compound_scope}
        self.c1 = {c: data[c]["parameters"]["c1_kg_m3"] for c in self.compound_scope}
        self.c2 = {c: data[c]["parameters"]["c2_kg_m3_K"] for c in self.compound_scope}
        self.T_liquidus = {c: data[c]["parameters"]["liquidus_T_K"] for c in self.compound_scope}

        self._get_component_scope()
        self._get_system_data()

    def _get_component_scope(self):
        # Regular expression to parse chemical formulas
        unique_components: set[str] = set()

        for formula in self.compound_scope:
            matches = re.findall(self.COMPOUND_PATTERN, formula)

            components = sorted([elem for elem, _ in matches])
            unique_components.update(components)

        self.component_scope = sorted(list(unique_components))

    def _get_system_data(self):
        # Regular expression to parse chemical formulas
        unique_components: set[str] = set()

        # Group compounds by their constituent components (systems)
        systems: dict[tuple[str, ...], list[str]] = {}
        for formula in self.compound_scope:
            matches = re.findall(self.COMPOUND_PATTERN, formula)

            components = sorted([elem for elem, _ in matches])
            system_key = tuple(components)
            unique_components.update(components)

            if system_key not in systems:
                systems[system_key] = []
            systems[system_key].append(formula)

        # For each system, map compositions (by fraction of 2nd component) to formulas
        for components_tuple, formulas in systems.items():
            system_key = "-".join(components_tuple)
            self.system_scope.append(system_key)
            self.system_data[system_key] = {}

            # The second component in the sorted tuple is used for the x-axis in interpolation
            component_for_lookup = components_tuple[1]

            for formula in formulas:
                matches = re.findall(self.COMPOUND_PATTERN, formula)
                composition = {elem: float(val) for elem, val in matches}
                total = sum(composition.values())

                # Normalize to mole fraction
                fraction = composition.get(component_for_lookup, 0.0) / total
                self.system_data[system_key][fraction] = formula

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Fe": 0.8,"Ni":0.2}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Density in [kg/m³].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        # Validate input state
        state = LiquidAlloyBinaryTpxaState(T=T, p=p, x=x, a={})

        # Identify the system from the input composition
        input_components = sorted(state.x.keys())
        system_key = "-".join(input_components)

        if system_key not in self.system_data:
            raise ValueError(
                f"System '{system_key}' is not supported by this model. Supported systems: {', '.join(self.system_data.keys())}"
            )

        system_compositions = self.system_data[system_key]

        # Determine which component's fraction to use for lookup/interpolation
        component_for_lookup = input_components[1]
        input_fraction = state.x[component_for_lookup]

        available_fractions = sorted(system_compositions.keys())
        c1_final, c2_final, T_liquidus_final = 0.0, 0.0, 0.0

        # Case 1: Exact composition match found in data
        if input_fraction in available_fractions:
            formula: str = system_compositions[input_fraction]
            if not (self.T_min[formula] <= T <= self.T_max[formula]):
                raise ValueError(
                    f"Temperature {T} K is outside the recommended range ({self.T_min[formula]}-{self.T_max[formula]} K) for {formula}."
                )
            c1_final = self.c1[formula]
            c2_final = self.c2[formula]
            T_liquidus_final = self.T_liquidus[formula]

        # Case 2: Composition requires interpolation
        else:
            if not (available_fractions[0] <= input_fraction <= available_fractions[-1]):
                raise ValueError(
                    f"Composition {component_for_lookup}={input_fraction:.3f} is outside the available range for this system ({available_fractions[0]:.3f} to {available_fractions[-1]:.3f})."
                )

            # Find bracketing compositions for interpolation
            frac_lower, frac_upper = -1.0, -1.0
            for i in range(len(available_fractions) - 1):
                if available_fractions[i] < input_fraction < available_fractions[i + 1]:
                    frac_lower, frac_upper = available_fractions[i], available_fractions[i + 1]
                    break

            formula_lower = system_compositions[frac_lower]
            formula_upper = system_compositions[frac_upper]

            # Check temperature warnings for both bracketing points
            T_min_lower = self.T_min[formula_lower]
            T_max_lower = self.T_max[formula_lower]
            T_min_upper = self.T_min[formula_upper]
            T_max_upper = self.T_max[formula_upper]

            if not (T_min_lower <= T <= T_max_lower) or not (T_min_upper <= T <= T_max_upper):
                raise ValueError(
                    f"Temperature {T} K is outside the recommended range {T_min_lower}-{T_max_lower} K for {formula_lower} and {T_min_upper}-{T_max_upper} K for {formula_upper}. Cannot perform interpolation."
                )

            # Linear interpolation
            interp_factor = (input_fraction - frac_lower) / (frac_upper - frac_lower)

            c1_final = self.c1[formula_lower] + interp_factor * (self.c1[formula_upper] - self.c1[formula_lower])
            c2_final = self.c2[formula_lower] + interp_factor * (self.c2[formula_upper] - self.c2[formula_lower])
            T_liquidus_final = self.T_liquidus[formula_lower] + interp_factor * (
                self.T_liquidus[formula_upper] - self.T_liquidus[formula_lower]
            )

            print(f"Note: Parameters interpolated between {formula_lower} and {formula_upper}.")

        # Final density calculation using either direct or interpolated parameters
        density = c1_final - c2_final * (T - T_liquidus_final)
        return density


EmpiricalBinary.load_data()
