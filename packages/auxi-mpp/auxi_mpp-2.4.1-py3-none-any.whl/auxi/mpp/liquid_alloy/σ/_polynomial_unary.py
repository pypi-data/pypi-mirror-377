from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ...core.material_state._tpx_state import TpxState
from ._model import Model


class PolynomialUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid metal electrical conductivity polynomial fit to experimental data.

    Returns:
       Electrical conductivity in [S/m].

    References:
        hixson1990, zytveld1980, ono1976, sasaki1995, seydel1977, kita1978, cagran2007
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = [
        "hixson1990",
        "zytveld1980",
        "ono1976",
        "sasaki1995",
        "seydel1977",
        "kita1978",
        "cagran2007",
    ]
    component_scope: list[strCompoundFormula] = Field(default_factory=list)

    degree: int = 1

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        available_degrees = [1, 2]
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
        Calculate unary system electrical conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"Fe":1.0}.
            a: Phase constituent activity dictionary. Not applicable to unary systems.

        Returns:
            Electrical conductivity in [S/m].
        """
        if a != {}:
            raise ValueError("Specifying activities is not applicable to liquid alloys.")

        # validate input
        state = TpxState(T=T, p=p, x=x)

        # test for components scope
        for c in state.x:
            if c not in self.component_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.component_scope)}'.")

        # load the polynomial coefficients
        data = PolynomialUnary.data
        x_comp = list(state.x.keys())
        x_comp = x_comp[0]
        poly_data = data[x_comp]["fits"][self.degree]["param"]

        # calculate resistivity
        rho_micro_ohm_cm = poly_data["constant"] + poly_data["T"] * state.T
        if self.degree > 1:
            rho_micro_ohm_cm += poly_data.get("T^2", 0) * state.T**2

        # convert resistivity in µΩcm to conductivity in S/m
        sigma = 1e8 / rho_micro_ohm_cm

        return sigma


PolynomialUnary.load_data()
