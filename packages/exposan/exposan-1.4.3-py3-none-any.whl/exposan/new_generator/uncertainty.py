#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
EXPOsan: Exposition of sanitation and resource recovery systems

This module is developed by:

    Shion Watabe <shionwatabe@gmail.com>

    Hannah Lohman <hlohman94@gmail.com>

    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/EXPOsan/blob/main/LICENSE.txt
for license details.
'''

# Run uncertainty analysis and Spearman without country-specific settings
from exposan import new_generator as ng
from exposan.new_generator import create_model, run_uncertainty

def run(model_IDs, seed=None, N=1000, country_specific=False, **model_kwargs):
    # Make it possible to run with one or more models
    if isinstance(model_IDs, str): model_IDs = (model_IDs, )
    for ID in model_IDs:
        model = create_model(ID, country_specific=country_specific, **model_kwargs)
        run_uncertainty(model, seed=seed, N=N)


if __name__ == '__main__':
    ng.INCLUDE_RESOURCE_RECOVERY = True
    run(('A', 'B'), seed=5, N=50) # running systems A and B for contextual analysis with DMsan
