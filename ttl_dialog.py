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

class TTLDialog():
    '''
    Dialog window for setting TTL pulse parameters.
    '''

    def ShowDialog(self, controller):
        # set controller
        self.controller = controller

        # initialize success bool
        self.success = False

        # initialize invalid params label
        self.invalid_params_label = None

        # get current TTL params
        self.TTL_params = controller.config_params['TTL_params']

        # create the form
        self.dialog_window = Form()
        self.dialog_window.FormBorderStyle = FormBorderStyle.FixedSingle
        self.dialog_window.Text = "TTL Parameters"
        self.dialog_window.StartPosition = FormStartPosition.CenterScreen
        self.dialog_window.Width = 200

        # add & populate TTL param panel
        self.add_TTL_param_panel()
        self.populate_TTL_param_panel()

        # add save button panel
        self.add_save_button_panel()

        # auto-size the window
        self.dialog_window.AutoSize = True

        # show the dialog
        self.dialog_window.ShowDialog()
        
        # return success boolean
        return self.success

    def add_TTL_param_panel(self):
        # create TTL param panel
        self.TTL_param_panel = FlowLayoutPanel()
        self.TTL_param_panel.Parent = self.dialog_window
        self.TTL_param_panel.BackColor = PARAM_PANEL_COLOR
        self.TTL_param_panel.Dock = DockStyle.Bottom
        self.TTL_param_panel.Padding = Padding(10)
        self.TTL_param_panel.FlowDirection = FlowDirection.TopDown
        self.TTL_param_panel.WrapContents = False
        self.TTL_param_panel.AutoScroll = True
        self.TTL_param_panel.Font = BODY_FONT
        self.TTL_param_panel.AutoSize = True

    def populate_TTL_param_panel(self):
        # initialize TTL param text controls dict
        self.TTL_param_textboxes = {}

        # add heading label
        add_heading_label("TTL Parameters", self.TTL_param_panel)

        # add param labels & textboxes
        self.add_TTL_param_to_window('delay', 'Delay (ms)')
        self.add_TTL_param_to_window('frequency', 'Frequency (Hz)')
        self.add_TTL_param_to_window('pulse_width', 'Pulse width (ms)')
        self.add_TTL_param_to_window('duration', 'Duration (s)')

    def add_TTL_param_to_window(self, name, label_text):
        # add param label
        add_param_label(label_text + ':', self.TTL_param_panel)

        # add param textbox
        self.TTL_param_textboxes[name] = TextBox()
        self.TTL_param_textboxes[name].Parent = self.TTL_param_panel
        self.TTL_param_textboxes[name].Text = str(self.TTL_params[name])
        self.TTL_param_textboxes[name].Width = 150
        self.TTL_param_textboxes[name].BackColor = TEXTBOX_COLOR
        self.TTL_param_textboxes[name].AutoSize = True
        self.TTL_param_textboxes[name].Font = Font(BODY_FONT.FontFamily, 18)

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
        # save TTL params
        self.success = self.save_TTL_params(sender, event)

        if self.success:
            # saving was successful; close the window
            self.dialog_window.Close()

    def save_TTL_params(self, sender, event):
        # get contents of param textboxes
        self.TTL_param_textbox_values = {key: value.Text for (key, value) in self.TTL_param_textboxes.items()}
        
        if self.are_valid_params(self.TTL_param_textbox_values):
            # the params are valid

            # remove any invalid params text
            self.remove_invalid_params_text()
            
            # create new parameters dicts
            new_TTL_params = {key: float(value) for (key, value) in self.TTL_param_textbox_values.items()}

            # update controller's TTL params
            self.controller.config_params['TTL_params'] = new_TTL_params

            # save TTL params
            self.controller.save_config_params()

            return True
        else:
            # the params are invalid; add invalid params text
            self.add_invalid_params_text()

            return False

    def are_valid_params(self, TTL_params):
        # check that all of the params are valid
        stim_params_are_valid = (is_nonnegative_number(TTL_params['delay'])
                                 and is_positive_number(TTL_params['frequency'])
                                 and is_positive_number(TTL_params['pulse_width'])
                                 and is_positive_number(TTL_params['duration']))

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
