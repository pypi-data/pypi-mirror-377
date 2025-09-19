.. _essentials:

Essentials
==========

Each material physical property model in ``auxi-mpp`` is packaged into a Python class.
All models estimating the same physical property share the same class attributes, where only the references and material scope may vary.

Class Attributes
---------------

The class attributes describing the essence of the model are the following.

#. **property**

#. **symbol**

#. **display_symbol** - for use in :math:`\LaTeX`

#. **units** - for use in :math:`\LaTeX` (all model outputs are in SI units)

#. **references** - gives the source from which the model was taken

#. **compound_scope/component_scope/system_scope** - gives the scope of materials for which the model can be used

The compound/component/system scope is specific to the class in question.
Most models have either a compound scope (i.e. slag models) or a component scope (i.e. liquid alloy models).

These attributes are callable.
For example, if ``ExampleModel()`` is an instance of a molar volume model;

.. code-block::

   print(ExampleModel().property)

**Output**

.. code-block::

   Molar Volume
