import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System import Array
from System.Windows.Forms import Application, Form, Panel, TableLayoutPanel, FlowLayoutPanel
from System.Windows.Forms import Button, Label, Control, ComboBox, TextBox, TrackBar
from System.Windows.Forms import AnchorStyles, DockStyle, FlowDirection, BorderStyle, ComboBoxStyle, Padding, FormBorderStyle, FormStartPosition, DialogResult
from System.Drawing import Color, Size, Font, FontStyle, Icon, SystemFonts, FontFamily, ContentAlignment

# import shared constants & helper functions
from shared import *

class StimDialog():
    '''
    Dialog window for setting stim parameters.
    Used when creating or editing a stimulus.
    '''

    def ShowDialog(self, controller, stim_index):
        # set controller
        self.controller = controller

        # initialize success bool
        self.success = False

        # initialize invalid params label
        self.invalid_params_label = None

        # create a dictionary to save stim parameters for different stim types
        # as the user changes parameters & types of stimuli in this dialog.
        # If the user switches from looming dot to moving dot and back,
        # the previous settings for the looming dot can be restored.
        self.saved_stim_parameters = {}

        if stim_index != None:
            # we are editing an existing stim; get the stim params
            self.i = stim_index
            self.stim_name = self.controller.config_params['stim_list'][self.i]
            self.stim_type = self.controller.config_params['types_list'][self.i]
            self.stim_duration = self.controller.config_params['durations_list'][self.i]
            self.stim_parameters = self.controller.config_params['parameters_list'][self.i]

        else:
            # we are creating a new stim; make new stim params
            self.i = len(self.controller.config_params['stim_list'])
            self.stim_name = "Stim {0}".format(self.i + 1)
            self.stim_type = 'Looming Dot'
            self.stim_duration = self.controller.default_stim_duration()
            self.stim_parameters = self.controller.default_stim_params(self.stim_type)

            # add the stim to the config params
            self.controller.add_stim(self.stim_name, self.stim_type, self.stim_duration, self.stim_parameters)

        # save a copy of the initial stim params so we can restore them later
        self.saved_stim_parameters[self.stim_type] = self.controller.config_params['parameters_list'][self.i]

        # create the form
        self.dialog_window = Form()
        self.dialog_window.FormBorderStyle = FormBorderStyle.FixedSingle
        self.dialog_window.Text = "{} Parameters".format(self.stim_name)
        self.dialog_window.StartPosition = FormStartPosition.CenterScreen
        self.dialog_window.Width = 400

        # add & populate stim param panel
        self.add_stim_param_panel()
        self.populate_stim_param_panel()

        # add & populate stim choice panel
        self.add_stim_choice_panel()
        self.populate_stim_choice_panel()

        # add save button panel
        self.add_save_button_panel()

        # auto-size the window
        self.dialog_window.AutoSize = True

        # show the dialog
        self.dialog_window.ShowDialog()
        
        # return success boolean
        return self.success

    def add_stim_choice_panel(self):
        # create stim choice panel
        self.stim_choice_panel = FlowLayoutPanel()
        self.stim_choice_panel.Parent = self.dialog_window
        self.stim_choice_panel.BackColor = CHOICE_PANEL_COLOR
        self.stim_choice_panel.Dock = DockStyle.Top
        self.stim_choice_panel.Padding = Padding(10)
        self.stim_choice_panel.FlowDirection = FlowDirection.TopDown
        self.stim_choice_panel.WrapContents = False
        self.stim_choice_panel.AutoSize = True
        self.stim_choice_panel.Font = BODY_FONT

    def populate_stim_choice_panel(self):
        # empty stim choice panel
        list_of_controls = self.stim_choice_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.stim_choice_panel.Controls.Clear()

        # add stim choice label
        stim_choice_label = Label()
        stim_choice_label.Parent = self.stim_choice_panel
        stim_choice_label.Text = "Stim:"
        stim_choice_label.AutoSize = True

        # add stim chooser
        self.stim_chooser = ComboBox()
        self.stim_chooser.DropDownStyle = ComboBoxStyle.DropDownList
        self.stim_chooser.Parent = self.stim_choice_panel
        self.stim_chooser.Items.AddRange(("Looming Dot", "Moving Dot", "Combined Dots", "Grating", "Delay", "Black Flash", "White Flash"))  ##!! need to add option for OKR here
        self.stim_chooser.SelectionChangeCommitted += self.on_stim_choice
        self.stim_chooser.Text = self.stim_type
        self.stim_chooser.Width = self.dialog_window.Width - 40
        self.stim_chooser.AutoSize = True
        self.stim_chooser.Font = Font(BODY_FONT.FontFamily, 18)

    def add_stim_param_panel(self):
        # create stim param panel
        self.stim_param_panel = FlowLayoutPanel()
        self.stim_param_panel.Parent = self.dialog_window
        self.stim_param_panel.BackColor = PARAM_PANEL_COLOR
        self.stim_param_panel.Dock = DockStyle.Top
        self.stim_param_panel.Padding = Padding(10)
        self.stim_param_panel.FlowDirection = FlowDirection.TopDown
        self.stim_param_panel.WrapContents = False
        self.stim_param_panel.AutoScroll = True
        self.stim_param_panel.Font = BODY_FONT
        self.stim_param_panel.AutoSize = True
        self.stim_param_panel.MaximumSize = Size(0, 500)

    def populate_stim_param_panel(self):
        # empty stim param panel
        list_of_controls = self.stim_param_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.stim_param_panel.Controls.Clear()
        
        # initialize stim param text controls dict
        self.stim_param_textboxes = {}

        # add name label & textbox
        add_param_label('Name:', self.stim_param_panel)
        self.name_textbox = TextBox()
        self.name_textbox.Parent = self.stim_param_panel
        self.name_textbox.Text = str(self.stim_name)
        self.name_textbox.AutoSize = True
        self.name_textbox.BackColor = BUTTON_PANEL_COLOR
        self.name_textbox.Font = Font(BODY_FONT.FontFamily, 18)

        # add duration label & textbox
        add_param_label('Duration (s):', self.stim_param_panel)
        self.duration_textbox = TextBox()
        self.duration_textbox.Parent = self.stim_param_panel
        self.duration_textbox.Text = str(self.stim_duration)
        self.duration_textbox.AutoSize = True
        self.duration_textbox.BackColor = BUTTON_PANEL_COLOR
        self.duration_textbox.Font = Font(BODY_FONT.FontFamily, 18)

        # add parameters heading label
        if self.stim_type not in ("Delay", "Black Flash", "White Flash"):
            add_heading_label("{} Parameters".format(self.stim_type), self.stim_param_panel)

        # add param labels & textboxes
        if self.stim_type == "Looming Dot":
            self.add_stim_param_to_window('looming_dot_init_x_pos', 'Initial x position (deg)')
            self.add_stim_param_to_window('looming_dot_init_y_pos', 'Initial y position (deg)')
            self.add_stim_param_to_window('l_v', 'l/v (ms)')
            self.add_stim_param_to_window('looming_dot_brightness', 'Dot brightness (0 - 1)') #Will need to change to brightness ie moving dot
            self.add_stim_param_to_window('background_brightness', 'Background brightness (0 - 1)')     #here is the background_brightness problem
