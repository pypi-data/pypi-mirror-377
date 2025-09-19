.. _liquid-alloy:

Liquid Alloy 
============

Physical Property Models
------------------------

#. **Molar Volume** models.

    To import:

    .. code-block:: 

        from auxi.mpp.liquid_alloy.Vm import (
            EmpiricalUnary, 
            EmpiricalBinary, 
            EmpiricalMulti, 
            MillsCommercial, 
            EmpiricalBinaryWithNonMetallics
            )


#. **Density** models.

    To import:

    .. code-block::

        from auxi.mpp.liquid_alloy.ρ import (
            EmpiricalUnary,
            EmpiricalBinary, 
            EmpiricalMulti, 
            MillsCommercial, 
            EmpiricalBinaryWithNonMetallics
            )
  
#. **Electrical Conductivity** polynomial fits.

    To import:

    .. code-block::

        from auxi.mpp.liquid_alloy.σ import (
            PolynomialUnary, 
            PolynomialBinary, 
            PolynomialMulti
            )

#. **Viscosity** models.

    To import:

    .. code-block:: 

        from auxi.mpp.liquid_alloy.μ import (
            EmpiricalUnary,
            DengBinary, 
            DengMulti, 
            )

#. **Thermal Conductivity** Wiedemann-Franz implementations.

    To import:

    .. code-block::

        from auxi.mpp.liquid_alloy.κ import (
            WiedemannFranzUnary,
            WiedemannFranzBinary,
            WiedemannFranzMulti
            )

.. note::
  
   Two additional classes are available for calculating the **molar volume** and
   **density** of liquid alloys. These classes provide additional empirical
   models for specific alloy systems.

   * **For Molar Volume:** ``MillsCommercial``, ``EmpiricalBinaryWithNonMetallics``
   * **For Density:** ``MillsCommercial``, ``EmpiricalBinaryWithNonMetallics``

Using the Models
----------------

Calculating a physical property is as simple as creating an instance of a physical property model and calling the ``calculate`` method on it, through which the conditions can be specified.
All models are subdivided into unary, binary and multi-component models, from which model instances can be created.
For the polynomial-based models (electrical and thermal conductivity), the unary, binary and multi-component classes all function in the same way.
All model classes are explained below.

.. toctree::
   :maxdepth: 1

   using-the-models/unary-to-multi-classes
   using-the-models/polynomial-class
   using-the-models/property-commercial-class
   using-the-models/binary-with-non-metallics-class

