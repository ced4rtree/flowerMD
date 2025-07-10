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
                    shrink_steps_index = 0
                    static_steps_index = 0
                    for parameter in parameters:
                        if parameter.find("shrink_steps") != -1:
                            shrink_steps_index = parameters.index(parameter)
                        if parameter.find("static_steps") != -1:
                            static_steps_index = parameters.index(parameter)
                        tps_arr = log["flowermdbasesimulationSimulationtps"]
                        tps_arr = tps_arr[tps_arr != 0]
                        shrink_steps = float(parameters[shrink_steps_index].split()[-1])
                        static_steps = float(parameters[static_steps_index].split()[-1])
                        total_steps = shrink_steps + static_steps
                        if (len(tps_arr) != 0):
                            runtime = (total_steps / len(tps_arr)) / tps_arr
                            total_time += numpy.sum(runtime)

print("Total runtime (s): ", total_time)
print("Total runtime (m): ", total_time / 60)
print("Total runtime (h): ", total_time / 60 / 60)
