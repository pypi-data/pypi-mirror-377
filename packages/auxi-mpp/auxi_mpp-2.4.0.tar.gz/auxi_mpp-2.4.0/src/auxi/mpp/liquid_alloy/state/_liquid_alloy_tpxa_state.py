from typing import Any, Self

from pydantic import Field, model_validator

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositiveOrZero

from ...core.material_state import MaterialState


class LiquidAlloyTpxaState(MaterialState):
    """
    Generate a temperature and composition state for a ferrous liquid alloy.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : Mole fraction of liquid alloy components.
        a : Phase constituent activities.

    Raises:
    ------
        ValueError: If the temperature is out of range (1000 K < T < 2500 K).
        ValueError: If less than three components are provided.
        ValueError: If the sum of mole fractions does not equal 1.00.
    """

    T: floatPositiveOrZero
    p: floatPositiveOrZero
    x: dict[str, floatFraction]
    a: dict[str, dict[str, float]]
    compounds: listCompoundFormulas = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        self.compounds: list[str] = list(self.x.keys())

        if self.T < 800 or self.T > 2500:
            raise ValueError("Temperature should be above 1000 K and below 2500 K.")

        if len(self.x) < 3:
            raise ValueError("For a multi-component model, three or more components should be provided.")

        total_mole_frac = 0
        for comp in self.x:
            total_mole_frac += self.x[comp]

        if abs(total_mole_frac - 1.00) > 1e-9:
            raise ValueError("Mole fractions should add up to 1.00.")

        return self

    def _init(self):
        return
