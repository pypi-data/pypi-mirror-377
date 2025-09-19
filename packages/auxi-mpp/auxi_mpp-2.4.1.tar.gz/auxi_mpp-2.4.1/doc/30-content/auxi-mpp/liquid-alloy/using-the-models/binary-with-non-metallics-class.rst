.. _binary-woth-non-metallics-classes-liquid-alloy:

Binary with Non-Metallics Classes
=================================

The molar volume and density for specific binary alloys can be determined using their respective commercial classes.

* **For Molar Volume:**  ``EmpiricalBinaryWithNonMetallics``
* **For Density:**  ``EmpiricalBinaryWithNonMetallics``

Both classes function in the same way.

Let ``PropertyBinaryWithNonMetallics`` represent an abstract binary with non-metallics class.

Creating an Instance
--------------------

To create an instance of ``PropertyBinaryWithNonMetallics``, it can be called as is.

.. code-block::

   ExampleModel = PropertyBinaryWithNonMetallics()


Calculating the Physical Property
---------------------------------

To calculate the relevant physical property, the ``calculate`` method is called on the model instance, while at the same time providing the conditions.

.. code-block::
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``

All quantities provided should be in SI units and amount fractions should be given as mole fractions.
If a temperature or pressure is not provided, standard temperature and pressure will be assumed.
Note that the activity should not be provided for liquid alloy models.

Usage example:

.. code-block::

   result = ExampleModel.calculate(T=1700, x={"Fe": 0.97, "C":0.03})

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be used.

