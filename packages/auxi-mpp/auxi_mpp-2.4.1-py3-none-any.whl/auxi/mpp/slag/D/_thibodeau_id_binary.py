import math
import warnings
from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import R
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateBinarySlagEquilibriumTpxState
from ._model import Model


class ThibodeauIDBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid silicate slag ionic diffusivity model by Thibodeau.

    Args:
        esf : Equilibrium slag function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of equilibrium slag composition as well as a dictionary of bond fractions. Eg. def my_esf(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]: ...

    Returns:
       Dictionary containing the diffusivity of each cation in units of [m²/s].

    References:
        thibodeau2016-ec
    """

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-ec", "thibodeau2016-ec-disseration"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    # backward-compatible function finder for binary systems
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]] | None = None

    esf: (
        Callable[
            [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
        ]
        | None
    ) = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        # handle backward compatibility for the equilibrium solver function
        if self.esf and self.bff:
            raise ValueError("Cannot provide both 'esf' and 'bff'.")

        if self.bff:
            warnings.warn(
                "'bff' is deprecated and will be removed in a future version. Please use 'esf' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            bff_callable = self.bff
            self.esf = lambda T, p, x, a: ({}, bff_callable(T, p, x, a))

        elif not self.esf:
            raise ValueError("Please provide either 'esf' or 'bff'.")

        data = ThibodeauIDBinary.data
        self.compound_scope = list(data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> dict[str, float]:
        """
        Calculate binary system ionic diffusivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.5}.
            a: Phase constituent activity dictionary. Not applicable to binary systems.

        Returns:
            Ionic diffusivity dictionary [m²/s].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        data = ThibodeauIDBinary.data

        # validate input
        state = SilicateBinarySlagEquilibriumTpxState(T=T, p=p, x=x)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # load A, B and C parameters for specified components
        A_params = {c: data[c]["param"]["A"] for c in state.x}
        B_params = {c: data[c]["param"]["B"] for c in state.x}
        C_params = {c: data[c]["param"]["C"] for c in state.x}

        # get SiSi, SiAl and AlAl bond fractions
        assert self.esf is not None, "Equilibrium solver function 'esf' was not initialized."
        _, x_b = self.esf(state.T, state.p, state.x, {})

        # assign zero for Al interactions if Al2O3 not present
        if "Al-Si" not in x_b:
            x_b["Al-Si"] = 0.0
            x_b["Al-Al"] = 0.0

        D_comps: dict[str, float] = {}

        # equation 7 - calculate diffusivity for each cation
        for comp in state.x:
            D_i = A_params[comp] * math.exp(
                -(
                    float(B_params[comp])
                    + (
                        float(C_params[comp]["C_SiSi"]) * float(x_b["Si-Si"])
                        + float(C_params[comp]["C_AlSi"]) * float(x_b["Al-Si"])
                        + float(C_params[comp]["C_AlAl"]) * float(x_b["Al-Al"])
                    )
                )
                / (R * state.T)
            )

            D_comps[comp] = D_i

        return D_comps


ThibodeauIDBinary.load_data()
