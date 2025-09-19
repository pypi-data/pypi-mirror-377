from typing import Self

from pydantic import Field, model_validator

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositive

from ...core.material_state import MaterialState


class LiquidMetalTpxState(MaterialState):
    """
    Temperature and composition state for a material.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : Mole fraction of material components.

    Raises:
    ------
        ValueError: If the temperature is out of range (200 K < T < 5000 K).
        ValueError: If the sum of mole fractions does not equal 1.00
    """

    T: floatPositive
    p: floatPositive
    x: dict[str, floatFraction]
    compounds: listCompoundFormulas = Field(default_factory=list)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        self.compounds = list(self.x.keys())

        if self.T < 200 or self.T > 8000:
            raise ValueError("Temperature should be above 200 K and below 8000 K.")

        total_mole_frac = 0
        for comp in self.x:
            total_mole_frac += self.x[comp]
        if abs(total_mole_frac - 1.00) > 1e-12:
            raise ValueError("Mole fractions should add up to 1.00.")

        return self

    def _init(self):
        return
