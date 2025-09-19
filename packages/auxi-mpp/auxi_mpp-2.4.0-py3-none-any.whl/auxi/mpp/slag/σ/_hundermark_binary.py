import math
import warnings
from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateBinarySlagEquilibriumTpxState
from ._model import Model


class HundermarkBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary silicate liquid oxide electrical conductivity model by Hundermark.

    Args:
        esf : Equilibrium slag function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of equilibrium slag composition as well as a dictionary of bond fractions. Eg. def my_esf(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]: ...

    Returns:
       Electrical conductivity in [S/m].

    References:
        hundermark2003-dissertation
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["hundermark2003-dissertation"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    esf: (
        Callable[
            [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
        ]
        | None
    ) = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        # handle backward compatibility for the equilibrium solver function
        if not self.esf:
            warnings.warn(
                "Model instantiation without 'esf' is deprecated and not providing it can cause incorrect estimations. Providing 'esf' will be compulsary in a future version.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.esf = lambda T, p, x, a: (x, {})

        self.compound_scope = list(self.data.keys())

    def _get_total_iron_as_FeO(self, x: dict[str, float], a: dict[str, dict[str, float]]):
        # get actual iron amount
        Fe_count = 2 * x.get("Fe2O3", 0) + x.get("FeO", 0)

        return self._all_Fe_as_FeO_and_normalise(x, Fe_count)

    def _all_Fe_as_FeO_and_normalise(self, x: dict[str, float], Fe_count: float):
        # all Fe as FeO
        x_copy = x.copy()
        x_copy.pop("FeO", None)
        x_copy.pop("Fe2O3", None)
        x_copy["FeO"] = Fe_count

        # normalise
        total = sum(x_copy.values())
        normalised_x_copy = {key: value / total for key, value in x_copy.items()}
        Fe_as_FeO_fraction = normalised_x_copy["FeO"]

        return Fe_as_FeO_fraction

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
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.5}.
            a: Phase constituent activity dictionary. Not applicable to binary systems.

        Returns:
            Electrical conductivity in [S/m].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        # get equilibrium composition
        assert self.esf is not None, "Equilibrium solver function 'esf' was not initialized."
        x_slg_comp, _ = self.esf(T, p, x, a)

        # validate input
        state = SilicateBinarySlagEquilibriumTpxState(T=T, p=p, x=x_slg_comp)

        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        data = HundermarkBinary.data

        # sum of all oxide contributions to electrical conductivity
        ln_sigma: float = 0.0

        # iron is present
        if ("FeO" in x and x["FeO"] > 0.0) or ("Fe2O3" in x and x["Fe2O3"] > 0.0):
            # get total iron as FeO
            x_FeO = self._get_total_iron_as_FeO(x=x, a=a)

            # get Fe2+ fraction
            Fe2plus = state.x.get("FeO", 0) / (state.x.get("FeO", 0) + 2 * state.x.get("Fe2O3", 0))

            # get Fe3+ fraction
            Fe3plus = 2 * state.x.get("Fe2O3", 0) / (state.x.get("FeO", 0) + 2 * state.x.get("Fe2O3", 0))

            # eqn 34
            # non Fe oxides
            for comp in state.x:
                if comp not in {"FeO", "Fe2O3"}:
                    ln_sigma += (data[comp]["param"]["A2"] + (data[comp]["param"]["B2"] / state.T)) * x[comp]

            # FeO part
            ln_sigma += (data["FeO"]["param"]["A2"] + (data["FeO"]["param"]["B2"] / state.T)) * x_FeO * Fe2plus

            # Fe2O3 part
            ln_sigma += (data["Fe2O3"]["param"]["A2"] + (data["Fe2O3"]["param"]["B2"] / state.T)) * x_FeO * Fe3plus

            # FeO & Fe2O3 part
            ln_sigma += (data["FeO"]["param"]["A_eq"] + (data["FeO"]["param"]["B_eq"] / state.T)) * (
                x_FeO * Fe2plus * x_FeO * Fe3plus
            )
        # no iron present
        else:
            # eqn 32
            for comp in state.x:
                if comp in {"FeO", "Fe2O3"}:
                    continue
                else:
                    ln_sigma += (data[comp]["param"]["A1"] + (data[comp]["param"]["B1"] / state.T)) * x[comp]

        sigma: float = 100 * math.exp(ln_sigma)  # S/m

        return sigma


HundermarkBinary.load_data()
