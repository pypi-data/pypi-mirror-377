from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state._ferrous_liquid_alloy_binary_tpx_state import FerrousLiquidAlloyBinaryTpxState
from ._model import Model


class PolynomialBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid ferrous alloy electrical conductivity polynomial fit to experimental data.

    Returns:
       Electrical conductivity in [S/m].

    References:
        ono1976, hixson1990, zytveld1980, baum1971, ono1972, kita1984, chikova2021, seydel1977, kita1978, cagran2007, sasaki1995
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = [
        "ono1976",
        "hixson1990",
        "zytveld1980",
        "baum1971",
        "ono1972",
        "kita1984",
        "chikova2021",
        "seydel1977",
        "kita1978",
        "cagran2007",
        "sasaki1995",
    ]
    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    degree: int = 2

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        available_degrees = [1, 2, 3]
        if self.degree not in available_degrees:
            raise ValueError(
                f"A degree = {self.degree} polynomial is not available. Available ones are {available_degrees}."
            )

        self.component_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system electrical conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"Fe":0.9, "C": 0.1}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Electrical conductivity in [S/m].
        """
        if a != {}:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        # validate input
        state = FerrousLiquidAlloyBinaryTpxState(T=T, p=p, x=x)

        # test for components scope
        for c in state.x:
            if c not in self.component_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.component_scope)}'.")

        # load the polynomial coefficients
        data = PolynomialBinary.data
        x_comp = state.non_fe_component
        poly_data = data[x_comp]["fits"][self.degree]["param"]

        # calculate resistivity
        rho_micro_ohm_cm: float = (
            poly_data["constant"] + poly_data["T"] * state.T + poly_data[f"x_{x_comp}"] * state.x[x_comp]
        )
        if self.degree > 1:
            rho_micro_ohm_cm += (
                poly_data["T^2"] * state.T**2
                + poly_data[f"Tx_{x_comp}"] * state.T * state.x[x_comp]
                + poly_data[f"x_{x_comp}^2"] * state.x[x_comp] ** 2
            )
        if self.degree > 2:
            rho_micro_ohm_cm += (
                poly_data["T^3"] * state.T**3
                + poly_data[f"T^2x_{x_comp}"] * state.T**2 * state.x[x_comp]
                + poly_data[f"Tx_{x_comp}^2"] * state.T * state.x[x_comp] ** 2
                + poly_data[f"x_{x_comp}^3"] * state.x[x_comp] ** 3
            )

        # convert resistivity in µΩcm to conductivity in S/m
        sigma = 1e8 / rho_micro_ohm_cm

        return sigma


PolynomialBinary.load_data()
