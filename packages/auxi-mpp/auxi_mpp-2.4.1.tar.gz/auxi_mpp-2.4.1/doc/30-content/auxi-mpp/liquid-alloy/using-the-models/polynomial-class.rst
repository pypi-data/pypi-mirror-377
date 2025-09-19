.. _polynomial-class-liquid-alloy:

Polynomial Based Class
======================

The unary, binary and multi-component polynomial classes all function in the same way.
Let ``PolynomialClass`` represent an abstract polynomial class.

Creating an Instance
--------------------

To create an instance of ``PolynomialClass``, it can be called as is or the degree of the polynomial can be provided (defaults to 2).

.. code-block::

   ExampleModel = PolynomialClass(degree=2)


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

   result = ExampleModel.calculate(T=1800, x={"Fe": 0.95, "Si": 0.05})

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be used.
