import re
from re import Pattern
from typing import Any, ClassVar

import numpy as np
from pydantic import Field
from scipy.spatial import Delaunay

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._liquid_alloy_tpxa_state import LiquidAlloyTpxaState
from ._model import Model


class EmpiricalMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component liquid alloy density model.

    Returns:
       Density in [kg/m³].

    References:
        brillo2006, brillo2016, kobatake2013
    """

    # TODO: create dedicated file for all constants used in auxi-mpp
    COMPOUND_PATTERN: Pattern[str] = re.compile(r"([A-Z][a-z]?)(\d+\.?\d*)")
    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["brillo2006, brillo2016, kobatake2013"]

    T_min: dict[str, float] = Field(default_factory=dict)
    T_max: dict[str, float] = Field(default_factory=dict)
    c1: dict[str, float] = Field(default_factory=dict)
    c2: dict[str, float] = Field(default_factory=dict)
    T_liquidus: dict[str, float] = Field(default_factory=dict)

    compound_scope: list[strNotEmpty] = Field(default_factory=list)
    system_scope: list[strNotEmpty] = Field(default_factory=list)
    system_data: dict[str, dict[tuple[float, float], str]] = Field(default_factory=dict)
    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = EmpiricalMulti.data
        self.compound_scope = list(data.keys())

        # Load parameters for each compound
        self.T_min = {c: data[c]["T_range_K"]["min"] for c in self.compound_scope}
        self.T_max = {c: data[c]["T_range_K"]["max"] for c in self.compound_scope}
        self.c1 = {c: data[c]["parameters"]["c1_kg_m3"] for c in self.compound_scope}
        self.c2 = {c: data[c]["parameters"]["c2_kg_m3_K"] for c in self.compound_scope}
        self.T_liquidus = {c: data[c]["parameters"]["T_liquidus_K"] for c in self.compound_scope}

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
        # Regular expression to parse chemical formulas (e.g., "Ag1Al1Cu1")

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

        self.component_scope = sorted(list(unique_components))
        # For each system, create a mapping from 2D composition tuples to formulas
        for components_tuple, formulas in systems.items():
            system_key = "-".join(components_tuple)
            self.system_scope.append(system_key)
            self.system_data[system_key] = {}

            # The first two components in the sorted tuple define the 2D coordinate system
            elem_x, elem_y = components_tuple[1], components_tuple[2]

            for formula in formulas:
                matches = re.findall(self.COMPOUND_PATTERN, formula)
                composition = {elem: float(val) for elem, val in matches}
                total = sum(composition.values())

                # Normalize to mole fractions
                frac_x = composition.get(elem_x, 0.0) / total
                frac_y = composition.get(elem_y, 0.0) / total

                self.system_data[system_key][(frac_x, frac_y)] = formula

    def _calculate_barycentric_weights(self, point: np.ndarray, triangle_vertices: np.ndarray) -> np.ndarray:
        """
        Calculate the barycentric weights of a point within a triangle.

        These weights are used for 2D interpolation.
        """
        # Using a matrix approach to solve for the weights (w1, w2, w3)
        T = np.vstack((triangle_vertices.T, np.ones(3)))
        p = np.append(point, 1)
        weights = np.linalg.solve(T, p)

        return weights

    def _get_composition_coordinates(self, state: "LiquidAlloyTpxaState", components: list[str]) -> tuple[float, float]:
        """Define the 2D coordinate system and returns the composition tuple."""
        # For a ternary system, we use the concentrations of the 2nd and 3rd
        # components (alphabetically sorted) as the coordinates.
        elem_x, elem_y = components[1], components[2]
        return (state.x[elem_x], state.x[elem_y])

    def _get_params_for_exact_match(
        self, T: float, composition_tuple: tuple[float, float], system_compositions: dict[tuple[float, float], str]
    ) -> tuple[float, float, float]:
        """Retrieve model parameters for an exact composition match."""
        formula: str = system_compositions[composition_tuple]
        if not (self.T_min[formula] <= T <= self.T_max[formula]):
            raise ValueError(
                f"Temperature {T} K is outside the recommended range "
                f"({self.T_min[formula]}-{self.T_max[formula]} K) for {formula}."
            )
        c1 = self.c1[formula]
        c2 = self.c2[formula]
        T_liquidus = self.T_liquidus[formula]
        return c1, c2, T_liquidus

    def _interpolate_params(
        self, composition_tuple: tuple[float, float], system_compositions: dict[tuple[float, float], str]
    ) -> tuple[float, float, float]:
        """Interpolates model parameters for a given composition."""
        available_points = np.array(list(system_compositions.keys()))
        triangulation = Delaunay(available_points, qhull_options="QJ")

        simplex_index = triangulation.find_simplex(composition_tuple)
        if simplex_index == -1:
            raise ValueError(
                f"Composition {composition_tuple} is outside the convex hull of available data for this system."
            )

        # Get vertices and corresponding formulas of the enclosing triangle
        triangle_indices = triangulation.simplices[simplex_index]
        triangle_vertices = available_points[triangle_indices]
        formulas = [system_compositions[tuple(v)] for v in triangle_vertices]

        # Calculate barycentric weights for interpolation
        weights = self._calculate_barycentric_weights(np.array(composition_tuple), triangle_vertices)

        # Interpolate each parameter
        c1_interp = np.dot(weights, [self.c1[f] for f in formulas])
        c2_interp = np.dot(weights, [self.c2[f] for f in formulas])
        T_liquidus_interp = np.dot(weights, [self.T_liquidus[f] for f in formulas])

        return c1_interp, c2_interp, T_liquidus_interp

    def _calculate_final_density(self, T: float, c1: float, c2: float, T_liquidus: float) -> float:
        """Calculate density using the final model parameters."""
        return c1 - c2 * (T - T_liquidus)

    def calculate(
        self,
        T: float = 298.15,
        p: float = 101325,
        x: dict[str, float] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] E.g., {"Ag": 0.1, "Al": 0.6, "Cu": 0.3}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Density in [kg/m³].
        """
        if a:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        # 1. Validate input state
        state = LiquidAlloyTpxaState(T=T, p=p, x=x, a={})

        # 2. Identify the system and retrieve its data
        input_components = sorted(state.x.keys())
        system_key = "-".join(input_components)

        if system_key not in self.system_data:
            raise ValueError(
                f"System '{system_key}' is not supported by this model. Supported systems: {', '.join(self.system_data.keys())}"
            )

        system_compositions = self.system_data[system_key]

        # Define the 2D coordinate system based on the sorted components
        elem_x, elem_y = input_components[1], input_components[2]
        composition_tuple = (state.x[elem_x], state.x[elem_y])

        # 3. Get model parameters either directly or via interpolation
        if composition_tuple in system_compositions:
            c1, c2, T_liquidus = self._get_params_for_exact_match(T, composition_tuple, system_compositions)
        else:
            c1, c2, T_liquidus = self._interpolate_params(composition_tuple, system_compositions)

        # 4. Calculate the final density with the determined parameters
        return self._calculate_final_density(T, c1, c2, T_liquidus)


EmpiricalMulti.load_data()
