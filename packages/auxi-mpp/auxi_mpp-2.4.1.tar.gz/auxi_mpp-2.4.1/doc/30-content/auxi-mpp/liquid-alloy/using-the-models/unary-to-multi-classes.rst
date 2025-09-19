.. _unary-to-multi-classes-liquid-alloy:

Unary, Binary and Multi Classes
================================

The unary, binary and multi-component material physical property classes for liquid alloys all function in the same way.

Let ``ModelBinary`` represent an abstract binary class.

Creating an Instance
--------------------

To create an instance of ``ModelBinary``, it can be called as is.

.. code-block::

   ExampleModel = ModelBinary()


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

   result = ExampleModel.calculate(T=1800, x={"Fe": 0.5, "Co": 0.5})

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be used.
