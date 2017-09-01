import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System import Array
from System.Windows.Forms import Application, Form, Panel, TableLayoutPanel, FlowLayoutPanel, ControlStyles
from System.Windows.Forms import Button, Label, Control, ComboBox, TextBox, TrackBar, CheckBox, ToolTip
from System.Windows.Forms import AnchorStyles, DockStyle, FlowDirection, BorderStyle, ComboBoxStyle, Padding, FormBorderStyle, FormStartPosition, DialogResult
from System.Drawing import Color, Size, Font, FontStyle, Icon, SystemFonts, FontFamily, ContentAlignment

from name_dialog import ExperimentNameDialog, ConfigNameDialog
from stim_dialog import StimDialog
from ttl_dialog import TTLDialog
from confirmation_dialog import ConfirmationDialog

import time
import threading

# import shared constants & helper functions
from shared import *

class ParamWindow(Form):
    '''
    Parameter window class.
    This is the main window that is opened.
    '''

    def __init__(self, controller):
        # set controller
        self.controller = controller

        self.tooltip = ToolTip()

        # initialize invalid params label
        self.invalid_params_label = None

        # initialize total time label
        self.total_time_label = None

        # set window details
        self.Text = 'Parameters'
        self.StartPosition = FormStartPosition.Manual
        self.FormBorderStyle = FormBorderStyle.FixedSingle
        self.Top = 30
        self.Left = 30
        self.AutoSize = True
        self.closing = False

        # create dialogs
        self.experiment_name_dialog = ExperimentNameDialog()
        self.config_name_dialog = ConfigNameDialog()
        self.stim_dialog = StimDialog()
        self.TTL_dialog = TTLDialog()
        self.confirmation_dialog = ConfirmationDialog()

        # add & populate stim list panel
        self.add_stim_list_panel()
        self.populate_stim_list_panel()

        # add & populate config button panel
        self.add_config_button_panel()
        self.populate_config_button_panel()

        # add & populate config choice panel
        self.add_config_choice_panel()
        self.populate_config_choice_panel()

        # add & populate exp param panel
        self.add_exp_param_panel()
        self.populate_exp_param_panel()

        # add exp choice panel
        self.add_exp_choice_panel()

        # add save button panel
        self.add_save_button_panel()

        Application.EnableVisualStyles()

    def add_exp_choice_panel(self):
        # add exp button panel
        self.exp_button_panel = FlowLayoutPanel()
        self.exp_button_panel.Parent = self
        self.exp_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.exp_button_panel.Padding = Padding(10, 0, 10, 10)
        self.exp_button_panel.Dock = DockStyle.Top
        self.exp_button_panel.FlowDirection = FlowDirection.LeftToRight
        self.exp_button_panel.WrapContents = False
        self.exp_button_panel.AutoSize = True
        self.exp_button_panel.Font = BODY_FONT

        # add new exp button
        new_exp_button = Button()
        new_exp_button.Parent = self.exp_button_panel
        new_exp_button.Text = "New"
        new_exp_button.AutoSize = True
        new_exp_button.Click += self.add_new_experiment
        new_exp_button.BackColor = BUTTON_COLOR

        # add remove exp button
        self.remove_exp_button = Button()
        self.remove_exp_button.Parent = self.exp_button_panel
        self.remove_exp_button.Text = "Delete"
        self.remove_exp_button.AutoSize = True
        self.remove_exp_button.Click += self.remove_experiment
        self.remove_exp_button.BackColor = BUTTON_COLOR

        # disable remove exp button if there is only one experiment
        if len(self.controller.experiments['experiments_list']) == 1:
            self.remove_exp_button.Enabled = False

        # add rename exp button
        rename_exp_button = Button()
        rename_exp_button.Parent = self.exp_button_panel
        rename_exp_button.Text = "Rename"
        rename_exp_button.AutoSize = True
        rename_exp_button.Click += self.rename_experiment
        rename_exp_button.BackColor = BUTTON_COLOR

        # create exp choice panel
        self.exp_choice_panel = FlowLayoutPanel()
        self.exp_choice_panel.Parent = self
        self.exp_choice_panel.BackColor = CHOICE_PANEL_COLOR
        self.exp_choice_panel.Dock = DockStyle.Top
        self.exp_choice_panel.Padding = Padding(10, 10, 0, 10)
        self.exp_choice_panel.FlowDirection = FlowDirection.TopDown
        self.exp_choice_panel.WrapContents = False
        self.exp_choice_panel.AutoSize = True
        self.exp_choice_panel.Font = BODY_FONT

        # add exp choice label
        exp_choice_label = Label()
        exp_choice_label.Parent = self.exp_choice_panel
        exp_choice_label.Text = "Experiment:"
        exp_choice_label.AutoSize = True

        # add exp chooser
        self.exp_chooser = ComboBox()
        self.exp_chooser.DropDownStyle = ComboBoxStyle.DropDownList
        self.exp_chooser.Parent = self.exp_choice_panel
        self.exp_chooser.Items.AddRange(Array[str](self.controller.experiments['experiments_list']))
        self.exp_chooser.SelectionChangeCommitted += self.on_exp_choice
        self.exp_chooser.Text = self.controller.experiments['current_experiment']
        self.exp_chooser.Width = self.Width - 35
        self.exp_chooser.AutoSize = True
        self.exp_chooser.Font = BODY_FONT

    def on_exp_choice(self, sender, event):
        # get new exp name
        new_exp_name = self.exp_chooser.SelectedItem.ToString()

        if new_exp_name != self.controller.experiments['current_experiment']:
            # change experiment
            self.controller.change_experiment(new_exp_name)

            # refresh panels
            self.exp_param_panel.Refresh()
            self.config_choice_panel.Refresh()
            self.config_button_panel.Refresh()
            self.stim_list_panel.Refresh()

            # re-populate exp param, config choice, config button & stim list panels
            self.populate_exp_param_panel()
            self.populate_config_choice_panel()
            self.populate_config_button_panel()
            self.populate_stim_list_panel()

            # re-populate config chooser
            self.config_chooser.Items.Clear()
            self.config_chooser.Items.AddRange(Array[str](self.controller.configs['configs_list']))
            self.config_chooser.Text = self.controller.configs['current_config']

            # disable remove config button if there's only one config
            if len(self.controller.configs['configs_list']) == 1:
                self.remove_config_button.Enabled = False

    def add_new_experiment(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Creating a new experiment will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            # get new experiment name
            new_exp_name = self.experiment_name_dialog.ShowDialog(self.controller, "Add New Experiment", "New experiment name:", "New Experiment", None)

            if new_exp_name != None:
                # add experiment to experiments list
                self.controller.experiments['experiments_list'].append(new_exp_name)

                # switch to the new experiment
                self.controller.change_experiment(new_exp_name)

                # add & switch to new experiment in the exp chooser
                self.exp_chooser.Items.Add(new_exp_name)
                self.exp_chooser.Text = self.controller.experiments['current_experiment']

                # refresh panels
                self.exp_param_panel.Refresh()
                self.config_choice_panel.Refresh()
                self.config_button_panel.Refresh()
                self.stim_list_panel.Refresh()

                # re-populate exp param, config choice, config button & stim list panels
                self.populate_exp_param_panel()
                self.populate_config_choice_panel()
                self.populate_config_button_panel()
                self.populate_stim_list_panel()

                # enable the remove experiment button
                self.remove_exp_button.Enabled = True

    def remove_experiment(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Removing this experiment will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            # remove experiment from experiments dict
            success = self.controller.remove_experiment(self.exp_chooser.SelectedItem.ToString())
            if success:
                # remove experiment from exp chooser & switch to the new current experiment
                self.exp_chooser.Items.Remove(self.exp_chooser.SelectedItem)
                self.exp_chooser.Text = self.controller.experiments['current_experiment']

                # refresh panels
                self.exp_param_panel.Refresh()
                self.config_choice_panel.Refresh()
                self.config_button_panel.Refresh()
                self.stim_list_panel.Refresh()

                # re-populate exp param, config choice, config button & stim list panels
                self.populate_exp_param_panel()
                self.populate_config_choice_panel()
                self.populate_config_button_panel()
                self.populate_stim_list_panel()

                # disable remove experiment button if there's only one experiment left
                if len(self.controller.experiments['experiments_list']) == 1:
                    self.remove_exp_button.Enabled = False

    def rename_experiment(self, sender, event):
        # get old experiment name
        old_exp_name = self.exp_chooser.SelectedItem.ToString()

        # get new experiment name
        new_exp_name = self.experiment_name_dialog.ShowDialog(self.controller, "Rename experiment","New experiment name:", old_exp_name, self.controller.experiments['experiments_list'].index(old_exp_name))
        
        if new_exp_name != None:
            # rename the experiment
            success = self.controller.rename_experiment(old_exp_name, new_exp_name)

            if success:
                # rename the experiment in the exp chooser
                exp_index = self.exp_chooser.Items.IndexOf(old_exp_name)
                self.exp_chooser.Items.Item[exp_index] = new_exp_name
                self.exp_chooser.Text = self.controller.experiments['current_experiment']

    def add_exp_param_panel(self):
        # create exp param panel
        self.exp_param_panel = FlowLayoutPanel()
        self.exp_param_panel.Parent = self
        self.exp_param_panel.BackColor = PARAM_PANEL_COLOR
        self.exp_param_panel.Dock = DockStyle.Top
        self.exp_param_panel.Padding = Padding(10)
        self.exp_param_panel.FlowDirection = FlowDirection.LeftToRight
        self.exp_param_panel.WrapContents = True
        # self.exp_param_panel.Height = 250
        self.exp_param_panel.AutoSize = True
        self.exp_param_panel.Font = BODY_FONT

    def populate_exp_param_panel(self):
        # initialize exp param textboxes, sliders & slider labels dicts
        self.exp_param_textboxes = {}
        self.exp_param_sliders   = {}
        self.exp_param_slider_labels = {}

        # empty exp param panel
        list_of_controls = self.exp_param_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.exp_param_panel.Controls.Clear()

        # add exp param heading label
        # add_heading_label("Experiment Parameters", self.exp_param_panel)
        
        # add exp params
        self.add_exp_param_to_window('screen_cm_width', 'Screen width (cm)')
        self.add_exp_param_to_window('screen_px_width', 'Screen width (px)')
        self.add_exp_param_to_window('distance', 'Screen distance (cm)', tooltip="The perpendicular distance from the screen to the eye of the mouse, in centimeters.")

        self.add_exp_param_slider_to_window('width', 'Viewport width', 1, 100)
        self.add_exp_param_slider_to_window('height', 'Viewport height', 1, 100)

        # add filler subpanel
        exp_param_subpanel = FlowLayoutPanel()
        exp_param_subpanel.Parent = self.exp_param_panel
        exp_param_subpanel.BackColor = PARAM_PANEL_COLOR
        exp_param_subpanel.Dock = DockStyle.Bottom
        exp_param_subpanel.Padding = Padding(0)
        exp_param_subpanel.FlowDirection = FlowDirection.TopDown
        exp_param_subpanel.WrapContents = False
        exp_param_subpanel.Width = int(self.Width/3) - 20
        exp_param_subpanel.Height = 50
        # exp_param_subpanel.AutoSize = True
        exp_param_subpanel.Font = BODY_FONT

        self.add_exp_param_slider_to_window('x_offset', 'Viewport x offset', 0, 100)
        self.add_exp_param_slider_to_window('y_offset', 'Viewport y offset', 0, 100)

    def add_exp_param_to_window(self, name, label_text, tooltip=None):
        # create exp param panel
        exp_param_subpanel = FlowLayoutPanel()
        exp_param_subpanel.Parent = self.exp_param_panel
        exp_param_subpanel.BackColor = PARAM_PANEL_COLOR
        exp_param_subpanel.Dock = DockStyle.Bottom
        exp_param_subpanel.Padding = Padding(0)
        exp_param_subpanel.FlowDirection = FlowDirection.TopDown
        exp_param_subpanel.WrapContents = False
        exp_param_subpanel.Width = int(self.Width/3) - 15
        exp_param_subpanel.Height = 50
        # exp_param_subpanel.AutoSize = True
        exp_param_subpanel.Font = BODY_FONT

        # add param label
        label = Label()
        label.Parent = exp_param_subpanel
        label.Text = label_text + ":"
        label.AutoSize = True
        label.Font = BODY_FONT
        label.Margin = Padding(0, 5, 0, 0)
        label.Width = exp_param_subpanel.Width

        # add param textbox
        self.exp_param_textboxes[name] = TextBox()
        self.exp_param_textboxes[name].Parent = exp_param_subpanel
        self.exp_param_textboxes[name].Text = str(self.controller.experiment_params[name])
        self.exp_param_textboxes[name].Width = int(self.Width/3) - 20
        self.exp_param_textboxes[name].BackColor = BUTTON_PANEL_COLOR
        self.exp_param_textboxes[name].Font = BODY_FONT

        if tooltip is not None:
            self.tooltip.SetToolTip(label, tooltip)

    def add_exp_param_slider_to_window(self, name, label_text, min, max):
        # create exp param panel
        exp_param_subpanel = FlowLayoutPanel()
        exp_param_subpanel.Parent = self.exp_param_panel
        exp_param_subpanel.BackColor = PARAM_PANEL_COLOR
        exp_param_subpanel.Dock = DockStyle.Bottom
        exp_param_subpanel.Padding = Padding(0)
        exp_param_subpanel.FlowDirection = FlowDirection.TopDown
        exp_param_subpanel.WrapContents = False
        exp_param_subpanel.Width = int(self.Width/3) - 15
        exp_param_subpanel.Height = 50
        # exp_param_subpanel.AutoSize = True
        exp_param_subpanel.Font = BODY_FONT

        # add param label
        self.exp_param_slider_labels[name] = Label()
        self.exp_param_slider_labels[name].Parent = exp_param_subpanel
        self.exp_param_slider_labels[name].Text = label_text + ": " + str(self.controller.experiment_params[name])
        self.exp_param_slider_labels[name].AutoSize = True
        self.exp_param_slider_labels[name].Font = BODY_FONT
        self.exp_param_slider_labels[name].Margin = Padding(0, 5, 0, 0)
        self.exp_param_slider_labels[name].Name = label_text

        # add param slider
        self.exp_param_sliders[name] = TrackBar()
        self.exp_param_sliders[name].Parent = exp_param_subpanel
        self.exp_param_sliders[name].Minimum = min
        self.exp_param_sliders[name].Maximum = max
        self.exp_param_sliders[name].Value = float(self.controller.experiment_params[name])*100.0
        self.exp_param_sliders[name].Width = int(self.Width/3) - 20
        self.exp_param_sliders[name].Name = name
        self.exp_param_sliders[name].TickFrequency = 100
        self.exp_param_sliders[name].Scroll += self.on_slider_scroll

    def on_slider_scroll(self, sender, event):
        self.exp_param_slider_labels[sender.Name].Text = self.exp_param_slider_labels[sender.Name].Name + ": " + str(sender.Value/100.0)

        # update stim window's params
        if self.controller.stim_window:
            if self.controller.running_stim:
                confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Changing experiment paremeters will stop the currently-running stimulation. Continue?")
            else:
                confirmation = True

            if confirmation:
                # stop any running stim
                self.controller.stop_stim(ignore_troubleshooting=True)
                
                self.controller.experiment_params[sender.Name] = sender.Value/100.0
                self.controller.save_experiment_params()

                self.controller.stim_window.update_params()

    def add_config_choice_panel(self):
        # create config choice panel
        self.config_choice_panel = FlowLayoutPanel()
        self.config_choice_panel.Parent = self
        self.config_choice_panel.BackColor = CHOICE_PANEL_COLOR
        self.config_choice_panel.Dock = DockStyle.Top
        self.config_choice_panel.Padding = Padding(10, 10, 0, 10)
        self.config_choice_panel.FlowDirection = FlowDirection.TopDown
        self.config_choice_panel.WrapContents = False
        self.config_choice_panel.AutoSize = True
        self.config_choice_panel.Font = BODY_FONT

    def populate_config_choice_panel(self):
        # empty config choice panel
        list_of_controls = self.config_choice_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.config_choice_panel.Controls.Clear()

        # add config choice label
        config_choice_label = Label()
        config_choice_label.Parent = self.config_choice_panel
        config_choice_label.Text = "Config:"
        config_choice_label.AutoSize = True

        # add config chooser
        self.config_chooser = ComboBox()
        self.config_chooser.DropDownStyle = ComboBoxStyle.DropDownList
        self.config_chooser.Parent = self.config_choice_panel
        self.config_chooser.Items.AddRange(Array[str](self.controller.configs['configs_list']))
        self.config_chooser.SelectionChangeCommitted += self.on_config_choice
        self.config_chooser.Text = self.controller.configs['current_config']
        self.config_chooser.Width = self.Width - 35
        self.config_chooser.AutoSize = True
        self.config_chooser.Font = BODY_FONT

    def on_config_choice(self, sender, event):
        # get new config name
        new_config_name = self.config_chooser.SelectedItem.ToString()

        if new_config_name != self.controller.configs['current_config']:
            # refresh panel
            self.stim_list_panel.Refresh()

            # change config
            self.controller.change_config(new_config_name)

            # re-populate stim list panel
            self.populate_stim_list_panel()

    def add_config_button_panel(self):
        # add config button panel
        self.config_button_panel = FlowLayoutPanel()
        self.config_button_panel.Parent = self
        self.config_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.config_button_panel.Padding = Padding(10, 0, 10, 10)
        self.config_button_panel.Dock = DockStyle.Top
        self.config_button_panel.FlowDirection = FlowDirection.LeftToRight
        self.config_button_panel.WrapContents = False
        self.config_button_panel.AutoSize = True
        self.config_button_panel.Font = BODY_FONT

    def populate_config_button_panel(self):
        # empty config button panel
        list_of_controls = self.config_button_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.config_button_panel.Controls.Clear()

        # add new config button
        new_config_button = Button()
        new_config_button.Parent = self.config_button_panel
        new_config_button.Text = "New"
        new_config_button.Click += self.add_new_config
        new_config_button.BackColor = BUTTON_COLOR
        new_config_button.AutoSize = True

        # add remove config button
        self.remove_config_button = Button()
        self.remove_config_button.Parent = self.config_button_panel
        self.remove_config_button.Text = "Delete"
        self.remove_config_button.Click += self.remove_config
        self.remove_config_button.BackColor = BUTTON_COLOR
        self.remove_config_button.AutoSize = True
        if len(self.controller.configs['configs_list']) == 1:
            self.remove_config_button.Enabled = False

        # add rename config button
        rename_config_button = Button()
        rename_config_button.Parent = self.config_button_panel
        rename_config_button.Text = "Rename"
        rename_config_button.Click += self.rename_config
        rename_config_button.BackColor = BUTTON_COLOR
        rename_config_button.AutoSize = True

    def add_new_config(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Creating a new configuration will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            # get new config name
            new_config_name = self.config_name_dialog.ShowDialog(self.controller, "Add New Config", "New config name:", "New Config", None)

            if new_config_name != None:
                # add config to configs list
                self.controller.configs['configs_list'].append(new_config_name)

                # switch to the new config
                self.controller.change_config(new_config_name)

                # add & switch to new config in the exp chooser
                self.config_chooser.Items.Add(new_config_name)
                self.config_chooser.Text = self.controller.configs['current_config']

                # refresh panel
                self.stim_list_panel.Refresh()

                # re-populate stim list panel
                self.populate_stim_list_panel()

                # enable the remove config button
                self.remove_config_button.Enabled = True

                list_of_controls = self.stim_list_panel.Controls
                for control in list_of_controls:
                    index = self.stim_list_panel.Controls.IndexOf(control)

    def remove_config(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Removing this configuration will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            # remove config from configs dict
            success = self.controller.remove_config(self.config_chooser.SelectedItem.ToString())
            if success:
                # remove config from exp chooser & switch to the new current config
                self.config_chooser.Items.Remove(self.config_chooser.SelectedItem)
                self.config_chooser.Text = self.controller.configs['current_config']

                # refresh panel
                self.stim_list_panel.Refresh()

                # re-populate stim list panel
                self.populate_stim_list_panel()

                # disable remove config button if there's only one config left
                if len(self.controller.configs['configs_list']) == 1:
                    self.remove_config_button.Enabled = False

                list_of_controls = self.stim_list_panel.Controls
                for control in list_of_controls:
                    index = self.stim_list_panel.Controls.IndexOf(control)

    def rename_config(self, sender, event):
        # get old config name
        old_config_name = self.config_chooser.SelectedItem.ToString()

        # get new config name
        new_config_name = self.config_name_dialog.ShowDialog(self.controller, "Rename Config","New config name:", old_config_name, self.controller.configs['configs_list'].index(old_config_name))
        
        if new_config_name != None:
            # rename the config
            success = self.controller.rename_config(old_config_name, new_config_name)

            if success:
                # rename the config in the exp chooser
                config_index = self.config_chooser.Items.IndexOf(old_config_name)
                self.config_chooser.Items.Item[config_index] = new_config_name
                self.config_chooser.Text = self.controller.configs['current_config']

    def add_stim_list_panel(self):
        # create stim list panel
        self.stim_list_panel = FlowLayoutPanel()
        self.stim_list_panel.Parent = self
        self.stim_list_panel.BackColor = PARAM_PANEL_COLOR
        self.stim_list_panel.Dock = DockStyle.Fill
        self.stim_list_panel.Padding = Padding(10)
        self.stim_list_panel.FlowDirection = FlowDirection.TopDown
        self.stim_list_panel.WrapContents = False
        self.stim_list_panel.AutoScroll = True
        # self.stim_list_panel.Width = self.Width
        self.stim_list_panel.MaximumSize = Size(0, 300)
        self.stim_list_panel.AutoSize = True
        self.stim_list_panel.Font = BODY_FONT

    def populate_stim_list_panel(self):
        # stop the param window from refreshing
        self.SuspendLayout()

        self.stim_list_panel.Visible = False

        # empty stim list panel
        list_of_controls = self.stim_list_panel.Controls
        for control in list_of_controls:
            control.Dispose()
        self.stim_list_panel.Controls.Clear()

        # initialize lists of controls
        self.stim_list_subpanels       = []
        self.stim_list_duration_labels = []
        self.stim_list_name_labels     = []
        self.stim_list_type_labels     = []
        self.stim_list_edit_buttons    = []
        self.stim_list_delete_buttons  = []

        # add all stims
        for i in range(len(self.controller.config_params['stim_list'])):
            self.add_stim_to_stim_list_panel(i)

        self.stim_list_panel.Visible = True

        # allow the param window to refresh
        self.ResumeLayout()

        # update total time label
        self.update_total_time_label()

    def add_stim_to_stim_list_panel(self, i):
        # create stim subpanel
        subpanel = FlowLayoutPanel()
        subpanel.Parent = self.stim_list_panel
        subpanel.Dock = DockStyle.Left
        subpanel.Padding = Padding(0)
        subpanel.Margin = Padding(1, 0, 1, 1)
        subpanel.FlowDirection = FlowDirection.LeftToRight
        subpanel.WrapContents = False
        subpanel.AutoSize = True
        subpanel.Font = BODY_FONT
        subpanel.Tag = i

        # get stim type
        stim_type = self.controller.config_params['types_list'][i]

        # add edit button
        edit_button = Button()
        edit_button.Parent = subpanel
        edit_button.Text = "Edit"
        edit_button.AutoSize = True
        edit_button.Click += self.edit_stim
        edit_button.BackColor = BUTTON_COLOR

        # add edit button to list of edit buttons
        self.stim_list_edit_buttons.append(edit_button)

        # add delete button
        delete_button = Button()
        delete_button.Parent = subpanel
        delete_button.Text = "Delete"
        delete_button.AutoSize = True
        delete_button.Click += self.remove_stim
        delete_button.BackColor = BUTTON_COLOR

        # add delete button to list of delete buttons
        self.stim_list_delete_buttons.append(delete_button)

        # add stim name label
        stim_name_label = Label()
        stim_name_label.Parent = subpanel
        stim_name_label.Text = self.controller.config_params['stim_list'][i]
        stim_name_label.MinimumSize = Size(220, 40)
        stim_name_label.MaximumSize = Size(220, 40)
        stim_name_label.AutoSize = True
        stim_name_label.Padding = Padding(0, 7, 0, 0)
        stim_name_label.AutoEllipsis = True

        # add stim name label to list of stim name labels
        self.stim_list_name_labels.append(stim_name_label)

        # add stim type label
        stim_type_label = Label()
        stim_type_label.Parent = subpanel
        stim_type_label.Text = stim_type
        stim_type_label.MinimumSize = Size(100, 40)
        stim_type_label.MaximumSize = Size(100, 40)
        stim_type_label.AutoEllipsis = True
        stim_type_label.AutoSize = True
        stim_type_label.Padding = Padding(0, 7, 0, 0)

        # add stim type label to list of stim type labels
        self.stim_list_type_labels.append(stim_type_label)

        # add duration label
        duration_label = Label()
        duration_label.Parent = subpanel
        duration_label.Text = str(self.controller.config_params['durations_list'][i]) + "s"
        duration_label.MinimumSize = Size(100, 40)
        duration_label.MaximumSize = Size(100, 40)
        duration_label.AutoSize = True
        duration_label.Padding = Padding(0, 7, 0, 0)

        # add duration label to list of duration labels
        self.stim_list_duration_labels.append(duration_label)

        # add move up button
        move_up_button = Button()
        move_up_button.Parent = subpanel
        move_up_button.Text = u"\u02C4"
        move_up_button.MaximumSize = Size(40, 0)
        move_up_button.AutoSize = True
        move_up_button.Click += self.move_up_stim
        move_up_button.BackColor = BUTTON_COLOR

        # add move down button
        move_down_button = Button()
        move_down_button.Parent = subpanel
        move_down_button.Text = u"\u02C5"
        move_down_button.MaximumSize = Size(40, 0)
        move_down_button.AutoSize = True
        move_down_button.Click += self.move_down_stim
        move_down_button.BackColor = BUTTON_COLOR

        # add color accent
        edit_button.BackColor = stim_color(stim_type)

        # add subpanel to list of subpanels
        self.stim_list_subpanels.append(subpanel)

    def move_up_stim(self, sender, event):
        if len(self.controller.config_params['stim_list']) > 0:
            if self.controller.running_stim:
                confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Rearranging stimulations will stop the currently-running stimulation. Continue?")
            else:
                confirmation = True

            if confirmation:
                # stop any running stim
                self.controller.stop_stim(ignore_troubleshooting=True)

                # get stim index
                stim_index = sender.Parent.Tag

                if stim_index != 0:
                    # rearrange subpanels
                    self.stim_list_panel.Controls.SetChildIndex(self.stim_list_panel.Controls[stim_index-1], stim_index)

                    # rearrange tags
                    self.stim_list_panel.Controls[stim_index-1].Tag -= 1
                    self.stim_list_panel.Controls[stim_index].Tag += 1
                    
                    # update lists of controls
                    self.stim_list_subpanels[stim_index], self.stim_list_subpanels[stim_index-1] = self.stim_list_subpanels[stim_index-1], self.stim_list_subpanels[stim_index]
                    self.stim_list_duration_labels[stim_index], self.stim_list_duration_labels[stim_index-1] = self.stim_list_duration_labels[stim_index-1], self.stim_list_duration_labels[stim_index]
                    self.stim_list_name_labels[stim_index], self.stim_list_name_labels[stim_index-1] = self.stim_list_name_labels[stim_index-1], self.stim_list_name_labels[stim_index]
                    self.stim_list_type_labels[stim_index], self.stim_list_type_labels[stim_index-1] = self.stim_list_type_labels[stim_index-1], self.stim_list_type_labels[stim_index]
                    self.stim_list_edit_buttons[stim_index], self.stim_list_edit_buttons[stim_index-1] = self.stim_list_edit_buttons[stim_index-1], self.stim_list_edit_buttons[stim_index]
                    self.stim_list_delete_buttons[stim_index], self.stim_list_delete_buttons[stim_index-1] = self.stim_list_delete_buttons[stim_index-1], self.stim_list_delete_buttons[stim_index]

                    # update config params
                    self.controller.config_params['stim_list'][stim_index], self.controller.config_params['stim_list'][stim_index-1] = self.controller.config_params['stim_list'][stim_index-1], self.controller.config_params['stim_list'][stim_index]
                    self.controller.config_params['durations_list'][stim_index], self.controller.config_params['durations_list'][stim_index-1] = self.controller.config_params['durations_list'][stim_index-1], self.controller.config_params['durations_list'][stim_index]
                    self.controller.config_params['types_list'][stim_index], self.controller.config_params['types_list'][stim_index-1] = self.controller.config_params['types_list'][stim_index-1], self.controller.config_params['types_list'][stim_index]
                    self.controller.config_params['parameters_list'][stim_index], self.controller.config_params['parameters_list'][stim_index-1] = self.controller.config_params['parameters_list'][stim_index-1], self.controller.config_params['parameters_list'][stim_index]

                    # update stim window's params
                    if self.controller.stim_window:
                        self.controller.stim_window.update_params()

    def move_down_stim(self, sender, event):
        if len(self.controller.config_params['stim_list']) > 0:
            if self.controller.running_stim:
                confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Rearranging stimulations will stop the currently-running stimulation. Continue?")
            else:
                confirmation = True

            if confirmation:
                # stop any running stim
                self.controller.stop_stim(ignore_troubleshooting=True)

                # get stim index
                stim_index = sender.Parent.Tag

                if stim_index != self.stim_list_panel.Controls.Count - 1:
                    # rearrange subpanels
                    self.stim_list_panel.Controls.SetChildIndex(self.stim_list_panel.Controls[stim_index+1], stim_index)

                    # rearrange tags
                    self.stim_list_panel.Controls[stim_index+1].Tag += 1
                    self.stim_list_panel.Controls[stim_index].Tag -= 1
                    
                    # update lists of controls
                    self.stim_list_subpanels[stim_index], self.stim_list_subpanels[stim_index+1] = self.stim_list_subpanels[stim_index+1], self.stim_list_subpanels[stim_index]
                    self.stim_list_duration_labels[stim_index], self.stim_list_duration_labels[stim_index+1] = self.stim_list_duration_labels[stim_index+1], self.stim_list_duration_labels[stim_index]
                    self.stim_list_name_labels[stim_index], self.stim_list_name_labels[stim_index+1] = self.stim_list_name_labels[stim_index+1], self.stim_list_name_labels[stim_index]
                    self.stim_list_type_labels[stim_index], self.stim_list_type_labels[stim_index+1] = self.stim_list_type_labels[stim_index+1], self.stim_list_type_labels[stim_index]
                    self.stim_list_edit_buttons[stim_index], self.stim_list_edit_buttons[stim_index+1] = self.stim_list_edit_buttons[stim_index+1], self.stim_list_edit_buttons[stim_index]
                    self.stim_list_delete_buttons[stim_index], self.stim_list_delete_buttons[stim_index+1] = self.stim_list_delete_buttons[stim_index+1], self.stim_list_delete_buttons[stim_index]

                    # update config params
                    self.controller.config_params['stim_list'][stim_index], self.controller.config_params['stim_list'][stim_index+1] = self.controller.config_params['stim_list'][stim_index+1], self.controller.config_params['stim_list'][stim_index]
                    self.controller.config_params['durations_list'][stim_index], self.controller.config_params['durations_list'][stim_index+1] = self.controller.config_params['durations_list'][stim_index+1], self.controller.config_params['durations_list'][stim_index]
                    self.controller.config_params['types_list'][stim_index], self.controller.config_params['types_list'][stim_index+1] = self.controller.config_params['types_list'][stim_index+1], self.controller.config_params['types_list'][stim_index]
                    self.controller.config_params['parameters_list'][stim_index], self.controller.config_params['parameters_list'][stim_index+1] = self.controller.config_params['parameters_list'][stim_index+1], self.controller.config_params['parameters_list'][stim_index]

                    # update stim window's params
                    if self.controller.stim_window:
                        self.controller.stim_window.update_params()

    def remove_stim(self, sender, event):
        if len(self.controller.config_params['stim_list']) > 0:
            if self.controller.running_stim:
                confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Removing this stimulation will stop the currently-running stimulation. Continue?")
            else:
                confirmation = True

            if confirmation:
                # stop any running stim
                self.controller.stop_stim(ignore_troubleshooting=True)

                # stop the param window from refreshing
                self.SuspendLayout()

                # get stim index
                stim_index = sender.Parent.Tag

                # remove stim
                self.stim_list_panel.Controls.RemoveAt(stim_index)
                del self.stim_list_subpanels[stim_index]
                del self.stim_list_duration_labels[stim_index]
                del self.stim_list_name_labels[stim_index]
                del self.stim_list_type_labels[stim_index]
                del self.stim_list_edit_buttons[stim_index]
                del self.stim_list_delete_buttons[stim_index]

                # adjust indices of remaining stims
                for i in range(stim_index, len(self.stim_list_subpanels)):
                    self.stim_list_subpanels[i].Tag -= 1

                # remove stim from experiment params
                del self.controller.config_params['stim_list'][stim_index]
                del self.controller.config_params['durations_list'][stim_index]
                del self.controller.config_params['types_list'][stim_index]
                del self.controller.config_params['parameters_list'][stim_index]

                # update stim window's params
                if self.controller.stim_window:
                    self.controller.stim_window.update_params()

                # allow the param window to refresh
                self.ResumeLayout()

                # update total time label
                self.update_total_time_label()

    def edit_stim(self, sender, event):
        # get stim index
        stim_index = sender.Parent.Tag

        # show stim dialog
        success = self.stim_dialog.ShowDialog(self.controller, stim_index)

        print(success)

        if success:
            self.controller.stop_stim(ignore_troubleshooting=True)

            # stop the param window from refreshing
            self.SuspendLayout()

            # update stim subpanel controls
            self.stim_list_name_labels[stim_index].Text = str(self.controller.config_params['stim_list'][stim_index])
            self.stim_list_duration_labels[stim_index].Text = str(self.controller.config_params['durations_list'][stim_index]) + "s"

            # get stim type
            stim_type = self.controller.config_params['types_list'][stim_index]

            # update stim type label
            self.stim_list_type_labels[stim_index].Text = str(stim_type)

            # add color accent
            self.stim_list_edit_buttons[stim_index].BackColor = stim_color(stim_type)

            # allow the param window to refresh
            self.ResumeLayout()

            # update total time label
            self.update_total_time_label()

    def add_save_button_panel(self):
        # create save button panel
        self.save_button_panel = FlowLayoutPanel()
        self.save_button_panel.Parent = self
        self.save_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.save_button_panel.Dock = DockStyle.Bottom
        self.save_button_panel.Padding = Padding(10)
        self.save_button_panel.WrapContents = False
        self.save_button_panel.AutoSize = True
        self.save_button_panel.Font = BODY_FONT

        # add new stim button
        self.add_stim_button = Button()
        self.add_stim_button.Parent = self.save_button_panel
        self.add_stim_button.Text = "Add Stim"
        self.add_stim_button.Click += self.add_stim
        self.add_stim_button.BackColor = BUTTON_COLOR
        self.add_stim_button.AutoSize = True

        # add save button
        self.save_button = Button()
        self.save_button.Parent = self.save_button_panel
        self.save_button.Text = "Save"
        self.save_button.Click += self.save_experiment_params
        self.save_button.BackColor = BUTTON_COLOR
        self.save_button.AutoSize = True

        self.AcceptButton = self.save_button

        # add start/stop button
        self.start_stop_button = Button()
        self.start_stop_button.Parent = self.save_button_panel
        self.start_stop_button.Text = "Start"
        self.start_stop_button.Click += self.start_stop_stim
        self.start_stop_button.BackColor = BUTTON_COLOR
        self.start_stop_button.AutoSize = True

        # add edit TTL params button
        self.ttl_button = Button()
        self.ttl_button.Parent = self.save_button_panel
        self.ttl_button.Text = "TTL"
        self.ttl_button.Click += self.edit_TTL_params
        self.ttl_button.BackColor = BUTTON_COLOR
        self.ttl_button.AutoSize = True

        # add troubleshooting checkbox
        self.troubleshooting_checkbox = CheckBox()
        self.troubleshooting_checkbox.Parent = self.save_button_panel
        self.troubleshooting_checkbox.Checked = self.controller.troubleshooting
        self.troubleshooting_checkbox.CheckedChanged += self.controller.toggle_troubleshooting
        self.troubleshooting_checkbox.Text = "Troubleshooting"
        self.troubleshooting_checkbox.AutoSize = True

        # create save button panel
        self.button_panel_2 = FlowLayoutPanel()
        self.button_panel_2.Parent = self
        self.button_panel_2.BackColor = BUTTON_PANEL_COLOR
        self.button_panel_2.Dock = DockStyle.Bottom
        self.button_panel_2.Padding = Padding(10)
        self.button_panel_2.WrapContents = False
        self.button_panel_2.AutoSize = True
        self.button_panel_2.Font = BODY_FONT

        # add stimulation progress indicator
        self.progress_label = Label()
        self.progress_label.Parent = self.save_button_panel
        self.progress_label.Text = ""
        self.progress_label.Width = 200
        self.progress_label.ForeColor = Color.Red
        self.progress_label.Padding = Padding(5)
        self.progress_label.AutoSize = True
        self.progress_label.Font = ITALIC_BODY_FONT

        # add display chooser label
        self.display_chooser_label = Label()
        self.display_chooser_label.Parent = self.button_panel_2
        self.display_chooser_label.Text = "Show stimulation on:"
        self.display_chooser_label.Padding = Padding(5)
        self.display_chooser_label.AutoSize = True

        # add display chooser
        self.display_chooser = ComboBox()
        self.display_chooser.DropDownStyle = ComboBoxStyle.DropDownList
        self.display_chooser.Parent = self.button_panel_2
        display_options = ["Monitor", "Projector"]
        self.display_chooser.Items.AddRange(Array[str](["Monitor", "Projector"]))
        self.display_chooser.SelectionChangeCommitted += self.on_display_choice
        self.display_chooser.SelectedItem = display_options[self.controller.display_index]
        self.display_chooser.Width = 100
        self.display_chooser.BackColor = BUTTON_PANEL_COLOR
        self.display_chooser.Font = BODY_FONT

        # add total time indicator
        self.total_time_label = Label()
        self.total_time_label.Parent = self.button_panel_2
        self.total_time_label.Text = "Total Time: {}s".format(sum(self.controller.config_params['durations_list']))
        self.total_time_label.Width = 200
        self.total_time_label.Padding = Padding(5)
        self.total_time_label.Font = ITALIC_BODY_FONT

    def update_total_time_label(self):
        if self.total_time_label:
            self.total_time_label.Text = "Total Time: {}s".format(sum(self.controller.config_params['durations_list']))

    def on_display_choice(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Changing where the stimulation is displayed will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            self.controller.restart_stim_window(display_index=["Monitor", "Projector"].index(self.display_chooser.SelectedItem.ToString()))

    def add_stim(self, sender, event):
        if self.controller.running_stim:
            confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Adding a stimulation will stop the currently-running stimulation. Continue?")
        else:
            confirmation = True

        if confirmation:
            # stop any running stim
            self.controller.stop_stim(ignore_troubleshooting=True)

            # show stim dialog
            success = self.stim_dialog.ShowDialog(self.controller, None)

            if success:
                # stop the param window from refreshing
                self.SuspendLayout()

                # add stim subpanel
                self.add_stim_to_stim_list_panel(len(self.controller.config_params['stim_list'])-1)

                # allow the param window to refresh
                self.ResumeLayout()

                # update total time label
                self.update_total_time_label()

    def save_experiment_params(self, sender, event):
        print("ParamWindow: Saving experiment params.")

        # get contents of param textboxes
        self.exp_param_values         = {key: value.Text for (key, value) in self.exp_param_textboxes.items()}
        self.exp_param_slider_values  = {key: value.Value/100.0 for (key, value) in self.exp_param_sliders.items()}

        self.exp_param_values.update(self.exp_param_slider_values)

        if self.are_valid_params(self.exp_param_values):
            # create new parameters dicts
            new_exp_params = {key: float(value) for (key, value) in self.exp_param_values.items()}

            if not are_experiment_params_equal(self.controller.experiment_params, new_exp_params):
                if self.controller.running_stim:
                    confirmation = self.confirmation_dialog.ShowDialog(self.controller, "Stop Current Stimulation?", "Editing the experiment parameters will stop the currently-running stimulation. Continue?")
                else:
                    confirmation = True

                if confirmation:
                    # stop any running stim
                    self.controller.stop_stim(ignore_troubleshooting=True)

                    # set experiment params to new params & save them
                    self.controller.set_experiment_params(new_exp_params)
                    self.controller.save_experiment_params()
                    self.controller.save_experiments()
                    self.controller.save_configs()
                    self.controller.save_config_params()

                    # update stim window's params
                    if self.controller.stim_window:
                        self.controller.stim_window.update_params()
        else:
            print("invalid")
            # the params are invalid; add invalid params text
            self.add_invalid_params_text()

    def start_stop_stim(self, sender, event):
        if self.controller.running_stim:
            self.controller.stop_stim(ignore_troubleshooting=True)
        else:
            self.controller.start_stim(ignore_troubleshooting=True)

    def edit_TTL_params(self, sender, event):
        # show TTL dialog
        success = self.TTL_dialog.ShowDialog(self.controller)

    def are_valid_params(self, exp_params):
        # check that all of the params are valid
        exp_params_are_valid = (is_positive_number(exp_params['screen_px_width'])
                                and is_positive_number(exp_params['screen_cm_width'])
                                and is_positive_number(exp_params['distance'])
                                and is_positive_number(exp_params['width'])
                                and is_positive_number(exp_params['height'])
                                and is_nonnegative_number(exp_params['x_offset'])
                                and is_nonnegative_number(exp_params['y_offset']))

        return exp_params_are_valid

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

    def run(self):
        Application.Run(self)

    def OnFormClosing(self, e):
        print("ParamWindow: Closing.")

        self.experiment_name_dialog = None
        self.config_name_dialog = None
        self.stim_dialog = None

        # save experiment params
        self.save_experiment_params(self, None)

        self.controller.close_windows()
