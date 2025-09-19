.. _property-commercial-classes-liquid-alloy:

Commercial Alloy Property Classes
=================================

The molar volume and density for specific commercial alloys can be determined using their respective commercial classes.

* **For Molar Volume:** ``MillsCommercial``
* **For Density:** ``MillsCommercial``

Both commercial classes function in the same way.

Let ``PropertyCommercial`` represent an abstract commercial class.

Creating an Instance
--------------------

To create an instance of ``PropertyCommercial``, it can be called as.

.. code-block::

   ExampleModel = PropertyCommercial()


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

   result = ExampleModel.calculate(T=1700, x={"grey_cast_iron": 1.0})

Available commercial alloys include:

.. code-block::
   
  - "grey_cast_iron"
  - "ductile_iron"
  - "stainless_steel_304"
  - "stainless_steel_316"

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be used.
