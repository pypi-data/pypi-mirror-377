from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._liquid_alloy_property_model import LiquidAlloyPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](LiquidAlloyPropertyModel[T, p, x, a]):
    """
    Base class for all liquid alloy molar volume models.

    In all cases, molar volume is calculated in units of [m³/mol].
    """

    property: strNotEmpty = "Molar Volume"
    symbol: strNotEmpty = "Vm"
    display_symbol: strNotEmpty = "\\bar{V}"
    units: strNotEmpty = "\\cubic\\meter\\per\\mol"
