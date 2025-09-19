import warnings
from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import F, R
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..D import ThibodeauIDBinary
from ..state import SilicateBinarySlagEquilibriumTpxState
from ..Vm import ThibodeauBinary
from ._model import Model


class ThibodeauECBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary silicate liquid oxide electrical conductivity model by Thibodeau.

    Args:
        esf : Equilibrium slag function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of equilibrium slag composition as well as a dictionary of bond fractions. Eg. def my_esf(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]: ...

    Returns:
       Electrical conductivity in [S/m].

    References:
        thibodeau2016-ec
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-ec", "thibodeau2016-dissertation"]
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

        self.compound_scope = list(self.data.keys())

    def _get_Fe_fractions(self, x_slg_comp: dict[str, float]) -> tuple[float, float]:
        # get Fe2+ fraction
        Fe2plus = x_slg_comp.get("FeO", 0) / (x_slg_comp.get("FeO", 0) + 2 * x_slg_comp.get("Fe2O3", 0))

        # get Fe3+ fraction
        Fe3plus = 2 * x_slg_comp.get("Fe2O3", 0) / (x_slg_comp.get("FeO", 0) + 2 * x_slg_comp.get("Fe2O3", 0))

        return Fe2plus, Fe3plus

    def _get_total_iron_per_mole(self, x: dict[str, float]):
        # get actual iron amount
        Fe_count = 2 * x.get("Fe2O3", 0) + x.get("FeO", 0)
        return Fe_count

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

        # validate input
        state = SilicateBinarySlagEquilibriumTpxState(T=T, p=p, x=x)

        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        data = ThibodeauECBinary.data

        # ionic conduction contribution
        # calculate the molar volume
        melt_Vm_object = ThibodeauBinary(esf=self.esf)
        Vm = melt_Vm_object.calculate(T=state.T, p=state.p, x=state.x, a={})

        # convert to m^3/mol to cm^3/mol
        Vm = Vm / 1e-6

        # eqn 7 - calculate diffusivity for each cation
        D_dict: dict[str, float] = ThibodeauIDBinary(esf=self.esf).calculate(T=state.T, p=state.p, x=state.x, a={})

        # eqn 8 - sum of all cation contributions to electrical conductivity
        sigma_ionic: float = 0.0
        for comp in state.x:
            sigma_ionic += (
                100
                * ((data[comp]["z"] ** 2 * F**2) * (data[comp]["num_cats"] * state.x[comp]) * D_dict[comp])
                / ((R * state.T) * Vm)
            )

        # electronic conduction contribution
        sigma_electronic: float = 0.0

        if ("FeO" in x and x["FeO"] > 0.0) or ("Fe2O3" in x and x["Fe2O3"] > 0.0):
            # calculate the total Fe concentration
            total_iron_per_mole = self._get_total_iron_per_mole(x=x)

            total_Fe_concentration: float = total_iron_per_mole / Vm

            # calculate Fe2+ and Fe3+ fractions
            FeII, FeIII = self._get_Fe_fractions(x)

            # eqn 29 dissertation - calculate electronic contribution
            sigma_electronic += (4e14 / state.T) * D_dict.get("FeO", 0) * total_Fe_concentration**2 * FeII * FeIII

        sigma: float = sigma_ionic + sigma_electronic

        return sigma


ThibodeauECBinary.load_data()
