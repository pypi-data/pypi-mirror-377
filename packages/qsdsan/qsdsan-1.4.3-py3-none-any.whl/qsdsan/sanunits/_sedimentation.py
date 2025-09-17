#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
QSDsan: Quantitative Sustainable Design for sanitation and resource recovery systems

This module is developed by:
    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/main/LICENSE.txt
for license details.
'''


# %%

from math import ceil, pi, cos
from . import SludgeSeparator
from .. import Construction
from ..processes import Decay
from ..utils import ospath, load_data, data_path

__all__ = ('Sedimentation',)

sedmentation_path = ospath.join(data_path, 'sanunit_data/_sedimentation_tank.tsv')


class Sedimentation(SludgeSeparator, Decay):
    '''
    Sedimentation of wastes into liquid and solid phases based on
    `Trimmer et al. <https://doi.org/10.1021/acs.est.0c03296>`_

    To enable life cycle assessment, the following impact items should be pre-constructed:
    `Concrete`, `Steel`.

    Parameters
    ----------
    ins : Iterable(stream)
        Waste for treatment.
    outs : Iterable(stream)
        Liquid, settled solids, fugitive CH4, and fugitive N2O.

    Examples
    --------
    `bwaise systems <https://github.com/QSD-Group/EXPOsan/blob/main/exposan/bwaise/systems.py>`_

    References
    ----------
    [1] Trimmer et al., Navigating Multidimensional Social–Ecological System
    Trade-Offs across Sanitation Alternatives in an Urban Informal Settlement.
    Environ. Sci. Technol. 2020, 54 (19), 12641–12653.
    https://doi.org/10.1021/acs.est.0c03296.

    See Also
    --------
    :ref:`qsdsan.processes.Decay <processes_Decay>`
    '''
    _N_ins = 1
    _N_outs = 4
    _units = {
        'Single tank volume': 'm3',
        'Single tank height': 'm',
        'Single tank width': 'm',
        'Single tank length': 'm',
        'Single roof area': 'm2'
        }
    if_capture_biogas = False
    
    def __init__(self, ID='', ins=None, outs=(),thermo=None, init_with='WasteStream',
                 split=None, settled_frac=None,
                 degraded_components=('OtherSS',), if_N2O_emission=False, **kwargs):

        SludgeSeparator.__init__(self, ID, ins, outs, thermo, init_with,
                                 split, settled_frac, F_BM_default=1)
        self._sol_copy = self.outs[1].copy()
        self.degraded_components = degraded_components
        self.if_N2O_emission = if_N2O_emission

        data = load_data(path=sedmentation_path)
        for para in data.index:
            value = float(data.loc[para]['expected'])
            setattr(self, '_'+para, value)
        del data

        for attr, value in kwargs.items():
            setattr(self, attr, value)


    def _init_lca(self):
        self.construction = [
            Construction('concrete', linked_unit=self, item='Concrete', quantity_unit='m3'),
            Construction('steel', linked_unit=self, item='Steel', quantity_unit='kg'),
            ]

    def _run(self):
        waste = self.ins[0]
        liq, sol, CH4, N2O = self.outs
        CH4.phase = N2O.phase = 'g'

        # Retention in the settled solids
        SludgeSeparator._run(self)
        
        sol_copy = self._sol_copy
        sol_copy.copy_like(sol)
        Decay._first_order_run(self, waste=sol_copy, treated=sol)

        # Adjust total mass of of the settled solids by changing water content
        sol_COD = sol.COD * sol.F_vol
        liq, sol = self._adjust_solid_water(waste, liq, sol)
        sol._COD = sol_COD / sol.F_vol


    def _design(self):
        design = self.design_results
        # `tau` not used, might be that working volume fraction not known
        design['Tank number'] = N = self.N_tank
        design['Single tank volume'] = V_single = self.tank_V
        L2W = self.tank_L_to_W
        W2H = self.tank_W_to_H
        design['Single tank height'] = H = (V_single/(L2W*(W2H**2)))**(1/3)
        design['Single tank width'] = W = H * W2H
        design['Single tank length'] = L = W * L2W
        design['Single roof area'] = N*L*W/(cos(self.roof_slope/180*pi))
        side_area = N*2*(L*H + W*H)

        # Concrete
        thick = self.concrete_thickness
        side_concrete = N*thick*(L*W+2*W*H+2*L*H)
        column_concrete = N*(thick**2)*H*self.column_per_side*2

        constr = self.construction
        constr[0].quantity = side_concrete + column_concrete
        constr[1].quantity = (design['Single roof area']+side_area) * self.roof_unit_mass # steel

        self.add_construction()

    @property
    def tau(self):
        '''[float] Residence time, [d].'''
        return self._tau
    @tau.setter
    def tau(self, i):
        self._tau = i

    @property
    def tank_V(self):
        '''[float] Volume of the sedimentation tank.'''
        return self._tank_V
    @tank_V.setter
    def tank_V(self, i):
        self._tank_V = i

    @property
    def tank_L_to_W(self):
        '''[float] Length-to-width ratio of the sedimentation tank.'''
        return self._tank_L_to_W
    @tank_L_to_W.setter
    def tank_L_to_W(self, i):
        self._tank_L_to_W = i

    @property
    def tank_W_to_H(self):
        '''[float] Width-to-height ratio of the sedimentation tank.'''
        return self._tank_W_to_H
    @tank_W_to_H.setter
    def tank_W_to_H(self, i):
        self._tank_W_to_H = i

    @property
    def N_tank(self):
        '''[int] Number of sedimentation tanks, float will be converted to the smallest integer.'''
        return self._N_tank
    @N_tank.setter
    def N_tank(self, i):
        self._N_tank = ceil(i)

    @property
    def column_per_side(self):
        '''[int] Number of columns per side of sedimentation tanks, float will be converted to the smallest integer.'''
        return self._column_per_side
    @column_per_side.setter
    def column_per_side(self, i):
        self._column_per_side = ceil(i)

    @property
    def concrete_thickness(self):
        '''[float] Thickness of the concrete wall.'''
        return self._concrete_thickness
    @concrete_thickness.setter
    def concrete_thickness(self, i):
        self._concrete_thickness = i

    @property
    def roof_slope(self):
        '''[float] Slope of the tank roof, [°].'''
        return self._roof_slope
    @roof_slope.setter
    def roof_slope(self, i):
        self._roof_slope = i

    @property
    def roof_unit_mass(self):
        '''[float] Unit mass of the tank roof, [kg/m2].'''
        return self._roof_unit_mass
    @roof_unit_mass.setter
    def roof_unit_mass(self, i):
        self._roof_unit_mass = i