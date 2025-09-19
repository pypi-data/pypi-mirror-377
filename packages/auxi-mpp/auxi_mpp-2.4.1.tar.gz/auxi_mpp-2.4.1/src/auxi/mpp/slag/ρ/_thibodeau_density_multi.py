import warnings
from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateSlagEquilibriumTpxaState
from ..Vm import ThibodeauMulti
from ._model import Model


class ThibodeauDensityMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component silicate melt density model derived from Thibodeau's molar volume model.

    Args:
        esf : Equilibrium slag function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of equilibrium slag composition as well as a dictionary of bond fractions. Eg. def my_esf(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]: ...

    Returns:
       Density in [kg/m³].

    References:
        thibodeau2016-part2, thibodeau2016-part3
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-part2", "thibodeau2016-part3"]

    # backward-compatible function finder for binary systems
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]] | None = None

    esf: (
        Callable[
            [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
        ]
        | None
    ) = None
    molar_mass: dict[str, float] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

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

        data = ThibodeauDensityMulti.data

        self.compound_scope: list[strCompoundFormula] = [c for c in list(data.keys())]
        self.molar_mass: dict[str, float] = {c: data[c]["molar mass"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.3, "FeO": 0.2}.
            a: Phase constituent activity dictionary. Eg. {"gas_ideal": {"O2": 0.21}}. Phase and constituent name depends on how the user set up the equilibrium slag function.

        Returns:
            Density in [kg/m³].
        """
        # validate input
        state = SilicateSlagEquilibriumTpxaState(T=T, p=p, x=x, a=a)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        molar_volume_model = ThibodeauMulti(esf=self.esf)
        Vm = molar_volume_model.calculate(T=state.T, p=state.p, x=state.x, a=state.a)

        # calculate composition specific molar mass of the system
        weighted_molar_masses: float = float(sum([self.molar_mass[comp] * (state.x[comp]) for comp in state.x]))

        # scale to units of kg/m-3
        ρ = (weighted_molar_masses / Vm) * 1e-3

        return ρ


ThibodeauDensityMulti.load_data()
