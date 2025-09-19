from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._liquid_alloy_property_model import LiquidAlloyPropertyModel


class WFModel[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](LiquidAlloyPropertyModel[T, p, x, a]):
    """
    Base class for all liquid alloy thermal conductivity models based on the Wiedemann-Franz law.

    In all cases, thermal conductivity is calculated in units of [W/(m.K)].
    """

    property: strNotEmpty = "Thermal Conductivity"
    symbol: strNotEmpty = "κ"
    display_symbol: strNotEmpty = "\\kappa"
    units: strNotEmpty = "\\watt\\per\\meter\\per\\kelvin"
    L_0: float = 2.445e-8
