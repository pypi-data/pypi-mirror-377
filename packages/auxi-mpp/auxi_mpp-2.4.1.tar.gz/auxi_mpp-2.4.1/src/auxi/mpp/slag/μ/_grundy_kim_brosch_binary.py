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


class GrundyKimBroschBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary silicate slag dynamic viscosity model by Grundy, Kim, and Brosch.

    Args:
        esf : Equilibrium slag function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of equilibrium slag composition as well as a dictionary of bond fractions. Eg. def my_esf(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]: ...

    Returns:
       Dynamic viscosity in [Pa.s].

    References:
        grundy2008-part1, grundy2008-part2, kim2012-part3
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["grundy2008-part1", "grundy2008-part2", "kim2012-part3"]

    # backward-compatible function finder for binary systems
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]] | None = None

    esf: (
        Callable[
            [float, float, dict[str, float], dict[str, dict[str, float]]], tuple[dict[str, float], dict[str, float]]
        ]
        | None
    ) = None

    names: dict[str, str] = Field(default_factory=dict)
    structural_x: dict[str, float] = Field(default_factory=dict)
    cation: dict[str, str] = Field(default_factory=dict)
    struc_unit: dict[str, str] = Field(default_factory=dict)
    struc_ox_count: dict[str, float] = Field(default_factory=dict)
    cation_count: dict[str, int] = Field(default_factory=dict)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
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

        data = GrundyKimBroschBinary.data
        self.compound_scope = list(self.data.keys())

        self.cation: dict[str, str] = {c: data[c]["cation"] for c in self.compound_scope}
        self.cation_count: dict[str, int] = {c: data[c]["cation_count"] for c in self.compound_scope}
        self.struc_unit: dict[str, str] = {c: data[c]["struc_unit"] for c in self.compound_scope}
        self.struc_ox_count: dict[str, float] = {c: data[c]["struc_ox_count"] for c in self.compound_scope}
        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}
        self.names: dict[str, str] = {data[c]["struc_unit"]: c for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.5}.
            a: Phase constituent activity dictionary. Not applicable to binary systems.

        Returns:
            Viscosity in [Pa.s].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        data = GrundyKimBroschBinary.data

        # validate input
        state = SilicateBinarySlagEquilibriumTpxState(T=T, p=p, x=x)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # convert input composition to structural unit fractions
        x_struc: dict[str, float] = {}
        for comp in state.x:
            x_struc[data[comp]["struc_unit"]] = data[comp]["cation_count"] * state.x[comp]

        x_struc_unit = self._normalise_fractions(x_struc)

        # eqn 2 to 3
        p_SiSi = self._probability_SiSi(state, x_struc_unit)

        # eqn 18 a
        A_parameter = self._calculate_A_parameter(x_struc_unit, p_SiSi, state)

        # eqn 18 b
        E_parameter = self._calculate_E_parameter(x_struc_unit, p_SiSi, state)

        # eqn 10
        mu = math.exp(A_parameter + E_parameter / (R * state.T))

        self.structural_x = x_struc_unit

        return mu

    def _normalise_fractions(self, dict_in: dict[str, float]) -> dict[str, float]:
        x_sum: float = sum(dict_in[comp] for comp in dict_in)
        normalised_dict: dict[str, float] = {}
        for key, value in dict_in.items():
            normalised_dict[key] = value / x_sum
        return normalised_dict

    def _count_oxygens(self, x_comps: dict[str, float]):
        n_tot_oxygen: float = 0.0
        for comp, value in x_comps.items():
            n_tot_oxygen += self.struc_ox_count[self.names[comp]] * value
        return n_tot_oxygen

    # eqn 2 to 3
    def _probability_SiSi(self, state: SilicateBinarySlagEquilibriumTpxState, x_comps: dict[str, float]) -> float:
        if x_comps["SiO2"] != 0.0:
            assert self.esf is not None, "Equilibrium solver function 'esf' was not initialized."
            _, x_b = self.esf(state.T, state.p, state.x, {})
            p_SiSi: float = (x_b["Si-Si"] * self._count_oxygens(x_comps)) / (2 * x_comps["SiO2"])
        else:
            p_SiSi = 0.0
        return p_SiSi

    def _calculate_A_parameter(
        self, x_comp: dict[str, float], p_SiSi: float, state: SilicateBinarySlagEquilibriumTpxState
    ) -> float:
        data = GrundyKimBroschBinary.data

        MOx = state.compound
        MOx_struc = data[MOx]["struc_unit"]

        A_MOx = self.parameters[MOx]["A"]
        A_SiO2_star = self.parameters["SiO2"]["A_*"]
        A_SiO2_E = self.parameters["SiO2"]["A_E"]
        A_M_Si = self.parameters[MOx]["A_M_Si"]
        A_M_Si_R = self.parameters[MOx]["A_M_Si_R"]

        # eqn 18 a
        A_param = A_MOx * x_comp[MOx_struc] + x_comp["SiO2"] * (
            A_SiO2_star + A_SiO2_E * p_SiSi**40 + A_M_Si * x_comp[MOx_struc] + A_M_Si_R * (p_SiSi**4 - p_SiSi**40)
        )

        return A_param

    def _calculate_E_parameter(
        self, x_comp: dict[str, float], p_SiSi: float, state: SilicateBinarySlagEquilibriumTpxState
    ) -> float:
        data = GrundyKimBroschBinary.data

        MOx = state.compound
        MOx_struc = data[MOx]["struc_unit"]

        E_MOx = self.parameters[MOx]["E"]
        E_SiO2_star = self.parameters["SiO2"]["E_*"]
        E_SiO2_E = self.parameters["SiO2"]["E_E"]
        E_M_Si = self.parameters[MOx]["E_M_Si"]
        E_M_Si_R = self.parameters[MOx]["E_M_Si_R"]

        # eqn 18 b
        E_param = E_MOx * x_comp[MOx_struc] + x_comp["SiO2"] * (
            E_SiO2_star + E_SiO2_E * p_SiSi**40 + E_M_Si * x_comp[MOx_struc] + E_M_Si_R * (p_SiSi**4 - p_SiSi**40)
        )

        return E_param


GrundyKimBroschBinary.load_data()
