#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
EXPOsan: Exposition of sanitation and resource recovery systems

This module is developed by:
    
    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/EXPOsan/blob/main/LICENSE.txt
for license details.
'''

import os
from exposan.utils import _init_modules
asm_path = os.path.dirname(__file__)
module = os.path.split(asm_path)[-1]
data_path, results_path = _init_modules(module, include_data_path=True)


# %%

# =============================================================================
# Load the components, process model, and system
# =============================================================================

from . import systems
from .systems import create_system

_system_loaded = False
_loaded_pc_model = None
_loaded_aerated = None
def load(reload=False, flowsheet=None, process_model='ASM1', aerated=False,
         inf_kwargs={}, asm_kwargs={}, init_conds={}):
    global _system_loaded, _loaded_pc_model, _loaded_aerated
    if (process_model!=_loaded_pc_model) or (_loaded_aerated!=aerated): reload = True
    if reload:
        global cmps, components, asm, sys
        sys = create_system(
            flowsheet=flowsheet,
            process_model=process_model,
            aerated=aerated,
            inf_kwargs=inf_kwargs,
            asm_kwargs=asm_kwargs,
            init_conds=init_conds,
            )
        CSTR = sys.flowsheet.unit.CSTR
        cmps = components = CSTR.components
        asm = CSTR.suspended_growth_model
        _loaded_pc_model = process_model
        _loaded_aerated = aerated
    dct = globals()
    dct.update(sys.flowsheet.to_dict())
    _system_loaded = True


def __getattr__(name):
    if not _system_loaded:
        raise AttributeError(
            f'Module {__name__} does not have the attribute "{name}" '
            'and the module has not been loaded, '
            f'loading the module with `{__name__}.load()` may solve the issue.')


__all__ = (
    'asm_path',
    'data_path',
    'results_path',
    *systems.__all__,
)