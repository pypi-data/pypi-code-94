# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module extends the tp_dependent_property module from the thermo library:
# https://github.com/CalebBell/thermo
# Copyright (C) 2020 Caleb Bell <Caleb.Andrew.Bell@gmail.com>
#
# This module is under a dual license:
# 1. The UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
# 
# 2. The MIT open-source license. See
# https://github.com/CalebBell/chemicals/blob/master/LICENSE.txt for details.
from thermo import TPDependentProperty, VolumeLiquid, VolumeGas

# Remove cache from call
def __call__(self, T, P):
    if self._method_P:
        return self.TP_dependent_property(T, P)
    else:
        return self.T_dependent_property(T)

TPDependentProperty.__call__ = __call__

# Missing method 
def has_method(self):
    return bool(self._method or self._method_P)

TPDependentProperty.__bool__ = has_method

# Handling methods

@TPDependentProperty.method_P.setter
def method_P(self, method):
    if method is not None:
        method, *_ = method.split('(')
        method = method.upper().replace(' ', '_').replace('_AND_', '_').strip('_').replace('SOLID', 'S')
        if method not in self.all_methods_P and method != 'POLY_FIT':
            raise ValueError("Pressure dependent method '%s' is not available for this chemical; "
                             "available methods are %s" %(method, self.all_methods_P))
    self._method_P = method

TPDependentProperty.method_P = method_P

VolumeLiquid.ranked_methods.remove('EOS')
VolumeLiquid.ranked_methods_P.remove('EOS')
VolumeGas.ranked_methods_P.remove('EOS')