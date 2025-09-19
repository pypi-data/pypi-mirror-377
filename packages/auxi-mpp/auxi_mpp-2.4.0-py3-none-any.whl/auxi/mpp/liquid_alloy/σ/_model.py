from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._liquid_alloy_property_model import LiquidAlloyPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](LiquidAlloyPropertyModel[T, p, x, a]):
    """
    Base class for all liquid alloy electrical conductivity models.

    In all cases, electrical conductivity is calculated in units of [S/m].
    """

    property: strNotEmpty = "Electrical Conductivity"
    symbol: strNotEmpty = "σ"
    display_symbol: strNotEmpty = "\\sigma"
    units: strNotEmpty = "\\siemens\\per\\meter"
