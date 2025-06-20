#!/usr/bin/env python

from flowermd.base import Pack,Lattice, Simulation
from flowermd.library import EllipsoidForcefield, EllipsoidChain
from flowermd.utils import get_target_box_number_density
from flowermd.utils.constraints import create_rigid_ellipsoid_chain
import argparse
import datetime
import gsd
import gsd.hoomd
import hoomd
import hoomd
import matplotlib.pyplot as plt
import numpy as np
import os
import signac
import unyt as u
import warnings
warnings.filterwarnings('ignore')

GSD_FILE_PATH = 'trajectory.gsd'
LOG_FILE_PATH = 'log.txt'

def run_sim(*jobs):
    for job in jobs:
        # job has already run, pass
        if job.isfile('trajectory.gsd'):
            continue

        parameters = job.cached_statepoint
        
        ellipsoid_chain = EllipsoidChain(
            lengths=parameters['lengths'],
            num_mols=parameters['num_mols'],
            lpar=parameters['lpar'],
            bead_mass=parameters['bead_mass'],
        )
        ff = EllipsoidForcefield(
            epsilon=parameters['epsilon'],
            lpar=parameters['lpar'],
            lperp=parameters['lperp'],
            r_cut=parameters['r_cut'],
            bond_r0=parameters['bond_r0'],
        )
        system = Pack(
            molecules=ellipsoid_chain,
            density=parameters['density_initial']*u.Unit("nm**-3"),
            packing_expand_factor=parameters['packing_expand_factor'],
            edge=parameters['pack_edge'],
            overlap=parameters['pack_overlap'],
            fix_orientation=parameters['pack_fix_orientation'],
        )
        
        rigid_frame, rigid_constraint = create_rigid_ellipsoid_chain(
            system.hoomd_snapshot
        )
        ellipsoid_sim = Simulation(
            initial_state=rigid_frame,
            forcefield=ff.hoomd_forces,
            constraint=rigid_constraint,
            gsd_write_freq=int(5e3),
            gsd_file_name=GSD_FILE_PATH,
            log_write_freq=int(5e3),
            log_file_name=LOG_FILE_PATH,
            dt=parameters['dt']
        )
        
        target_box = get_target_box_number_density(
            density=parameters['density_final']*u.Unit("nm**-3"),
            n_beads=parameters['num_mols']
        )
        ellipsoid_sim.run_update_volume(
            final_box_lengths=target_box,
            kT=parameters['shrink_kT'],
            n_steps=parameters['shrink_steps'],
            tau_kt=parameters['shrink_tau_kt'],
            period=parameters['shrink_period'],
            thermalize_particles=parameters['shrink_thermalize_particles']
        )
        ellipsoid_sim.run_NVT(
            n_steps=parameters['static_steps'],
            kT=parameters['static_kT'],
            tau_kt=parameters['static_tau_kt'],
            thermalize_particles=parameters['static_thermalize_particles'],
        )
        ellipsoid_sim.flush_writers()
        
        #ellipsoid_sim.save_restart_gsd("restart.gsd")
        #ellipsoid_sim.save_simulation("sim.pickle")



def ellipsoid_gsd(gsd_file, new_file, ellipsoid_types, lpar, lperp):
    """Add needed information to GSD file to visualize ellipsoids.

    Saves a new GSD file with lpar and lperp values populated
    for each particle. Ovito can be used to visualize the new GSD file.

    Parameters
    ----------
    gsd_file : str
        Path to the original GSD file containing trajectory information
    new_file : str
        Path and filename of the new GSD file
    ellipsoid_types : str or list of str
        The particle types (i.e. names) of particles to be drawn
        as ellipsoids.
    lpar : float
        Value of lpar of the ellipsoids
    lperp : float
        Value of lperp of the ellipsoids

    """
    with gsd.hoomd.open(new_file, "w") as new_t:
        with gsd.hoomd.open(gsd_file) as old_t:
            for snap in old_t:
                shape_dicts_list = []
                for ptype in snap.particles.types:
                    if ptype == ellipsoid_types or ptype in ellipsoid_types:
                        shapes_dict = {
                            "type": "Ellipsoid",
                            "a": lpar,
                            "b": lperp,
                            "c": lperp,
                        }
                    else:
                        shapes_dict = {"type": "Sphere", "diameter": 0.001}
                        shape_dicts_list.append(shapes_dict)
                        snap.particles.type_shapes = shape_dicts_list
                        snap.validate()
                        new_t.append(snap)

def process_logs(*jobs):
    for job in jobs:
        if job.isfile('ovito-trajectory.gsd'):
            continue
        
    ellipsoid_gsd(
        gsd_file=GSD_FILE_PATH,
        new_file=GSD_FILE_PATH.replace('trajectory.gsd', 'ovito-trajectory.gsd'),
        ellipsoid_types='R',
        lpar=parameters['lpar'],
        lperp=parameters['lperp'],
    )

    log = np.genfromtxt(LOG_FILE_PATH, names=True)
    timestep = log["flowermdbasesimulationSimulationtimestep"]
    potential_energy = log["mdcomputeThermodynamicQuantitiespotential_energy"]
    kinetic_energy = log["mdcomputeThermodynamicQuantitieskinetic_energy"]
    volume = log["mdcomputeThermodynamicQuantitiesvolume"]
    temp = log["mdcomputeThermodynamicQuantitieskinetic_temperature"]
    density = parameters['num_mols']/volume
    
    plt.plot(timestep, potential_energy/parameters['num_mols'])
    plt.title('Potential Energy Per Particle vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Potential Energy Per Particle')
    plt.savefig(output_dir + 'potential-energy.png')
    plt.close()
    
    plt.plot(timestep, potential_energy/parameters['num_mols'])
    plt.ylim(-1, 20000)
    plt.title('Potential Energy Per Particle vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Potential Energy Per Particle')
    plt.savefig(output_dir + 'potential-energy-limited.png')
    plt.close()
    
    plt.plot(timestep, kinetic_energy/parameters['num_mols'])
    plt.title('Kinetic Energy Per Particle vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Kinetic Energy')
    plt.savefig(output_dir + 'kinetic-energy.png')
    plt.close()
    
    plt.plot(timestep, volume)
    plt.title('Volume vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Volume')
    plt.savefig(output_dir + 'volume.png')
    plt.close()
    
    plt.plot(timestep, density)
    plt.title('Density vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Density')
    plt.savefig(output_dir + 'density.png')
    plt.close()
    
    plt.plot(timestep, temp)
    plt.title('Temperature vs. Time')
    plt.xlabel('Timestep')
    plt.ylabel('Temperature')
    plt.savefig(output_dir + 'temp.png')
    plt.close()


    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True)
    parser.add_argument('directories', nargs='+')
    args = parser.parse_args()

    # Open the signac jobs
    project = signac.get_project()
    jobs = [project.open_job(id=directory) for directory in args.directories]

    # Call the action
    globals()[args.action](*jobs)
