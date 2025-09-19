.. _building-the-function:

Building the Function
=====================

We now have all the tools to build our own equilibrium slag function that can return the equilibrium slag composition and the bond fractions as two appropriate dictionaries.
The output of our function will have the type ``tuple[dict[str, float], dict[str, float]]``, where the first is the equilibrium slag composition and the last the bond fractions.
In the bond fraction dictionary, the keys follow the naming convention of ``"Si-Mg"`` to reference interactions, for example.

In your python environment where Chemapp for Python is installed, the equilibrium slag function can be set up as shown below.
Note that the esf should have the inputs ``T, p, x, a``, which are temperature, pressure, composition and activities in units of kelvin, pascal, mole fraction and unitless, respectively.
It is recommended to define the esf in a file separate from where physical property calculations will be performed and only import the function where needed.

Note that the user has the freedom to name the phases in the activity dictionary, as long as the ``dict[str, dict[str, float]]`` typing is still followed.
In this example, FactSage’s naming convention for the iron liquid and gas phase were upheld.

::

    import chemapp.basic as ca

    from chemapp.core import PressureUnit, Status, TemperatureUnit

    from chemapp.friendly import EquilibriumCalculation as caec
    from chemapp.friendly import ThermochemicalSystem as cats
    from chemapp.friendly import Units

    import numpy as np


    def my_esf(
        T: float,  # temperature
        p: float,  # pressure
        x: dict[str, float],  # assay_dictionary
        a: dict[str, dict[str, float]],  # activity_dictionary
    ) -> tuple[dict[str, float], dict[str, float]]:
        cats.load("path/to/your.cst")

        Units.set_T_unit(TemperatureUnit.K)
        Units.set_P_unit(PressureUnit.Pa)

        for comp in x:
            caec.set_IA_pc("Slag-liq#1", comp, x[comp])

        if "Fe_liquid(liq)" in a:
            caec.set_IA_pc("Fe_liquid(liq)", "Fe_liquid(liq)", 0.0)
            caec.set_eq_AC_pc("Fe_liquid(liq)", "Fe_liquid(liq)", a["Fe_liquid(liq)"]["Fe"])

        if "gas_ideal" in a:
            caec.set_IA_pc("gas_ideal", "O2", 0.0)
            caec.set_eq_AC_pc("gas_ideal", "O2", a["gas_ideal"]["O2"])

        caec.set_eq_T(T)
        caec.set_eq_P(p)

        cats.set_status_phs(Status.ELIMINATED)
        cats.set_status_ph("Slag-liq#1", Status.ENTERED)

        caec.calculate_eq(print_results=False)

        # extracting equilibrium slag composition
        slg_index: int = ca.tqinp("Slag-liq#1")
        slag_component_mole_amount: list[float] = caec.get_eq_A_pcs_in_ph(slg_index)

        eq_composition: dict[str, float] = {}
        for index, amount in enumerate(slag_component_mole_amount):
            if amount > 1e-9:
                name = ca.tqgnpc(slg_index, index)
                eq_composition[name] = amount

        def normalise(x: dict[str, float]):
            total = sum([x[comp] for comp in x])
            normalise_x = {comp: float(np.round(x[comp] / total, 12)) for comp in x}

            return normalise_x

        normalised_eq_composition = normalise(eq_composition)

        for comp in x:
            if comp not in normalised_eq_composition:
                normalised_eq_composition[comp] = 0.0

        # extracting bond fractions
        number_of_cations: int = ca.tqnolc(1, 0)
        number_of_anions: int = ca.tqnolc(1, 1)

        sublattice_ions: list[str] = [
            ca.tqgnlc(1, 0, c) for c in range(number_of_cations)
        ] + [ca.tqgnlc(1, 1, c) for c in range(number_of_anions)]

        cation_dictionary = {
            "SiO2": "Si",
            "MgO": "Mg",
            "CaO": "Ca",
            "Al2O3": "Al",
            "FeO": "Fe2+",
            "Fe2O3": "Fe3+",
        }

        list_of_cations: list[str] = [
            cation_dictionary[comp] for comp in normalised_eq_composition
        ]

        bond_fractions: dict[str, float] = {}
        for cation1 in list_of_cations:
            for cation2 in list_of_cations:
                bond_fractions[f"{cation1}-{cation2}"] = ca.tqbond(
                    1,
                    sublattice_ions.index(cation1),
                    sublattice_ions.index(cation2),
                    sublattice_ions.index("O"),
                    sublattice_ions.index("O"),
                )
        return normalised_eq_composition, bond_fractions

    model = MyModel(esf=my_esf) # my_esf is ready to be used in the slag property models
    ...

The dictionaries ``normalised_eq_composition`` and ``bond_fractions`` that is returned by ``my_esf`` will contain the equilibrium slag composition and all cation combinations of bond fractions, respectively.
