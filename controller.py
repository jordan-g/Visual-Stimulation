from param_window import ParamWindow
from stim_window import StimWindow

import threading
import os
import shutil
import datetime
import json

from shared import *

class StimController():
    def __init__(self):
        print("Controller: Initializing.")

        self.running_stim = False # whether the stimulation is running
        self.begin_stim   = False # whether the stimulation needs to begin

        # troubleshooting mode - this determines whether external triggers
        # will affect the stimulation and stimulation parameters will be
        # saved to a text file
        self.troubleshooting = True

        # load saved experiments
        self.load_experiments()

        # load experiment parameters for the current experiment
        self.load_experiment_params()

        # load saved configs
        self.load_configs()

        # load config parameters for the current config
        self.load_config_params()

        # initialize param & stim windows
        self.param_window = None
        self.stim_window  = None

        # start threads for param & stim windows
        self.param_thread = threading.Thread(target=self.create_param_window)
        self.stim_thread  = threading.Thread(target=self.create_stim_window)
        self.param_thread.start()
        self.stim_thread.start()

    def load_experiments(self):
        print("Controller: Loading experiments.")

        # stop any running stim
        self.running_stim = False

        # sete xperiments file
        self.experiments_file = "experiments.json"

        try:
            # load experiments
            with open(self.experiments_file, "r") as input_file:
                self.experiments = json.load(input_file)
        except:
            # if none exist, create & save a default experiment
            self.experiments = {'experiments_list': ['Default Experiment'],
                                'current_experiment': 'Default Experiment'}
            self.save_experiments()

        print("Controller: Current experiment: {}.".format(self.experiments['current_experiment']))

    def save_experiments(self):
        print("Controller: Saving experiments in {}.".format(self.experiments_file))

        # save experiments to file
        with open(self.experiments_file, "w") as output_file:
            json.dump(self.experiments, output_file)

    def load_configs(self):
        print("Controller: Loading configs for {}.".format(self.experiments['current_experiment']))

        # stop any running stim
        self.running_stim = False

        # set path to current experiment
        self.current_experiment_folder = self.experiments['current_experiment']

        # set configs file
        self.configs_file = "configs.json"

        # set path to configs file
        self.configs_path = os.path.join(self.current_experiment_folder, self.configs_file)

        try:
            # load configs
            with open(self.configs_path, "r") as input_file:
                self.configs = json.load(input_file)
        except:
            # if none exist, create & save a default config
            self.configs = {'configs_list': ['Default Config'],
                           'current_config': 'Default Config'}
            self.save_configs()

        print("Controller: Current config: {}.".format(self.configs['current_config']))

    def save_configs(self):
        print("Controller: Saving configs in {}.".format(self.configs_path))

        # save configs to file
        with open(self.configs_path, "w") as output_file:
            json.dump(self.configs, output_file)

    def load_experiment_params(self):
        print("Controller: Loading experiment params for {}.".format(self.experiments['current_experiment']))

        # stop any running stim
        self.running_stim = False

        # set experiment folder
        self.current_experiment_folder = self.experiments['current_experiment']

        # create a folder if necessary
        if not os.path.exists(self.current_experiment_folder):
            print("A folder for the current experiment does not exist. Creating a new folder.")
            os.makedirs(self.current_experiment_folder)

        # set experiment params file
        self.experiment_params_file = "experiment_params.json"

        # set path to experiment params file
        self.experiment_params_path = os.path.join(self.current_experiment_folder, self.experiment_params_file)
       
        try:
            # load experiment params
            with open(self.experiment_params_path, "r") as input_file:
                self.experiment_params = json.load(input_file)

            # convert params to floats
            for key in self.experiment_params:
                try:
                    self.experiment_params[key] = float(self.experiment_params[key])
                except:
                    pass
        except:
            # if none exist, create & save a default set of experiment params
            self.experiment_params = DEFAULT_EXPERIMENT_PARAMS

            # calculate resolution param
            self.experiment_params['resolution'] = self.experiment_params['screen_px_width']/self.experiment_params['screen_cm_width']

            self.save_experiment_params()

    def save_experiment_params(self):
        print("Controller: Saving experiment params in {}.".format(self.experiment_params_path))

        # save experiment params to file
        with open(self.experiment_params_path, "w") as output_file:
            json.dump(self.experiment_params, output_file)

    def set_experiment_params(self, new_params):
        print("Controller: Setting experiment params.")

        # set experiment params dict to a new one
        self.experiment_params['screen_cm_width'] = new_params['screen_cm_width']
        self.experiment_params['screen_px_width'] = new_params['screen_px_width']
        self.experiment_params['distance']        = new_params['distance']
        self.experiment_params['width']           = new_params['width']
        self.experiment_params['height']          = new_params['height']
        self.experiment_params['x_offset']        = new_params['x_offset']
        self.experiment_params['y_offset']        = new_params['y_offset']

    def load_config_params(self):
        print("Controller: Loading config params for {}.".format(self.configs['current_config']))

        # stop any running stim
        self.running_stim = False

        # set config folder
        self.current_config_folder = os.path.join(self.current_experiment_folder, self.configs['current_config'])

        # create a folder if necessary
        if not os.path.exists(self.current_config_folder):
            print("A folder for the current config does not exist. Creating a new folder.")
            os.makedirs(self.current_config_folder)

        # set config params file
        self.config_params_file = "config_params.json"

        # set path to config params file
        self.config_params_path = os.path.join(self.current_config_folder, self.config_params_file)
       
        try:
            # load config params
            with open(self.config_params_path, "r") as input_file:
            	self.config_params = json.load(input_file)

            # convert params to floats
            for i, duration in enumerate(self.config_params['durations_list']):
                self.config_params['durations_list'][i] = float(duration)

            for i, params in enumerate(self.config_params['parameters_list']):
                for key in params:
                    try:
                        self.config_params['parameters_list'][i][key] = float(params[key])
                    except:
                        pass

            for key in self.config_params['TTL_params']:
                self.config_params['TTL_params'][key] = float(self.config_params['TTL_params'][key])

        except:
            # if none exist, create & save a default set of config params
            self.config_params = DEFAULT_CONFIG_PARAMS

            self.save_config_params()

    def save_config_params(self):
        print("Controller: Saving config params in {}.".format(self.config_params_path))

        # save config params to file
        with open(self.config_params_path, "w") as output_file:
        	json.dump(self.config_params, output_file)

    def create_param_window(self):
        print("Controller: Creating param window.")

        self.param_window = ParamWindow(self)

        # run param window
        self.param_window.run()

        print("Controller: Finished running param window.")

        self.param_window = None

    def create_stim_window(self):
        print("Controller: Creating stim window.")

        self.stim_window = StimWindow(self)

        # run stim window @ 60fps
        self.stim_window.Run(60)

        self.stim_window.stim = None

        self.stim_window.Dispose()

        print("Controller: Finished running stim window.")

        self.stim_window = None

    def start_stim(self, ignore_troubleshooting=False):
        if ignore_troubleshooting or not self.troubleshooting:
            print("Controller: Starting stim.")
            self.begin_stim   = True
            self.running_stim = True

            self.param_window.start_stop_button.Text = "Stop"

    def stop_stim(self, ignore_troubleshooting=False):
        if ignore_troubleshooting or not self.troubleshooting:
            print("Controller: Stopping stim.")

            self.begin_stim   = False
            self.running_stim = False

            self.param_window.start_stop_button.Text = "Start"

    def change_experiment(self, experiment_name):
        print("Controller: Changing experiment to {}.".format(experiment_name))

        # update experiments dict
        self.experiments['current_experiment'] = experiment_name

        # load experiment params
        self.load_experiment_params()

        # load configs for new experiment
        self.load_configs()

        # load config params
        self.load_config_params()

        # update stim params
        self.stim_window.update_params()

        # save new experiments dict
        self.save_experiments()

    def rename_experiment(self, old_experiment_name, new_experiment_name):
        print("Controller: Renaming experiment '{0}' to '{1}'.".format(old_experiment_name, new_experiment_name))

        # rename folder that corresponds to the experiment
        try:
            os.rename(old_experiment_name, new_experiment_name)
        except:
            return False

        # update experiments dict
        experiment_index = self.experiments['experiments_list'].index(old_experiment_name)
        self.experiments['experiments_list'][experiment_index] = new_experiment_name
        self.experiments['current_experiment'] = new_experiment_name

        # load experiment params
        self.load_experiment_params()

        # load configs for new experiment
        self.load_configs()

        # load config params
        self.load_config_params()

        # save new experiments dict
        self.save_experiments()

        return True

    def remove_experiment(self, experiment_name):
        print("Controller: Removing experiment '{}'.".format(experiment_name))

        try:
            # delete folder that corresponds to the experiment
            shutil.rmtree(experiment_name)
        except:
            return False

        # update experiments dict
        self.experiments['experiments_list'].remove(experiment_name)

        # switch to the previous experiment
        self.change_experiment(self.experiments['experiments_list'][-1])

        # save new experiments dict
        self.save_experiments()

        return True

    def change_config(self, config_name):
        print("Controller: Changing config to {}.".format(config_name))

        # update configs dict
        self.configs['current_config'] = config_name

        # load params for new config
        self.load_config_params()

        # update stim params
        self.stim_window.update_params()

        # save new configs dict
        self.save_configs()

    def rename_config(self, old_config_name, new_config_name):
        print("Controller: Renaming config '{0}' to '{1}'.".format(old_config_name, new_config_name))

        # rename folder that corresponds to the config
        try:
            old_config_folder = os.path.join(self.current_experiment_folder, old_config_name)
            new_config_folder = os.path.join(self.current_experiment_folder, new_config_name)
            os.rename(old_config_folder, new_config_folder)
        except:
            return False

        # update configs dict
        config_index = self.configs['configs_list'].index(old_config_name)
        self.configs['configs_list'][config_index] = new_config_name
        self.configs['current_config'] = new_config_name

        # load params for new config
        self.load_config_params()

        # save new configs dict
        self.save_configs()

        return True

    def remove_config(self, config_name):
        print("Controller: Removing config '{}'.".format(config_name))

        try:
            # delete folder that corresponds to the config
            config_folder = os.path.join(self.current_experiment_folder, config_name)
            shutil.rmtree(config_folder)
        except:
            return False

        # update configs dict
        self.configs['configs_list'].remove(config_name)

        # switch to the previous config
        self.change_config(self.configs['configs_list'][-1])

        # save new experiments dict
        self.save_configs()

        return True

    def add_stim(self, stim_name, stim_type, stim_duration, stim_params):
        print("Controller: Adding {0} stim '{1}'.".format(stim_type, stim_name))

        # add stim to experiment params dict
        self.config_params['stim_list'].append(stim_name)
        self.config_params['durations_list'].append(stim_duration)
        self.config_params['types_list'].append(stim_type)
        self.config_params['parameters_list'].append(stim_params)

        # update stim params
        self.stim_window.update_params()

    def remove_stim(self, stim_index):
        print("Controller: Removing stim at index {}.".format(stim_index))

        # remove stim from experiment params dict
        del self.config_params['stim_list'][stim_index]
        del self.config_params['durations_list'][stim_index]
        del self.config_params['types_list'][stim_index]
        del self.config_params['parameters_list'][stim_index]

        # reset stim index
        self.stim_window.stim_index = 0

        # create the first stim
        self.stim_window.create_stim()

        # update stim params
        self.stim_window.update_params()

    def change_param(self, param_dimension, change_in_param):
        self.stim_window.change_param(param_dimension, change_in_param)

    def default_stim_params(self, stim_type):
        # create new stim parameters
        if stim_type == "Looming Dot":
            stim_parameters = DEFAULT_LOOMING_DOT_PARAMS
        elif stim_type == "Moving Dot":
            stim_parameters = DEFAULT_MOVING_DOT_PARAMS
        elif stim_type == "Combined Dots":     ##Should give initial params?
            stim_parameters = DEFAULT_COMBINED_DOTS_PARAMS
        # elif stim_type == "Multiple Moving Dots":     ##Should give initial params?
        #   stim_parameters = {'dot_params': [{'radius': 10.0,     ##moving dot from here
        #                                           'moving_dot_init_x_pos': 0.0,
        #                                           'moving_dot_init_y_pos': 0.0,
        #                                           'v_x': 0.01,
        #                                           'v_y': 0.0,
        #                                           'l_v': 150,
        #                                           'moving_dot_brightness': 1.0},
        #                                           {'radius': 10.0,     ##moving dot from here
        #                                           'moving_dot_init_x_pos': 0.0,
        #                                           'moving_dot_init_y_pos': 0.0,
        #                                           'v_x': 0.01,
        #                                           'v_y': 0.0,
        #                                           'l_v': 150,
        #                                           'moving_dot_brightness': 1.0}]} ## moving dot to here
        elif stim_type == "Grating":
            stim_parameters = DEFAULT_GRATING_PARAMS
        elif stim_type in ("Delay", "Black Flash", "White Flash"):
            stim_parameters = {}

        return stim_parameters

    def default_stim_duration(self):
        return DEFAULT_STIM_DURATION

    def toggle_troubleshooting(self, sender=None, event=None):
        self.troubleshooting = not self.troubleshooting

        if self.troubleshooting == True:
            print("Troubleshooting mode enabled.")
        else:
            print("Troubleshooting mode disabled.")

    def close_windows(self):
        print("Controller: Closing windows.")

        # close param & stim windows
        if self.param_window:
            self.param_window.Close()
        if self.stim_window:
            self.stim_window.Exit()

        # close the threads
        self.param_thread.join()
        self.stim_thread.join()

        print("Controller: Closed all threads.")

# --- HELPER FUNCTIONS --- #

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_positive_number(s):
    return is_number(s) and float(s) > 0

def is_nonnegative_number(s):
    return is_number(s) and float(s) >= 0

def is_number_between_0_and_1(s):
    return is_number(s) and 0 <= float(s) <= 1

# ------------------------ #

def add_heading_label(text, panel):
    # add heading label
    label = Label()
    label.Parent = panel
    label.Text = text
    label.AutoSize = True
    label.Font = controller.HEADER_FONT
    label.Margin = Padding(0, 5, 0, 5)

def add_param_label(text, panel):
    # add param label
    label = Label()
    label.Parent = panel
    label.Text = text
    label.AutoSize = True
    label.Font = controller.BODY_FONT
    label.Margin = Padding(0, 5, 0, 0)
    label.Width = panel.Width
