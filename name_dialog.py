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

class ExperimentNameDialog():
    '''
    Dialog window for inputting an experiment name.
    Used when creating or renaming an experiment.
    '''

    def ShowDialog(self, controller, title, text, default_input, exp_index):
        # set controller
        self.controller = controller

        # set exp index
        self.exp_index = exp_index

        # initialize exp name variable
        self.exp_name = None

        # initialize invalid name label
        self.invalid_name_label = None

        # create the form
        self.dialog_window = Form()
        self.dialog_window.AutoSize = True
        self.dialog_window.Width = 400
        self.dialog_window.MaximumSize = Size(400, 220)
        self.dialog_window.StartPosition = FormStartPosition.CenterScreen
        self.dialog_window.Text = title
        self.dialog_window.FormBorderStyle = FormBorderStyle.FixedSingle

        # create the main panel
        self.panel = FlowLayoutPanel()
        self.panel.Parent = self.dialog_window
        self.panel.BackColor = DIALOG_COLOR
        self.panel.Dock = DockStyle.Top
        self.panel.Padding = Padding(10, 10, 0, 10)
        self.panel.FlowDirection = FlowDirection.TopDown
        self.panel.WrapContents = False
        self.panel.AutoSize = True
        self.panel.Font = BODY_FONT

        # add the dialog text
        exp_name_label = Label()
        exp_name_label.Parent = self.panel
        exp_name_label.Text = text
        exp_name_label.Width = self.panel.Width
        exp_name_label.AutoSize = True
        exp_name_label.Margin = Padding(0, 5, 0, 0)

        # add the textbox
        self.exp_name_box = TextBox()
        self.exp_name_box.Text = default_input
        self.exp_name_box.Parent = self.panel
        self.exp_name_box.Width = self.panel.Width - 30
        self.exp_name_box.AutoSize = True
        self.exp_name_box.BackColor = BUTTON_PANEL_COLOR
        self.exp_name_box.Font = Font(BODY_FONT.FontFamily, 18)

        # add save button panel
        self.add_save_button_panel()

        # show the dialog
        self.dialog_window.ShowDialog()

        # return the exp name
        return self.exp_name

    def add_save_button_panel(self):
        # create save button panel
        self.save_button_panel = FlowLayoutPanel()
        self.save_button_panel.Parent = self.dialog_window
        self.save_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.save_button_panel.Dock = DockStyle.Bottom
        self.save_button_panel.Padding = Padding(10, 0, 10, 10)
        self.save_button_panel.WrapContents = False
        self.save_button_panel.AutoSize = True
        self.save_button_panel.Font = BODY_FONT
        self.save_button_panel.FlowDirection = FlowDirection.LeftToRight

        # add save button
        self.save_button = Button()
        self.save_button.Parent = self.save_button_panel
        self.save_button.Text = "Save"
        self.save_button.Click += self.on_save_button_click
        self.save_button.BackColor = BUTTON_COLOR
        self.save_button.AutoSize = True

        # save button is activated when user presses Enter
        self.dialog_window.AcceptButton = self.save_button

    def on_save_button_click(self, sender, event):
        # get what's in the text box
        exp_name = self.exp_name_box.Text

        if self.exp_index == None:
            # we are creating a new experiment; check if none of the existing experiments have the same name
            success = not (exp_name in self.controller.experiments['experiments_list'])
        else:
            # we are renaming an experiment; check if none of the other experiments have the same name
            other_experiments = [exp for exp in self.controller.experiments['experiments_list'] if not exp == self.controller.experiments['experiments_list'][self.exp_index]]
            success = not (exp_name in other_experiments)

        if success:
            # the exp name is valid; set exp name & close the window
            self.exp_name = exp_name
            self.dialog_window.Close()
        else:
            # the exp name is invalid; add invalid name text
            self.add_invalid_name_text()

    def add_invalid_name_text(self):
        if not self.invalid_name_label:
            # add invalid name label
            self.invalid_name_label = Label()
            self.invalid_name_label.Parent = self.save_button_panel
            self.invalid_name_label.Font = ERROR_FONT
            self.invalid_name_label.Padding = Padding(5)
            self.invalid_name_label.ForeColor = Color.Red
            self.invalid_name_label.AutoSize = True

        # set invalid name label text
        self.invalid_name_label.Text = "Experiment name is taken."

    def remove_invalid_name_text(self):
        if self.invalid_name_label:
            # clear invalid name label text
            self.invalid_name_label.Text = ""

