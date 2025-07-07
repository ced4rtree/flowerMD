"""Initialize signac project workspace"""

import signac
from itertools import product

def get_parameters():
    dt = 0.001
    parameters = {
        "lpar": [1.0],
        "lperp": [0.5],
        "num_mols": [128],
        "bead_mass": [1.0],
        "lengths": [1],
        "epsilon": [1.0],
        "r_cut": [3.0],
        "dt": [dt],
        "bond_r0": [0.1],

        # packing parameters
        "density_initial": [3.3],
        "packing_expand_factor": [4],
        "pack_edge": [2.0],
        "pack_overlap": [2.0],
        "pack_fix_orientation": [True],
    
        # shrinking parameters
        "density_final": [0.45],
        "shrink_steps": [1e7],
        "shrink_kT": [1.0],
        "shrink_tau_kt": [50*dt],
        "shrink_period": [10],
        "shrink_thermalize_particles": [True],
    
        # static sim parameters
        "static_steps": [5e4],
        "static_kT": [1.0],
        "static_tau_kt": [50*dt],
        "static_thermalize_particles": [True],
    }
    return list(parameters.keys()), list(product(*parameters.values()))

project = signac.get_project()
param_names, param_combinations = get_parameters()

for param_combo in param_combinations:
    statepoint = dict(zip(param_names, param_combo))
    job = project.open_job(statepoint).init()
