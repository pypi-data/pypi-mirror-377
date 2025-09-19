from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..σ import PolynomialUnary
from ._wf_model import WFModel


class WiedemannFranzUnary(
    WFModel[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid ferrous alloy thermal conductivity model based on applying the Wiedemann-Franz law to electrical conductivity polynomial fits.

    Returns:
       Thermal conductivity in [W/(m.K)].

    References:
        hixson1990, zytveld1980, ono1976, sasaki1995, seydel1977, kita1978, cagran2007
    """

    data: ClassVar[dict[str, dict[str, Any]]] = PolynomialUnary.data
    references: ClassVar[list[strNotEmpty]] = PolynomialUnary.references

    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    degree: int = 1
    ec_polynomial: PolynomialUnary = Field(default_factory=PolynomialUnary)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.ec_polynomial = PolynomialUnary(degree=self.degree)
        self.component_scope = self.ec_polynomial.component_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate unary system thermal conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"Fe":1.0}.
            a: Phase constituent activity dictionary. Not applicable to unary systems.

        Returns:
            Thermal conductivity in [W/(m.K)].
        """
        # get the electrical conductivity
        sigma = self.ec_polynomial.calculate(T=T, p=p, x=x, a=a)

        # apply the Wiedemann-Franz law
        kappa = sigma * self.L_0 * T

        return kappa


WiedemannFranzUnary.load_data()