class ConfigNameDialog():
    '''
    Dialog window for inputting a configuration name.
    Used when creating or renaming a configuration.
    '''

    def ShowDialog(self, controller, title, text, default_input, config_index):
        # set controller
        self.controller = controller

        # set exp index
        self.config_index = config_index

        # initialize exp name variable
        self.config_name = None

        # initialize invalid name label
        self.invalid_name_label = None

        # create the form
        self.dialog_window = Form()
        self.dialog_window.AutoSize = True
        self.dialog_window.Width = 400
        self.dialog_window.StartPosition = FormStartPosition.CenterScreen
        self.dialog_window.Text = title
        self.dialog_window.MaximumSize = Size(400, 220)
        self.dialog_window.FormBorderStyle = FormBorderStyle.FixedSingle

        # create the main panel
        self.panel = FlowLayoutPanel()
        self.panel.Parent = self.dialog_window
        self.panel.BackColor = DIALOG_COLOR
        self.panel.Dock = DockStyle.Top
        self.panel.Padding = Padding(10, 10, 0, 10)
        self.panel.FlowDirection = FlowDirection.TopDown
        self.panel.WrapContents = False
        self.panel.AutoSize = True
        self.panel.Font = BODY_FONT

        # add the dialog text
        config_name_label = Label()
        config_name_label.Parent = self.panel
        config_name_label.Text = text
        config_name_label.Width = self.panel.Width
        config_name_label.AutoSize = True
        config_name_label.Margin = Padding(0, 5, 0, 0)

        # add the textbox
        self.config_name_box = TextBox()
        self.config_name_box.Text = default_input
        self.config_name_box.Parent = self.panel
        self.config_name_box.Width = self.dialog_window.Width - 30
        self.config_name_box.AutoSize = True
        self.config_name_box.BackColor = BUTTON_PANEL_COLOR
        self.config_name_box.Font = Font(BODY_FONT.FontFamily, 18)

        # add save button panel
        self.add_save_button_panel()

        # show the dialog
        self.dialog_window.ShowDialog()

        # return the config name
        return self.config_name

    def add_save_button_panel(self):
        # create save button panel
        self.save_button_panel = FlowLayoutPanel()
        self.save_button_panel.Parent = self.dialog_window
        self.save_button_panel.BackColor = BUTTON_PANEL_COLOR
        self.save_button_panel.Dock = DockStyle.Bottom
        self.save_button_panel.Padding = Padding(10, 0, 10, 10)
        self.save_button_panel.WrapContents = False
        # self.save_button_panel.Height = 40
        self.save_button_panel.Font = BODY_FONT
        self.save_button_panel.FlowDirection = FlowDirection.LeftToRight
        self.save_button_panel.AutoSize = True

        # add save button
        self.save_button = Button()
        self.save_button.Parent = self.save_button_panel
        self.save_button.Text = "Save"
        self.save_button.Click += self.on_save_button_click
        self.save_button.BackColor = BUTTON_COLOR
        self.save_button.AutoSize = True

        # save button is activated when user presses Enter
        self.dialog_window.AcceptButton = self.save_button

    def on_save_button_click(self, sender, event):
        # get what's in the text box
        config_name = self.config_name_box.Text

        if self.config_index == None:
            # we are creating a new config; check if none of the existing configs have the same name
            success = not (config_name in self.controller.configs['configs_list'])
        else:
            # we are renaming an config; check if none of the other configs have the same name
            other_configs = [exp for exp in self.controller.configs['configs_list'] if not exp == "config_name"]
            success = not (config_name in other_configs)

        if success:
            # the exp name is valid; set exp name & close the window
            self.config_name = config_name
            self.dialog_window.Close()
        else:
            # the exp name is invalid; add invalid name text
            self.add_invalid_name_text()

    def add_invalid_name_text(self):
        if not self.invalid_name_label:
            # add invalid name label
            self.invalid_name_label = Label()
            self.invalid_name_label.Parent = self.save_button_panel
            self.invalid_name_label.Font = ERROR_FONT
            self.invalid_name_label.Padding = Padding(5)
            self.invalid_name_label.ForeColor = Color.Red
            self.invalid_name_label.AutoSize = True

        # set invalid name label text
        self.invalid_name_label.Text = "Config name is taken."

    def remove_invalid_name_text(self):
        if self.invalid_name_label:
            # clear invalid name label text
            self.invalid_name_label.Text = ""
