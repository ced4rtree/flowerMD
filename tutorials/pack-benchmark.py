print('0')
from flowermd.base import Pack, Simulation
print('1')
from flowermd.library import PPS, BeadSpring
print('2')
import time
print('3')

NUM_MOLS=100
print('4')
NUM_POLS=100
print('4.5')
pps_mol = PPS(num_mols=NUM_MOLS, lengths=NUM_POLS)
print('5')
pps_mol.coarse_grain(beads={"A": "c1ccc(S)cc1"})
print('6')

print('7')
ff = BeadSpring(
    r_cut=2.5,
    beads={
        "A": dict(epsilon=1, sigma=0.2),
    },
    bonds={
        "A-A": dict(r0=0.64, k=500),
    },
    angles={"A-A-A": dict(t0=2.8, k=50)},
)

start_time = time.perf_counter()
print('8')
cg_system = Pack(molecules=pps_mol, density=0.01, edge=2, overlap=2)
print('9')
cg_sim = Simulation(
    initial_state=cg_system.hoomd_snapshot,
    forcefield=ff.hoomd_forces,
    gsd_write_freq=int(2e4),
)
print('10')

target_box = get_target_box_number_density(
    density=0.85, n_beads=NUM_MOLS*NUM_POLS
)
print('11')

print('12')
ellipsoid_sim.run_update_volume(
    final_box_lengths=target_box,
    kT=1.0,
    n_steps=int(5e4),
    tau_kt=10 * ellipsoid_sim.dt,
    period=10,
    thermalize_particles=True,
)
print('13')
end_time = time.perf_counter()
print('14')
print(f"Simulation took {end_time-start_time} seconds.")
