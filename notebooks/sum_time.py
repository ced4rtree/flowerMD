import glob
import numpy
import os

# calculate total compute time from the tps and amount of steps from each log file
total_time = 0
for log_dir in glob.glob("notebooks/*logs"):
    for log_run in glob.glob(f'{log_dir}/*'):
        if os.path.exists(f"{log_run}/log.txt"):
            log = numpy.genfromtxt(f"{log_run}/log.txt", names=True)
            if os.path.exists(f"{log_run}/parameters.txt"):
                with open(fr"{log_run}/parameters.txt", 'r') as parameter_file:
                    parameters = parameter_file.readlines()
                    steps_index = 0
                    for parameter in parameters:
                        if parameter.find("shrink_steps") != -1:
                            steps_index = parameters.index(parameter)
                        tps_arr = log["flowermdbasesimulationSimulationtps"]
                        tps_arr = tps_arr[tps_arr != 0]
                        if (len(tps_arr) != 0):
                            steps = float(parameters[steps_index].split()[-1])
                            runtime = (steps / len(tps_arr)) / tps_arr
                            total_time += numpy.sum(runtime)

print("Total runtime (s): ", total_time)
print("Total runtime (m): ", total_time / 60)
print("Total runtime (h): ", total_time / 60 / 60)
