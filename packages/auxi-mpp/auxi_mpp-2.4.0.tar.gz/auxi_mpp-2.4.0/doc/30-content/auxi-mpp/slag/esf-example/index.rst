.. _esf-example:

Equilibrium Slag Function
======================

The equilibrium slag function (esf) is a user-defined function which should take in temperature, pressure, composition and oxidation conditions, and return equilibrium slag composition and bond fractions.
This function is type sensitive, meaning the inputs and outputs of it should follow a specific type and order -- see :ref:`building-the-function`.

In the context of the slag physical property models in ``auxi-mpp``, bond fractions refer to the abundance of the different cation-oxygen-cation (M-O-M) units.
These bond fractions are essential to describe the short- to medium-range structure in slag, which is an important phenomenon that dictates its physical properties.

However, the precise bond fractions of the various cation combinations do not scale linearly with slag constituent fractions and are therefore not as straightforward to obtain.
`ChemApp for Python <https://python.gtt-technologies.de/doc/chemapp/main.html#>`_ implements the Modified Quasichemical Model (:term:`MQM`) to determine these bond fractions, which is why the equilibrium slag functions require it.

All non-polynomial binary and multi component models require the user to provide a :term:`ESF`.
Here, we provide a condensed guide on how to set up a :term:`ESF` that implements `ChemApp for Python <https://python.gtt-technologies.de/doc/chemapp/main.html#>`_.


.. toctree::
   :maxdepth: 1

   equilibrium-calculation
   extracting-bond-fractions
   building-the-function
