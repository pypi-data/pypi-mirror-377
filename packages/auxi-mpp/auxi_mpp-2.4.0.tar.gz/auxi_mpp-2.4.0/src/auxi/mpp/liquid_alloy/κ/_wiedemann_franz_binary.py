from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..σ import PolynomialBinary
from ._wf_model import WFModel


class WiedemannFranzBinary(
    WFModel[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid ferrous alloy thermal conductivity model based on applying the Wiedemann-Franz law to electrical conductivity polynomial fits.

    Returns:
       Thermal conductivity in [W/(m.K)].

    References:
        ono1976, hixson1990, zytveld1980, baum1971, ono1972, kita1984, chikova2021, seydel1977, kita1978, cagran2007, sasaki1995
    """

    data: ClassVar[dict[str, dict[str, Any]]] = PolynomialBinary.data
    references: ClassVar[list[strNotEmpty]] = PolynomialBinary.references

    component_scope: list[strCompoundFormula] = Field(default_factory=list)
    degree: int = 2
    ec_polynomial: PolynomialBinary = Field(default_factory=PolynomialBinary)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.ec_polynomial = PolynomialBinary(degree=self.degree)
        self.component_scope = self.ec_polynomial.component_scope

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system thermal conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"Fe":0.9, "C": 0.1}.
            a: Phase constituent activity dictionary. Not applicable to liquid alloys.

        Returns:
            Thermal conductivity in [W/(m.K)].
        """
        # get the electrical conductivity
        sigma = self.ec_polynomial.calculate(T=T, p=p, x=x, a=a)

        # apply the Wiedemann-Franz law
        kappa = sigma * self.L_0 * T

        return kappa
