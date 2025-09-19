The main goal of this project is to provide easy access to semiconductor
band parameters for calculations and simulations. Basic functionality
requires only the standard python distribution.

Example scripts are provided for basic usage and for generating common
plots such as bandgap vs. lattice constant and bandgap vs. alloy
composition.

Materials included in this version:
- III-V Zinc Blendes
    - Binaries
        - AlN, GaN, InN,
          AlP, GaP, InP,
          AlAs, GaAs, InAs,
          AlSb, GaSb, InSb
    - Ternaries
        - AlGaN, AlInN, GaInN,
          AlGaP, AlInP, GaInP,
          AlGaAs, AlInAs, GaInAs,
          AlGaSb, AlInSb, GaInSb,
          AlNP, GaNP, InNP,
          AlNAs, GaNAs, InNAs,
          AlPAs, GaPAs, InPAs,
          AlPSb, GaPSb, InPSb,
          AlAsSb, GaAsSb, InAsSb
    - Quaternaries
        - AlNPAs, AlPAsSb,
          GaNPAs, GaPAsSb,
          InNPAs, InPAsSb,
          AlGaInN, AlGaInP, AlGaInAs, AlGaInSb,
          AlGaNP, AlInNP, GaInNP,
          AlGaNAs, AlInNAs, GaInNAs,
          AlGaPAs, AlInPAs, GaInPAs,
          AlGaPSb, AlInPSb, GaInPSb,
          AlGaAsSb, AlInAsSb, GaInAsSb

Parameters included in this version:
- lattice constants
- thermal expansion coefficients
- bandgap energies (direct and indirect)
- Varshni parameters
- split-off energies
- effective masses
- Luttinger parameters
- Kane parameters (Ep and F)
- Valance band offsets
- band deformation potentials
- elastic constants
- alloy bowing parameters
- effects of biaxial strain
- optical refractive index based on doi: 10.1088/0965-0393/4/4/002

The [source code](https://github.com/duarte-jfs/openbandparams/) and [documentation](https://duarte-jfs.github.io/openbandparams/) are graciously hosted by GitHub.


Up to and including version 0.9, the source code has been maintained by Scott J. Maddox, and you can find it's original repo here ([source code](http://github.com/scott-maddox/openbandparams)).