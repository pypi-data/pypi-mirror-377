.. _equilibrium-calculation:

Equilibrium Calculation
=======================

Before the equilibrium composition and bond fractions can be extracted, an equilibrium calculation is required.
To do this using ChemApp for Python, we start with loading the ``.cst`` file.

.. code-block::

       from chemapp.core import PressureUnit, Status, TemperatureUnit

       import chemapp.basic as ca

       from chemapp.friendly import EquilibriumCalculation as caec
       from chemapp.friendly import ThermochemicalSystem as cats
       from chemapp.friendly import Units

       cats.load("path/to/your.cst")

Be sure to set up SI units for the calculation.

.. code-block::

       Units.set_T_unit(TemperatureUnit.K)
       Units.set_P_unit(PressureUnit.Pa)

Set incoming amounts for phase constituents.

.. code-block::

       assay_dictionary : dict[str, float] = dict_of_components_with_fractions
       for comp in assay_dictionary:
           caec.set_IA_pc("Slag-liq#1", comp, assay_dictionary[comp])

Implement the activities, if they are specified. Note that the user here has the freedom to set the phase names to be used in 'a'. In this example, the naming convention of FactSage was upheld.

.. code-block::

       activity_dictionary : dict[str, dict[str, float]] = dict_of_phases_with_dict_of_pc_activities

       if "Fe_liquid(liq)" in a:
           caec.set_IA_pc("Fe_liquid(liq)", "Fe_liquid(liq)", 0.0)
           caec.set_eq_AC_pc("Fe_liquid(liq)", "Fe_liquid(liq)", a["Fe_liquid(liq)"]["Fe"])

       if "gas_ideal" in a:
           caec.set_IA_pc("gas_ideal", "O2", 0.0)
           caec.set_eq_AC_pc("gas_ideal", "O2", a["gas_ideal"]["O2"])

Set the equilibrium temperature and pressure.

.. code-block::

       caec.set_eq_T(my_temperature)
       caec.set_eq_P(my_pressure)

Ensure only the slag phase is used.

.. code-block::

       cats.set_status_phs(Status.ELIMINATED)
       cats.set_status_ph("Slag-liq#1", Status.ENTERED)

Perform the equilibrium calculation.

.. code-block::

       caec.calculate_eq(print_results=False)

The equilibrium composition and bond fractions can now be extracted.
The equilibrium composition can be obtained as follows.

.. code-block::

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

       for comp in assay_dictionary:
           if comp not in normalised_eq_composition:
               normalised_eq_composition[comp] = 0.0
