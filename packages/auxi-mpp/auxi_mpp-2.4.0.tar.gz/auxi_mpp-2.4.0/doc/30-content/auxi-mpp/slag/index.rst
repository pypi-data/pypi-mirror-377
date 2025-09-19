.. _slag:

Slag
====

Physical Property Models
------------------------


#. **Density** model based on the molar volume model by Thibodeau et al. (2016).

    To import:

    .. code-block::

        from auxi.mpp.slag.ρ import (
            ThibodeauDensityUnary,
            ThibodeauDensityBinary,
            ThibodeauDensityMulti
            )

#. **Molar Volume** model by Thibodeau et al. (2016).

    To import:

    .. code-block::

        from auxi.mpp.slag.Vm import (
            ThibodeauUnary,
            ThibodeauBinary,
            ThibodeauMulti
            )

#. **Ionic Diffusivity** model by Thibodeau et al. (2016).

    To import, call

    .. code-block::

        from auxi.mpp.slag.D import (
            ThibodeauIDUnary,
            ThibodeauIDBinary,
            ThibodeauIDMulti
            )

#. **Electrical Conductivity** model by Thibodeau et al. (2016).

    To import:

    .. code-block::

        from auxi.mpp.slag.σ import (
            ThibodeauECUnary,
            ThibodeauECBinary,
            ThibodeauECMulti
            )

#. **Viscosity** model by Grundy et al. (2008), Brosh et al. (2012) and Kim et al. (2021).

    To import:

    .. code-block::

        from auxi.mpp.slag.µ import (
            GrundyKimBroshUnary,
            GrundyKimBroshBinary,
            GrundyKimBroshMulti
            )

Using the Models
----------------

The ``auxi-mpp`` models are subdivided into unary, binary and multi-component classes.
Using these model classes is as simple as creating an instance of it and calling the ``calculate`` method on it.
There are some differences how this works between unary, binary and multi-component model, however.
These are explained below.

.. toctree::
   :maxdepth: 1

   using-the-models/unary-class
   using-the-models/binary-class
   using-the-models/multi-class
   esf-example/index
