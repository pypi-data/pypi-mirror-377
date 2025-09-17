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

import numpy as np
from math import ceil
from warnings import warn
from .. import SanUnit, Construction
from ..processes._decay import Decay
from ..utils import ospath, load_data, data_path, dct_from_str

__all__ = ('DryingBed', 'LiquidTreatmentBed')


# %%

drying_bed_path = ospath.join(data_path, 'sanunit_data/_drying_bed.tsv')

class DryingBed(SanUnit, Decay):
    '''
    Unplanted and planted drying bed for solids based on
    `Trimmer et al. <https://doi.org/10.1021/acs.est.0c03296>`_

    To enable life cycle assessment, the following impact items should be pre-constructed:
    `Concrete`, `Steel`.

    Parameters
    ----------
    ins : WasteStream
        Solid for drying.
    outs : WasteStream
        Dried solids, evaporated water, fugitive CH4, and fugitive N2O.
    design_type : str
        Can be "unplanted" or "planted". The default unplanted process has
        a number of "covered", "uncovered", and "storage" beds. The storage
        bed is similar to the covered bed, but with higher wall height.

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
        'Single covered bed volume': 'm3',
        'Single uncovered bed volume': 'm3',
        'Single storage bed volume': 'm3',
        'Single planted bed volume': 'm3',
        'Total cover area': 'm2',
        'Total column length': 'm'
        }

    def __init__(self, ID='', ins=None, outs=(), thermo=None, init_with='WasteStream',
                 design_type='unplanted', degraded_components=('OtherSS',), **kwargs):
        Decay.__init__(self, ID, ins, outs, thermo=thermo,
                       init_with=init_with, F_BM_default=1,
                       degraded_components=degraded_components,
                       if_capture_biogas=False,
                       if_N2O_emission=True,)
        N_unplanted = {'covered': 19,
                       'uncovered': 30,
                       'storage': 19,
                       'planted': 0}
        if design_type == 'unplanted':
            self._N_bed = N_unplanted
            self.design_type = 'unplanted'
        else:
            self._N_bed = dict.fromkeys(N_unplanted.keys(), 0)
            self._N_bed['planted'] = 2
            self.design_type = 'planted'

        data = load_data(path=drying_bed_path)
        for para in data.index:
            if para == 'N_bed': continue
            if para in ('sol_frac', 'bed_L', 'bed_W', 'bed_H'):
                value = dct_from_str(data.loc[para]['expected'], dtype='float')
            else:
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
        sol, evaporated, CH4, N2O = self.outs
        evaporated.phase = CH4.phase = N2O.phase = 'g'

        # COD/N degradation in settled solids
        Decay._first_order_run(self, waste=waste, treated=sol)
        sol_COD = sol._COD/1e3*sol.F_vol

        # Adjust water content in the dried solids
        sol_frac = self.sol_frac
        solid_content = 1 - sol.imass['H2O']/sol.F_mass
        if solid_content > sol_frac:
            msg = f'Solid content of the solid after COD removal is {solid_content:.2f}, '\
                f'larger than the set sol_frac of {sol_frac:.2f} for the {self.design_type} ' \
                'process type, the set value is ignored.'
            warn(msg, stacklevel=3)
            evaporated.empty()
        else:
            sol.imass['H2O'] = (sol.F_mass-sol.imass['H2O'])/sol_frac
            evaporated.imass['H2O'] = waste.imass['H2O'] - sol.imass['H2O']
        sol._COD = sol_COD*1e3/sol.F_vol


    def _design(self):
        design = self.design_results

        L = np.fromiter(self.bed_L.values(), dtype=float)
        W = np.fromiter(self.bed_W.values(), dtype=float)
        H = np.fromiter(self.bed_H.values(), dtype=float)
        V = L * W * H
        N_bed = self.N_bed
        N = np.fromiter(N_bed.values(), dtype=int)
        for n, i in enumerate(N_bed.keys()):
            design[f'Number of {i} bed'] = N_bed[i]
            design[f'Single {i} bed volume'] = V[n]
        cover_array = np.array((1, 0, 1, 0)) # covered, uncovered, storage, planted
        design['Total cover area'] = tot_cover_area = \
            (cover_array*N*L*W/(np.cos(self.cover_slope/180*np.pi))).sum()
        design['Total column length'] = tot_column_length = \
            (cover_array*N*2*self.column_per_side*self.column_H).sum()

        concrete = (N*self.concrete_thickness*(L*W+2*L*H+2*W*H)).sum()
        steel = tot_cover_area*self.cover_unit_mass + \
            tot_column_length*self.column_unit_mass

        constr = self.construction
        constr[0].quantity = concrete
        constr[1].quantity = steel

        for i in self.construction:
            self.F_BM[i.item.ID] = 1

    @property
    def tau(self):
        '''[float] Retention time, [d].'''
        return self._tau
    @tau.setter
    def tau(self, i):
        self._tau = float(i)

    @property
    def sol_frac(self):
        '''[float] Final solid content of the dried solids.'''
        return self._sol_frac[self.design_type]
    @sol_frac.setter
    def sol_frac(self, i):
        self._sol_frac[self.design_type] = float(i)

    @property
    def design_type(self):
        '''[str] Drying bed type, can be either "unplanted" or "planted".'''
        return self._design_type
    @design_type.setter
    def design_type(self, i):
        if i in ('unplanted', 'planted'):
            self._design_type = i
            self.line =f'{i.capitalize()} drying bed'
        else:
            raise ValueError(f'design_type can only be "unplanted" or "planted", '
                             f"not {i}.")

    @property
    def N_bed(self):
        '''
        [dict] Number of the different types of drying beds,
        float will be converted to the smallest integer.
        '''
        for i, j in self._N_bed.items():
            self._N_bed[i] = ceil(j)
        return self._N_bed
    @N_bed.setter
    def N_bed(self, i):
        int_i = {k: ceil(v) for k, v in i.items()}
        self._N_bed.update(int_i)

    @property
    def bed_L(self):
        '''[dict] Length of the different types of drying beds, [m].'''
        return self._bed_L
    @bed_L.setter
    def bed_L(self, i):
        self._bed_L.update(i)

    @property
    def bed_W(self):
        '''[dict] Width of the different types of drying beds, [m].'''
        return self._bed_W
    @bed_W.setter
    def bed_W(self, i):
        self._bed_W.update(i)

    @property
    def bed_H(self):
        '''[dict] Wall height of the different types of drying beds, [m].'''
        return self._bed_H
    @bed_H.setter
    def bed_H(self, i):
        self._bed_H.update(i)

    @property
    def column_H(self):
        '''[float] Column height for covered bed, [m].'''
        return self._column_H
    @column_H.setter
    def column_H(self, i):
        self._column_H = float(i)

    @property
    def column_per_side(self):
        '''[int] Number of columns per side of covered bed, float will be converted to the smallest integer.'''
        return self._column_per_side
    @column_per_side.setter
    def column_per_side(self, i):
        self._column_per_side = ceil(i)

    @property
    def column_unit_mass(self):
        '''[float] Unit mass of the column, [kg/m].'''
        return self._column_unit_mass
    @column_unit_mass.setter
    def column_unit_mass(self, i):
        self._column_unit_mass = float(i)

    @property
    def concrete_thickness(self):
        '''[float] Thickness of the concrete wall.'''
        return self._concrete_thickness
    @concrete_thickness.setter
    def concrete_thickness(self, i):
        self._concrete_thickness = float(i)

    @property
    def cover_slope(self):
        '''[float] Slope of the bed cover, [°].'''
        return self._cover_slope
    @cover_slope.setter
    def cover_slope(self, i):
        self._cover_slope = float(i)

    @property
    def cover_unit_mass(self):
        '''[float] Unit mass of the bed cover, [kg/m2].'''
        return self._cover_unit_mass
    @cover_unit_mass.setter
    def cover_unit_mass(self, i):
        self._cover_unit_mass = float(i)


# %%

liquid_bed_path = ospath.join(data_path, 'sanunit_data/_liquid_treatment_bed.tsv')


class LiquidTreatmentBed(SanUnit, Decay):
    '''
    For secondary treatment of liquid based on
    `Trimmer et al. <https://doi.org/10.1021/acs.est.0c03296>`_

    To enable life cycle assessment, the following impact items should be pre-constructed:
    Concrete.

    Parameters
    ----------
    ins : WasteStream
        Waste for treatment.
    outs : WasteStream
        Treated waste, fugitive CH4, and fugitive N2O.

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
    _N_outs = 3
    _run = Decay._first_order_run
    _units = {
        'Residence time': 'd',
        'Bed length': 'm',
        'Bed width': 'm',
        'Bed height': 'm',
        'Single bed volume': 'm3'
        }

    def __init__(self, ID='', ins=None, outs=(), thermo=None, init_with='WasteStream',
                 **kwargs):
        Decay.__init__(self, ID, ins, outs, thermo=thermo,
                       init_with=init_with, F_BM_default=1,
                       if_capture_biogas=False,
                       if_N2O_emission=False,)

        data = load_data(path=liquid_bed_path)
        for para in data.index:
            value = float(data.loc[para]['expected'])
            setattr(self, '_'+para, value)
        del data

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def _init_lca(self):
        self.construction = [
            Construction('concrete', linked_unit=self, item='Concrete', quantity_unit='m3'),
            ]

    def _design(self):
        design = self.design_results
        design['Residence time'] = self.tau
        design['Bed number'] = N = self.N_bed
        design['Bed length'] = L = self.bed_L
        design['Bed width'] = W = self.bed_W
        design['Bed height'] = H = self.bed_H
        design['Single bed volume'] = L*W*H

        concrete = N*self.concrete_thickness*(L*W+2*L*H+2*W*H)
        self.construction[0].quantity = concrete
        self.add_construction()


    def _cost(self):
        pass


    @property
    def tau(self):
        '''[float] Residence time, [d].'''
        return self._tau
    @tau.setter
    def tau(self, i):
        self._tau = i

    @property
    def N_bed(self):
        '''[int] Number of treatment beds, float will be converted to the smallest integer.'''
        return self._N_bed
    @N_bed.setter
    def N_bed(self, i):
        self._N_bed = ceil(i)

    @property
    def bed_L(self):
        '''[float] Bed length, [m].'''
        return self._bed_L
    @bed_L.setter
    def bed_L(self, i):
        self._bed_L = i

    @property
    def bed_W(self):
        '''[float] Bed width, [m].'''
        return self._bed_W
    @bed_W.setter
    def bed_W(self, i):
        self._bed_W = i

    @property
    def bed_H(self):
        '''[float] Bed height, [m].'''
        return self._bed_H
    @bed_H.setter
    def bed_H(self, i):
        self._bed_H = i

    @property
    def concrete_thickness(self):
        '''[float] Thickness of the concrete wall.'''
        return self._concrete_thickness
    @concrete_thickness.setter
    def concrete_thickness(self, i):
        self._concrete_thickness = i