from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._ferrous_liquid_alloy_tpxa_state import FerrousLiquidAlloyTpxaState
from ._model import Model


class PolynomialMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component liquid ferrous alloy electrical conductivity polynomial fit to experimental data.

    Returns:
       Electrical conductivity in [S/m].

    References:
        ono1976, sasaki1995, hixson1990, zytveld1980
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["ono1976", "sasaki1995", "hixson1990", "zytveld1980"]
    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    degree: int = 2

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        available_degrees = [2, 3, 4]
        if self.degree not in available_degrees:
            raise ValueError(
                f"A degree = {self.degree} polynomial is not available. Available ones are {available_degrees}."
            )

        unique_keys: set[str] = set()
        keys = list(self.data.keys())
        for key in keys:
            split_keys = key.split("-")
            for split_key in split_keys:
                unique_keys.add(split_key)
        self.component_scope = list(unique_keys)

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system electrical conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"Fe":0.85, "C": 0.1, "Si": 0.05}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Electrical conductivity in [S/m].
        """
        if a != {}:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        # validate input
        state = FerrousLiquidAlloyTpxaState(T=T, p=p, x=x, a={})

        # test for components scope
        for c in state.x:
            if c not in self.component_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.component_scope)}'.")

        # load the polynomial coefficients
        data = PolynomialMulti.data
        x_comps = "-".join(state.non_fe_components)
        poly_data = data[x_comps]["fits"][self.degree]["param"]

        # load non-fe components
        x_comp1, x_comp2 = state.non_fe_components[0], state.non_fe_components[1]

        # calculate resistivity
        rho_micro_ohm_cm = (
            # constant and linear terms
            poly_data["constant"]
            + poly_data["T"] * state.T
            + poly_data[f"x_{x_comp1}"] * state.x[x_comp1]
            + poly_data[f"x_{x_comp2}"] * state.x[x_comp2]
            # quadratic terms (sum of exponents = 2)
            + poly_data["T^2"] * state.T**2
            + poly_data[f"Tx_{x_comp1}"] * state.T * state.x[x_comp1]
            + poly_data[f"Tx_{x_comp2}"] * state.T * state.x[x_comp2]
            + poly_data[f"x_{x_comp1}^2"] * state.x[x_comp1] ** 2
            + poly_data[f"x_{x_comp2}^2"] * state.x[x_comp2] ** 2
            + poly_data[f"x_{x_comp1}x_{x_comp2}"] * state.x[x_comp1] * state.x[x_comp2]
        )
        # cubic terms (sum of exponents = 3)
        if self.degree > 2:
            rho_micro_ohm_cm += (
                poly_data["T^3"] * state.T**3
                + poly_data[f"T^2x_{x_comp1}"] * state.T**2 * state.x[x_comp1]
                + poly_data[f"T^2x_{x_comp2}"] * state.T**2 * state.x[x_comp2]
                + poly_data[f"Tx_{x_comp1}^2"] * state.T * state.x[x_comp1] ** 2
                + poly_data[f"Tx_{x_comp2}^2"] * state.T * state.x[x_comp2] ** 2
                + poly_data[f"Tx_{x_comp1}x_{x_comp2}"] * state.T * state.x[x_comp1] * state.x[x_comp2]
                + poly_data[f"x_{x_comp1}^3"] * state.x[x_comp1] ** 3
                + poly_data[f"x_{x_comp2}^3"] * state.x[x_comp2] ** 3
                + poly_data[f"x_{x_comp1}^2x_{x_comp2}"] * state.x[x_comp1] ** 2 * state.x[x_comp2]
                + poly_data[f"x_{x_comp1}x_{x_comp2}^2"] * state.x[x_comp1] * state.x[x_comp2] ** 2
            )
        # quartic terms (sum of exponents = 4)
        if self.degree > 3:
            rho_micro_ohm_cm += (
                poly_data["T^4"] * state.T**4
                + poly_data[f"T^3x_{x_comp1}"] * state.T**3 * state.x[x_comp1]
                + poly_data[f"T^3x_{x_comp2}"] * state.T**3 * state.x[x_comp2]
                + poly_data[f"T^2x_{x_comp1}^2"] * state.T**2 * state.x[x_comp1] ** 2
                + poly_data[f"T^2x_{x_comp2}^2"] * state.T**2 * state.x[x_comp2] ** 2
                + poly_data[f"T^2x_{x_comp1}x_{x_comp2}"] * state.T**2 * state.x[x_comp1] * state.x[x_comp2]
                + poly_data[f"Tx_{x_comp1}^3"] * state.T * state.x[x_comp1] ** 3
                + poly_data[f"Tx_{x_comp2}^3"] * state.T * state.x[x_comp2] ** 3
                + poly_data[f"Tx_{x_comp1}^2x_{x_comp2}"] * state.T * state.x[x_comp1] ** 2 * state.x[x_comp2]
                + poly_data[f"Tx_{x_comp1}x_{x_comp2}^2"] * state.T * state.x[x_comp1] * state.x[x_comp2] ** 2
                + poly_data[f"x_{x_comp1}^4"] * state.x[x_comp1] ** 4
                + poly_data[f"x_{x_comp2}^4"] * state.x[x_comp2] ** 4
                + poly_data[f"x_{x_comp1}^3x_{x_comp2}"] * state.x[x_comp1] ** 3 * state.x[x_comp2]
                + poly_data[f"x_{x_comp1}^2x_{x_comp2}^2"] * state.x[x_comp1] ** 2 * state.x[x_comp2] ** 2
                + poly_data[f"x_{x_comp1}x_{x_comp2}^3"] * state.x[x_comp1] * state.x[x_comp2] ** 3
            )

        # convert resistivity in µΩcm to conductivity in S/m
        sigma = 1e8 / rho_micro_ohm_cm

        return sigma


PolynomialMulti.load_data()
