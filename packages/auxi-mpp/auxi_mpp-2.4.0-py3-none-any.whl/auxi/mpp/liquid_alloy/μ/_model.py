from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from .._liquid_alloy_property_model import LiquidAlloyPropertyModel


class Model[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](LiquidAlloyPropertyModel[T, p, x, a]):
    """
    Base class for all liquid alloy viscosity models.

    In all cases, viscosity is calculated in units of [Pa.s].
    """

    property: strNotEmpty = "Dynamic Viscosity"
    symbol: strNotEmpty = "μ"
    display_symbol: strNotEmpty = "\\mu"
    units: strNotEmpty = "\\pascal\\second"