##            self.add_stim_param_to_window('background', ' Background (0-1)')##Will add option to change background
        elif self.stim_type == "Moving Dot":
            self.add_stim_param_to_window('radius', 'Radius (px)')
            self.add_stim_param_to_window('moving_dot_init_x_pos', 'Initial x position (deg)')
            self.add_stim_param_to_window('moving_dot_init_y_pos', 'Initial y position (deg)')
            self.add_stim_param_to_window('v_x', 'Horiz. velocity (deg/s)')
            self.add_stim_param_to_window('v_y', 'Vertical velocity (deg/s)')
            self.add_stim_param_to_window('moving_dot_brightness', 'Dot brightness (0 - 1)')
            self.add_stim_param_to_window('background_brightness', 'Background brightness (0 - 1)')
        elif self.stim_type == "Combined Dots":
##            ##Looming                     won't allow all of this, needs to fit window
            add_heading_label("Looming Dot Parameters", self.stim_param_panel)
            self.add_stim_param_to_window('looming_dot_init_x_pos', 'Initial x position (deg)')
            self.add_stim_param_to_window('looming_dot_init_y_pos', 'Initial y position (deg)')
            self.add_stim_param_to_window('l_v', 'l/v (ms)')
            self.add_stim_param_to_window('looming_dot_brightness', 'Contrast (0 - 1)') #changed brightness from contrast
            ##moving
            add_heading_label("Moving Dot Parameters", self.stim_param_panel)
            self.add_stim_param_to_window('radius', 'Radius (px)')
            self.add_stim_param_to_window('moving_dot_init_x_pos', 'Initial x position (deg)')
            self.add_stim_param_to_window('moving_dot_init_y_pos', 'Initial y position (deg)')
            self.add_stim_param_to_window('v_x', 'Horiz. velocity (deg/s)')
            self.add_stim_param_to_window('v_y', 'Vertical velocity (deg/s)')
            self.add_stim_param_to_window('moving_dot_brightness', 'Contrast (0 - 1)')
            self.add_stim_param_to_window('background_brightness', 'Background brightness (0-1)')
        elif self.stim_type == "Grating":
            self.add_stim_param_to_window('frequency', 'Spatial frequency (1/deg)')
            self.add_stim_param_to_window('init_phase', 'Initial phase (deg)')
            self.add_stim_param_to_window('velocity', 'Velocity (deg/s)')
            self.add_stim_param_to_window('contrast', 'Contrast (0 - 1)')
        ##!!Need a self.stim_type for OKR
        elif self.stim_type in ("Delay", "Black Flash", "White Flash"):
            pass

    def add_stim_param_to_window(self, name, label_text):
        # add param label
        add_param_label(label_text + ':', self.stim_param_panel)

        # add param textbox
        self.stim_param_textboxes[name] = TextBox()
        self.stim_param_textboxes[name].Parent = self.stim_param_panel
        self.stim_param_textboxes[name].Text = str(self.stim_parameters[name])
        self.stim_param_textboxes[name].AutoSize = True
        self.stim_param_textboxes[name].BackColor = TEXTBOX_COLOR
        self.stim_param_textboxes[name].Font = Font(BODY_FONT.FontFamily, 18)

    def on_stim_choice(self, sender, event):
        # stop the dialog window from refreshing
        self.dialog_window.SuspendLayout()

        # save a copy of the current stim params for the currently selected stim type
        self.stim_param_textbox_values = {key: value.Text for (key, value) in self.stim_param_textboxes.items()}
        self.saved_stim_parameters[self.stim_type] = {key: float(value) for (key, value) in self.stim_param_textbox_values.items()}

        # get selected stim type
        new_stim_type = self.stim_chooser.SelectedItem.ToString()

        if new_stim_type != self.stim_type:
            # update stim type
            self.stim_type = new_stim_type

            if new_stim_type in self.saved_stim_parameters:
                # we have previously set parameters for this stim type; restore these
                self.stim_parameters = self.saved_stim_parameters[self.stim_type]
            else:
                # create new default stim parameters
                self.stim_parameters = self.controller.default_stim_params(self.stim_type)

            # refresh panel
            self.stim_choice_panel.Refresh()

            self.stim_choice_panel.BackColor = stim_color(self.stim_type)

            # populate stim param panel
            self.populate_stim_param_panel()

        # allow the dialog window to refresh
        self.dialog_window.ResumeLayout()

    def add_save_button_panel(self):
        # create save button panel
        self.save_button_panel = FlowLayoutPanel()
        self.save_button_panel.Parent = self.dialog_window
        self.save_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.save_button_panel.Dock = DockStyle.Bottom
        self.save_button_panel.Padding = Padding(10)
        self.save_button_panel.WrapContents = False
        self.save_button_panel.AutoSize = True
        self.save_button_panel.Font = BODY_FONT

        # add save button
        self.save_button = Button()
        self.save_button.Parent = self.save_button_panel
        self.save_button.Text = "Save"
        self.save_button.Click += self.on_save_button_click
        self.save_button.BackColor = BUTTON_COLOR
        self.save_button.AutoSize = True

        # save button is activated when user presses Enter
        self.dialog_window.AcceptButton = self.save_button

        # add close button
        self.close_button = Button()
        self.close_button.Parent = self.save_button_panel
        self.close_button.Text = "Close"
        self.close_button.DialogResult = DialogResult.Cancel
        self.close_button.BackColor = BUTTON_COLOR
        self.close_button.AutoSize = True

    def on_save_button_click(self, sender, event):
        # save stim params
        self.success = self.save_stim_params(sender, event)

        if self.success:
            # saving was successful; close the window
            self.dialog_window.Close()

    def save_stim_params(self, sender, event):
        # stop any running stim
        self.controller.stop_stim()

        # get contents of param textboxes
        self.stim_param_textbox_values = {key: value.Text for (key, value) in self.stim_param_textboxes.items()}
        name = self.name_textbox.Text
        duration = self.duration_textbox.Text
        type = self.stim_chooser.SelectedItem.ToString()
        
        if self.are_valid_params(type, self.stim_param_textbox_values) and is_nonnegative_number(duration):
            # the params are valid

            # remove any invalid params text
            self.remove_invalid_params_text()
            
            # create new parameters dicts
            new_stim_params = {key: float(value) for (key, value) in self.stim_param_textbox_values.items()}

            # update config params
            self.controller.config_params['stim_list'][self.i] = name
            self.controller.config_params['durations_list'][self.i] = float(duration)
            self.controller.config_params['types_list'][self.i] = type
            self.controller.config_params['parameters_list'][self.i] = new_stim_params

            # save config params
            self.controller.save_config_params()

            # update stim window's params
            if self.controller.stim_window:
                self.controller.stim_window.update_params()

            return True
        else:
            # the params are invalid; add invalid params text
            self.add_invalid_params_text()

            return False

    def are_valid_params(self, stim_type, stim_params):
        # check that all of the params are valid
        if stim_type == "Looming Dot":
            stim_params_are_valid = (is_number(stim_params['looming_dot_init_x_pos'])
                                     and is_number(stim_params['looming_dot_init_y_pos'])
                                     and is_positive_number(stim_params['l_v'])
                                     and is_number_between_0_and_1(stim_params['looming_dot_brightness'])
                                     and is_number_between_0_and_1(stim_params['background_brightness']))
        elif stim_type == "Moving Dot":
            stim_params_are_valid = (is_nonnegative_number(stim_params['radius'])
                                     and is_number(stim_params['moving_dot_init_x_pos'])
                                     and is_number(stim_params['moving_dot_init_y_pos'])
                                     and is_number(stim_params['v_x'])
                                     and is_number(stim_params['v_y'])
                                     and is_number_between_0_and_1(stim_params['moving_dot_brightness'])
                                     and is_number_between_0_and_1(stim_params['background_brightness']))
        elif stim_type == "Combined Dots":
            stim_params_are_valid = (is_nonnegative_number(stim_params['radius'])## moving dot from here
                                     and is_number(stim_params['moving_dot_init_x_pos'])
                                     and is_number(stim_params['moving_dot_init_y_pos'])
                                     and is_number(stim_params['v_x'])
                                     and is_number(stim_params['v_y'])
                                     and is_number_between_0_and_1(stim_params['moving_dot_brightness']) ## moving dot to here
                                     and is_number(stim_params['looming_dot_init_x_pos']) ## Looming dot from here
                                     and is_number(stim_params['looming_dot_init_y_pos'])
                                     and is_positive_number(stim_params['l_v'])
                                     and is_number_between_0_and_1(stim_params['looming_dot_brightness'])
                                     and is_number_between_0_and_1(stim_params['background_brightness']))  ## Loming dot to here                                     
        elif stim_type == "Grating":
            stim_params_are_valid = (is_positive_number(stim_params['frequency'])
                                     and is_number(stim_params['init_phase'])
                                     and is_number(stim_params['velocity'])
                                     and is_number_between_0_and_1(stim_params['contrast']))
        ##!! check valid params for OKR
        elif stim_type in ("Delay", "Black Flash", "White Flash"):
            stim_params_are_valid = True

        return stim_params_are_valid

    def add_invalid_params_text(self):
        if not self.invalid_params_label:
            # add invalid params label
            self.invalid_params_label = Label()
            self.invalid_params_label.Parent = self.save_button_panel
            self.invalid_params_label.Font = ERROR_FONT
            self.invalid_params_label.Padding = Padding(5)
            self.invalid_params_label.ForeColor = Color.Red
            self.invalid_params_label.AutoSize = True

        # set invalid param label text
        self.invalid_params_label.Text = "Invalid parameters."

    def remove_invalid_params_text(self):
        if self.invalid_params_label:
            # clear invalid param label text
            self.invalid_params_label.Text = ""
