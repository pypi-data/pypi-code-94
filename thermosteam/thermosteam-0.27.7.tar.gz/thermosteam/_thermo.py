# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020-2021, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
"""
from . import equilibrium as eq
from ._chemical import Chemical
from ._chemicals import Chemicals
from .mixture import Mixture
from .utils import read_only, cucumber

__all__ = ('Thermo', 'IdealThermo')


@cucumber # Just means you can pickle it
@read_only
class Thermo:
    """
    Create a Thermo object that defines a thermodynamic property package
    
    Parameters
    ----------
    chemicals : Iterable[:class:`~thermosteam.Chemical` or str]
        Pure component chemical data.
    mixture : :class:`~thermosteam.mixture.Mixture`, optional
        Calculates mixture properties.
    Gamma : :class:`~thermosteam.equilibrium.activity_coefficients.ActivityCoefficients` subclass, optional
        Class for computing activity coefficients.
    Phi : :class:`~thermosteam.equilibrium.fugacity_coefficients.FugacityCoefficients` subclass, optional
        Class for computing fugacity coefficients.
    PCF : :class:`~thermosteam.equilibrium.poyinting_correction_factors.PoyintingCorrectionFactors` subclass, optional
        Class for computing poynting correction factors.
    cache : optional
        Whether or not to use cached chemicals.
    skip_checks : bool, optional
        Whether to skip checks for missing or invalid properties.
    
    Examples
    --------
    Create a property package for water and ethanol:
    
    >>> import thermosteam as tmo
    >>> thermo = tmo.Thermo(['Ethanol', 'Water'], cache=True)
    >>> thermo
    Thermo(chemicals=CompiledChemicals([Ethanol, Water]), mixture=Mixture(rule='ideal', ..., include_excess_energies=False), Gamma=DortmundActivityCoefficients, Phi=IdealFugacityCoefficients, PCF=IdealPoyintingCorrectionFactors)
    >>> thermo.show() # May be easier to read
    Thermo(
        chemicals=CompiledChemicals([Ethanol, Water]),
        mixture=Mixture(
            rule='ideal', ...
            include_excess_energies=False
        ),
        Gamma=DortmundActivityCoefficients,
        Phi=IdealFugacityCoefficients,
        PCF=IdealPoyintingCorrectionFactors
    )
    
    Note that the Dortmund-UNIFAC is the default activity coefficient model. 
    The ideal-equilibrium property package (which assumes a value of 1 for all
    activity coefficients) is also available:
        
    >>> ideal = thermo.ideal()
    >>> ideal.show()
    IdealThermo(
        chemicals=CompiledChemicals([Ethanol, Water]),
        mixture=Mixture(
            rule='ideal', ...
            include_excess_energies=False
        ),
    )
    
    Thermodynamic equilibrium results are affected by the choice of property package:
        
    >>> # Ideal
    >>> tmo.settings.set_thermo(ideal)
    >>> stream = tmo.Stream('stream', Water=100, Ethanol=100)
    >>> stream.vle(T=361, P=101325)
    >>> stream.show()
    MultiStream: stream
     phases: ('g', 'l'), T: 361 K, P: 101325 Pa
     flow (kmol/hr): (g) Ethanol  32.2
                         Water    17.3
                     (l) Ethanol  67.8
                         Water    82.7
    >>> # Modified Roult's law:                 
    >>> tmo.settings.set_thermo(thermo)
    >>> stream = tmo.Stream('stream', Water=100, Ethanol=100)
    >>> stream.vle(T=360, P=101325) 
    >>> stream.show()
    MultiStream: stream
     phases: ('g', 'l'), T: 360 K, P: 101325 Pa
     flow (kmol/hr): (g) Ethanol  100
                         Water    100
    
    Thermodynamic property packages are pickleable:
        
    >>> tmo.utils.save(thermo, "Ethanol-Water Property Package")
    >>> thermo = tmo.utils.load("Ethanol-Water Property Package")
    >>> thermo.show()
    Thermo(
        chemicals=CompiledChemicals([Ethanol, Water]),
        mixture=Mixture(
            rule='ideal', ...
            include_excess_energies=False
        ),
        Gamma=DortmundActivityCoefficients,
        Phi=IdealFugacityCoefficients,
        PCF=IdealPoyintingCorrectionFactors
    )
    
    Attributes
    ----------
    chemicals : Chemicals or Iterable[str]
        Pure component chemical data.
    mixture : Mixture, optional
        Calculates mixture properties.
    Gamma : ActivityCoefficients subclass, optional
        Class for computing activity coefficients.
    Phi : FugacityCoefficients subclass, optional
        Class for computing fugacity coefficients.
    PCF : PoyntingCorrectionFactor subclass, optional
        Class for computing poynting correction factors.
    
    """
    __slots__ = ('chemicals', 'mixture', 'Gamma', 'Phi', 'PCF', '_ideal') 
    
    def __init__(self, chemicals, mixture=None,
                 Gamma=eq.DortmundActivityCoefficients,
                 Phi=eq.IdealFugacityCoefficients,
                 PCF=eq.IdealPoyintingCorrectionFactors,
                 cache=None,
                 skip_checks=False):
        if not isinstance(chemicals, Chemicals): chemicals = Chemicals(chemicals, cache)
        if not mixture:
            mixture = Mixture.from_chemicals(chemicals)
        elif not isinstance(mixture, Mixture): # pragma: no cover
            raise ValueError(f"mixture must be a '{Mixture.__name__}' object")
        chemicals.compile(skip_checks=skip_checks)
        issubtype = issubclass
        if not issubtype(Gamma, eq.ActivityCoefficients): # pragma: no cover
            raise ValueError(f"Gamma must be a '{eq.ActivityCoefficients.__name__}' subclass")
        if not issubtype(Phi, eq.FugacityCoefficients): # pragma: no cover
            raise ValueError(f"Phi must be a '{eq.FugacityCoefficients.__name__}' subclass")
        if not issubtype(PCF, eq.PoyintingCorrectionFactors): # pragma: no cover
            raise ValueError(f"PCF must be a '{eq.PoyintingCorrectionFactors.__name__}' subclass")
        
        setattr = object.__setattr__
        setattr(self, 'chemicals', chemicals)
        setattr(self, 'mixture', mixture)
        setattr(self, 'Gamma', Gamma)
        setattr(self, 'Phi', Phi)
        setattr(self, 'PCF', PCF)
        setattr(self, '_ideal', None)
    
    def subset(self, chemicals):
        if chemicals is self.chemicals: return self
        if not isinstance(chemicals, Chemicals): chemicals = Chemicals(chemicals)
        groups = [(name, index) for name, index in self.chemicals._index.items() 
                  if isinstance(index, list)]
        chemicals.compile(skip_checks=True)
        CASs = self.chemicals.CASs
        for name, index in groups:
            group_CASs = [CASs[i] for i in index]
            chemicals.define_group(name, [i for i in group_CASs if i in chemicals])
        cls = self.__class__
        new = cls.__new__(cls)
        setattr = object.__setattr__
        setattr(new, 'chemicals', chemicals)
        setattr(new, 'mixture', self.mixture.from_chemicals(chemicals))
        setattr(new, 'Gamma', self.Gamma)
        setattr(new, 'Phi', self.Phi)
        setattr(new, 'PCF', self.PCF)
        setattr(new, '_ideal', None)
        return new
    
    def ideal(self):
        """Ideal thermodynamic property package."""
        ideal = self._ideal
        if not ideal: 
            ideal = IdealThermo.__new__(IdealThermo)
            setattr = object.__setattr__
            setattr(ideal, 'chemicals', self.chemicals)
            setattr(ideal, 'mixture', self.mixture)
            setattr(self, '_ideal', ideal)
        return ideal
    
    def as_chemical(self, chemical):
        """
        Return chemical as a Chemical object.

        Parameters
        ----------
        chemical : str or Chemical
            Name of chemical being retrieved.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> thermo = tmo.Thermo(['Ethanol', 'Water'], cache=True)
        >>> thermo.as_chemical('Water') is thermo.chemicals.Water
        True
        >>> thermo.as_chemical('Octanol') # Chemical not defined, so it will be created
        Chemical('Octanol')
        
        """
        isa = isinstance
        if isa(chemical, str):
            try: 
                chemical = self.chemicals[chemical]
            except:
                chemical = Chemical(chemical)
        elif not isa(chemical, Chemical): # pragma: no cover
            raise ValueError(f"can only convert '{type(chemical).__name__}' object to chemical")
        return chemical
    
    def __repr__(self):
        return f"{type(self).__name__}(chemicals={self.chemicals}, mixture={self.mixture}, Gamma={self.Gamma.__name__}, Phi={self.Phi.__name__}, PCF={self.PCF.__name__})"
    
    def show(self):
        try:
            mixture_info = self.mixture._info().replace('\n', '\n    ')
        except: # pragma: no cover
            mixture_info = str(self.mixture)
        print(f"{type(self).__name__}(\n"
              f"    chemicals={self.chemicals},\n"
              f"    mixture={mixture_info},\n"
              f"    Gamma={self.Gamma.__name__},\n"
              f"    Phi={self.Phi.__name__},\n"
              f"    PCF={self.PCF.__name__}\n"
               ")")
    _ipython_display_ = show
    
@cucumber # Just means you can pickle it
@read_only
class IdealThermo:
    """
    Create a Thermo object that defines a thermodynamic property package
    
    Parameters
    ----------
    chemicals : Iterable[:class:`~thermosteam.Chemical` or str]
        Pure component chemical data.
    mixture : :class:`~thermosteam.mixture.Mixture`, optional
        Calculates mixture properties.
    cache : optional
        Whether or not to use cached chemicals.
    skip_checks : bool, optional
        Whether to skip checks for missing or invalid properties.
    
    
    Attributes
    ----------
    chemicals : Chemicals or Iterable[str]
        Pure component chemical data.
    mixture : Mixture, optional
        Calculates mixture properties.
        
    """
    __slots__ = ('chemicals', 'mixture') 
    
    Gamma = eq.IdealActivityCoefficients
    Phi = eq.IdealFugacityCoefficients
    PCF = eq.IdealPoyintingCorrectionFactors
    as_chemical = Thermo.as_chemical
    
    def __init__(self, chemicals, mixture=None,
                 cache=None,
                 skip_checks=False):
        if not isinstance(chemicals, Chemicals): chemicals = Chemicals(chemicals, cache)
        if not mixture:
            mixture = Mixture.from_chemicals(chemicals)
        elif not isinstance(mixture, Mixture): # pragma: no cover
            raise ValueError(f"mixture must be a '{Mixture.__name__}' object")
        chemicals.compile(skip_checks=skip_checks)
        setattr = object.__setattr__
        setattr(self, 'chemicals', chemicals)
        setattr(self, 'mixture', mixture)
    
    def subset(self, chemicals):
        if chemicals is self.chemicals: return self
        if not isinstance(chemicals, Chemicals): chemicals = Chemicals(chemicals)
        groups = [(name, index) for name, index in self.chemicals._index.items() 
                  if isinstance(index, list)]
        chemicals.compile(skip_checks=True)
        CASs = self.chemicals.CASs
        for name, index in groups:
            group_CASs = [CASs[i] for i in index]
            chemicals.define_group(name, [i for i in group_CASs if i in chemicals])
        cls = self.__class__
        new = cls.__new__(cls)
        setattr = object.__setattr__
        setattr(new, 'chemicals', chemicals)
        setattr(new, 'mixture', self.mixture.from_chemicals(chemicals))
        return new
    
    def ideal(self):
        """Ideal thermodynamic property package."""
        return self
    
    def __repr__(self):
        return f"{type(self).__name__}(chemicals={self.chemicals}, mixture={self.mixture})"
    
    def show(self):
        try:
            mixture_info = self.mixture._info().replace('\n', '\n    ')
        except: # pragma: no cover
            mixture_info = str(self.mixture)
        print(f"{type(self).__name__}(\n"
              f"    chemicals={self.chemicals},\n"
              f"    mixture={mixture_info},\n"
               ")")
    _ipython_display_ = show