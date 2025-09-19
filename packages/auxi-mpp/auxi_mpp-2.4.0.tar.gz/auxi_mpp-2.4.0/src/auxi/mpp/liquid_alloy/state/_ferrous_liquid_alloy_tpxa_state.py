from typing import Any, Self

from pydantic import Field, model_validator

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositiveOrZero

from ...core.material_state import MaterialState


class FerrousLiquidAlloyTpxaState(MaterialState):
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
        ValueError: If Fe is not one of the compounds.
    """

    T: floatPositiveOrZero
    p: floatPositiveOrZero
    x: dict[str, floatFraction]
    a: dict[str, dict[str, float]]
    non_fe_components: listCompoundFormulas = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        components: set[str] = set(self.x.keys())

        if "Fe" not in components:
            raise ValueError("Fe must be one of the components.")

        if len(components) <= 2:
            raise ValueError("Three or more components must be specified.")

        if self.T < 1000 or self.T > 2500:
            raise ValueError("Temperature should be above 1000 K and below 2500 K.")

        total_mole_frac = 0
        for comp in self.x:
            total_mole_frac += self.x[comp]

        if abs(total_mole_frac - 1.00) > 1e-9:
            raise ValueError("Mole fractions should add up to 1.00.")

        components.remove("Fe")
        self.non_fe_components = sorted(list(components))

        return self

    def _init(self):
        return
