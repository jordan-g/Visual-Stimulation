import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System import Array
from System.Windows.Forms import Application, Form, Panel, TableLayoutPanel, FlowLayoutPanel
from System.Windows.Forms import Button, Label, Control, ComboBox, TextBox, TrackBar
from System.Windows.Forms import AnchorStyles, DockStyle, FlowDirection, BorderStyle, ComboBoxStyle, Padding, FormBorderStyle, FormStartPosition, DialogResult
from System.Drawing import Color, Size, Font, FontStyle, Icon, SystemFonts, FontFamily, ContentAlignment

scale = 2

# set fonts
HEADER_FONT      = Font("Segoe UI", 9, FontStyle.Bold)
BODY_FONT        = Font("Segoe UI", 9, FontStyle.Regular)
BOLD_BODY_FONT   = Font("Segoe UI", 9, FontStyle.Bold)
ITALIC_BODY_FONT = Font("Segoe UI", 9, FontStyle.Italic)
ERROR_FONT       = Font("Segoe UI", 9, FontStyle.Bold)

# set colors
CHOICE_PANEL_COLOR = Color.WhiteSmoke
BUTTON_PANEL_COLOR = Color.WhiteSmoke
PARAM_PANEL_COLOR  = Color.White
BUTTON_COLOR       = Color.White
TEXTBOX_COLOR      = Color.WhiteSmoke
DIALOG_COLOR       = Color.White

# set stim color accents
LOOMING_DOT_COLOR = Color.PaleGreen
MOVING_DOT_COLOR  = Color.LightCoral
GRATING_COLOR     = Color.LightBlue
DELAY_COLOR       = Color.Gainsboro

# set default params for new experiments
DEFAULT_EXPERIMENT_PARAMS = {'screen_cm_width': 20,
                             'screen_px_width': 1280,
                             # 'distance': 30,
                             'width': 0.5,
                             'height': 0.5,
                             'x_offset': 0,
                             'y_offset': 0,
                             'dish_radius': 100,
                             'warp_perspective': True}

# set default params for loooming dot stim
DEFAULT_LOOMING_DOT_PARAMS = {'looming_dot_init_x_pos': 0,
                              'looming_dot_init_y_pos': 0,
                              'l_v': 20,                   ## edited from 150 to 20
                              'looming_dot_brightness': 1.0,
                              'background_brightness': 0,
                              'checkered': False,
                              'num_squares': 10,
                              'expand_checkered_pattern': True}

# set default params for moving dot stim
DEFAULT_MOVING_DOT_PARAMS = {'radius': 10.0,
                             'moving_dot_init_x_pos': 0.0,
                             'moving_dot_init_y_pos': 0.0,
                             'v_x': 1.0,
                             'v_y': 0.0,
                             'moving_dot_brightness': 1.0,
                             'background_brightness': 0}

# set default params for combined dots stim
DEFAULT_COMBINED_DOTS_PARAMS = {'radius': 10.0,
                                'moving_dot_init_x_pos': 0.0,
                                'looming_dot_init_x_pos': 0.0,
                                'moving_dot_init_y_pos': 0.0,
                                'looming_dot_init_y_pos': 0.0,
                                'v_x': 0.01,
                                'v_y': 0.0,
                                'l_v': 20,
                                'moving_dot_brightness': 1.0,
                                'looming_dot_brightness': 1.0,
                                'background_brightness': 0}

# set default params for OMR stim
#can I use init_phase for phase? does x just signify distance from converging line?
DEFAULT_OPTOMOTOR_GRATING_PARAMS = {'frequency': 0.2,
                          'init_phase': 0.0,
                          'merging_pos': 0.0, 
                          'velocity': 5,
                          'contrast': 1.0,
                          'brightness': 1.0,
                          'angle': 0,}

# set default params for grating stim
DEFAULT_GRATING_PARAMS = {'frequency': 0.2,
                          'init_phase': 0.0,
                          'velocity': 5,
                          'contrast': 1.0,
                          'brightness': 1.0,
                          'angle': 0}

# set default params for broadband grating stim
DEFAULT_BROADBAND_GRATING_PARAMS = {'frequency': 0.2,
                                    'init_phase': 0.0,
                                    'velocity': 5,
                                    'contrast': 1.0,
                                    'brightness': 1.0,
                                    'angle': 0}

# set default params for white flash stim
DEFAULT_WHITE_FLASH_PARAMS = {'brightness': 1.0}

##!!Set default params for OKR

# set default duration for new stims
DEFAULT_STIM_DURATION = 10

# set default TTL params for new configs
DEFAULT_TTL_PARAMS    = {'delay': 10,      # ms
                         'frequency': 50,  # Hz
                         'pulse_width': 1, # ms
                         'duration': 5}    # s

# set default params for new configs
DEFAULT_CONFIG_PARAMS = {'stim_list': ['Stim 1'],
                         'durations_list': [DEFAULT_STIM_DURATION],
                         'types_list': ['Looming Dot'],
                         'parameters_list': [DEFAULT_LOOMING_DOT_PARAMS],
                         'TTL_params': DEFAULT_TTL_PARAMS
                         }

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

def are_experiment_params_equal(experiment_params_1, experiment_params_2):
    experiment_params_are_equal = (experiment_params_1['screen_cm_width'] == experiment_params_2['screen_cm_width']
                               and experiment_params_1['screen_px_width'] == experiment_params_2['screen_px_width']
                               # and experiment_params_1['distance']        == experiment_params_2['distance']
                               and experiment_params_1['dish_radius']     == experiment_params_2['dish_radius']
                               and experiment_params_1['warp_perspective'] == experiment_params_2['warp_perspective']
                               and experiment_params_1['width']           == experiment_params_2['width']
                               and experiment_params_1['height']          == experiment_params_2['height']
                               and experiment_params_1['x_offset']        == experiment_params_2['x_offset']
                               and experiment_params_1['y_offset']        == experiment_params_2['y_offset'])

    return experiment_params_are_equal

# ------------------------ #

def stim_color(stim_type):
    # get color accent for the provided stim type
    if stim_type == "Looming Dot":
        color = LOOMING_DOT_COLOR
    elif stim_type == "Moving Dot":
        color = MOVING_DOT_COLOR
    elif stim_type == "Grating":
        color = GRATING_COLOR
    ##!! Add color for the OKR, can also do the same for combined stim, not absolutely necessary though
    else:
        color = DELAY_COLOR

    return color

def add_heading_label(text, panel):
    # add heading label
    label = Label()
    label.Parent = panel
    label.Text = text
    label.AutoSize = True
    label.Font = HEADER_FONT
    label.Margin = Padding(0, 5, 0, 5)

def add_param_label(text, panel):
    # add param label
    label = Label()
    label.Parent = panel
    label.Text = text
    label.AutoSize = True
    label.Font = BODY_FONT
    label.Margin = Padding(0, 5, 0, 0)
    label.Width = panel.Width
