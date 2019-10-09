'''
Code for opening visual stimulation software, starting/stopping
the stimulation by analyzing external signal from the scope's TTL box,
and saving frame timestamps and stimulus details.

The TTL box outputs a HIGH signal by default, a LOW signal while imaging,
and a brief HIGH signal after every frame is captured:


         imaging start     imaging end
                +                 +
                |                 |
                v                 v

HIGH +----------+  +-+  +-+  +-+  +-----------+
                |  | |  | |  | |  |
                |  | |  | |  | |  |
 LOW            +--+ +--+ +--+ +--+

The Bonsai workflow takes this signal (Item 1), and creates two new
signals, one that skips 99 data points (Item 2), and one that skips 100
data points (Item 3). All three signals are compared to determine when
imaging starts, when each frame is gathered, and when imaging stops.
'''

print("Importing modules.")

# import Keys
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import Keys
from System import Tuple

# import StimController
import sys
import os
import datetime
sys.path.append(os.path.join(os.getcwd(), "Visual-Stimulation"))
from controller import StimController

def load():
    print("Loading.")
    # create stim controller
    global stim_controller
    stim_controller = StimController()

imaging    = False # whether the scope is currently imaging
stopped    = True  # whether the stimulation is stopped
filename_2 = ""    # filename for saving timestamp data
filename   = ""    # filename for saving experiment param data

file_2 = None
file   = None

start_time = None

def process(value):
    global imaging
    global stopped
    global stim_controller
    global filename_2
    global filename
    global file_2
    global file
    global start_time

    if not imaging and value.Item1 < 100 and not stim_controller.troubleshooting and not stim_controller.running_stim:
        # start the stimulation if the user starts imaging and the stim isn't running
        imaging = True
        stopped = False

        time = datetime.datetime.now()
        
        start_time = time
        delta = start_time - time

        stim_controller.start_stim()

        # Save a file containing the experiment parameters

        experiments = stim_controller.experiments
        configs = stim_controller.configs
        experiment_params = stim_controller.experiment_params
        config_params = stim_controller.config_params

        # generate filename for experiment params file
        original_filename = "{}.{}.{} {}.{} - experiment params".format(time.year, time.month, time.day, time.hour, time.minute)
        filename = original_filename + ".txt"

        filename_append_number = 1

        while os.path.isfile(os.path.join(os.getcwd(), filename)):
            filename = original_filename + " ({}).txt".format(filename_append_number)

            filename_append_number += 1

        # generate filename for timestamps file
        original_filename = "{}.{}.{} {}.{} - timestamps".format(time.year, time.month, time.day, time.hour, time.minute)
        filename_2 = original_filename + ".txt"

        filename_append_number = 1

        while os.path.isfile(os.path.join(os.getcwd(), filename_2)):
            filename_2 = original_filename + " ({}).csv".format(filename_append_number)

            filename_append_number += 1

        file = open(filename, "a")

        file.write("Start Time: {}/{}/{} {}:{}:{}\n\n".format(time.year, time.month, time.day, time.hour, time.minute, time.second))

        file.write("Experiment: {}\n".format(experiments["current_experiment"]))

        file.write("Config: {}\n".format(configs["current_config"]))

        file.write("\n")

        file.write("Experiment Params:\n")
        for i in range(len(experiment_params.keys())):
            file.write("    {}: {}\n".format(experiment_params.keys()[i], experiment_params.values()[i]))

        for i in range(len(config_params["stim_list"])):
            file.write("\n")

            file.write("{} ({}) Params:\n".format(config_params["stim_list"][i], config_params["types_list"][i]))
            file.write("    duration: {}\n".format(config_params["durations_list"][i]))

            for j in range(len(config_params["parameters_list"][i])):
                p = config_params["parameters_list"][i]
                file.write("    {}: {}\n".format(p.keys()[j], p.values()[j]))

        file_2 = open(filename_2, "a")

        # file_2.write("ms: {}, stimulation start\n\n".format(int(delta.total_seconds() * 1000)))

        file_2.write("time (ms),stim #,stim name,stim type,stim params\n")
        file_2.write("{},-1,start,None,None\n".format(int(delta.total_seconds() * 1000)))
    elif imaging and not stim_controller.troubleshooting and value.Item3 > 1000 and value.Item3 - value.Item1 < 100:
        # imaging has ended
        imaging = False
        stopped = True

        time = datetime.datetime.now()
        delta = time - start_time

        stim_controller.stop_stim()

        file.write("\nImaging End Time: {}/{}/{} {}:{}:{}\n\n".format(time.year, time.month, time.day, time.hour, time.minute, time.second))

        # file_2.write("\nms: {}, imaging end\n\n".format(int(delta.total_seconds() * 1000)))

        file_2.write("{},-1,end,None,None\n".format(int(delta.total_seconds() * 1000)))

        file.close()
        file_2.close()

        file = None
        file_2 = None
    elif imaging and not stim_controller.troubleshooting and value.Item3 < 10 and value.Item1 - value.Item2 > 900:
        # a frame has been collected
        time = datetime.datetime.now()
        delta = time - start_time

        stim_state, keys = stim_controller.current_stim_state()

        stim_state_string = "; ".join([ "{}: {}".format(keys[i], stim_state[keys[i]]) for i in range(len(keys)) if keys[i] not in ("stim #", "stim name", "stim type") ])

        # file_2.write("ms: {}, {}\n".format(int(delta.total_seconds() * 1000), stim_state_string))

        file_2.write("{},{},{},{},{}\n".format(int(delta.total_seconds() * 1000), stim_state["stim #"], stim_state["stim name"], stim_state["stim type"], stim_state_string))
    elif not stim_controller.running_stim and imaging and not stopped and not stim_controller.troubleshooting:
        stopped = True
        # stop recording if the stimulation stops
        time = datetime.datetime.now()
        delta = time - start_time

        file.write("\nStim End Time: {}/{}/{} {}:{}:{}\n\n".format(time.year, time.month, time.day, time.hour, time.minute, time.second))

        # file_2.write("\nms: {}, stimulation end\n\n".format(int(delta.total_seconds() * 1000)))

        file_2.write("{},-1,stim end,None,None\n".format(int(delta.total_seconds() * 1000)))
    return

def unload():
    try:
        # close everything
        print("Unloading controller.")
        global stim_controller
        stim_controller.param_window.Close()

        if file is not None:
            file.close()
        if file_2 is not None:
            file_2.close()

        file = None
        file_2 = None
    except:
        pass