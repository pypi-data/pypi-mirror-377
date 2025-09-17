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

__all__ = ('format_number', 'format_str',)


def format_number(number):
    '''Pretty print number based on its magnitude.'''
    if not number:
        return 'None'

    number = float(number)
    if abs(number) == 0 or str(number) == 'nan':
        return '0'

    elif abs(number) > 1e6 or abs(number) < 1e-4:
        return str(f'{number:.2E}')

    elif 1e-3 < abs(number) < 0.01:
        return str(round(number, 4))

    elif number == int(number):
        return str(int(number))

    else:
        return str(round(number, 2))


def format_str(string):
    '''Replace space and "-" with "_".'''
    string = string.replace(' ', '_')
    string = string.replace('-', '_')
    return string