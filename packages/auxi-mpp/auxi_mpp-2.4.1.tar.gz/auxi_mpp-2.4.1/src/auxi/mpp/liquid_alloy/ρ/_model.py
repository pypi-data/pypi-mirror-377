from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._liquid_alloy_property_model import LiquidAlloyPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](LiquidAlloyPropertyModel[T, p, x, a]):
    """
    Base class for all liquid alloy density models.

    In all cases, density is calculated in units of [kg/m³].
    """

    property: strNotEmpty = "Density"
    symbol: strNotEmpty = "ρ"
    display_symbol: strNotEmpty = "\\rho"
    units: strNotEmpty = "\\kilo\\gram\\per\\cubic\\meter"
