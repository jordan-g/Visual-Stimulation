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

class ConfirmationDialog():
    '''
    Dialog window for confirming changed stim settings.
    Used when clicking 'Save' on a stim dialog to confirm that
    the user wants to stop the currently-running stimulation.
    '''

    def ShowDialog(self, controller, title, text):
        # set controller
        self.controller = controller

        # create confirmation boolean -- True means the user wants to save
        # the stimulus settings and stop the currently running stimulation.
        self.confirmation = False

        # create the form
        self.dialog_window = Form()
        self.dialog_window.AutoSize = True
        self.dialog_window.Width = 400
        self.dialog_window.MaximumSize = Size(400, 225)
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
        dialog_label = Label()
        dialog_label.Parent = self.panel
        dialog_label.Text = text
        dialog_label.Width = self.panel.Width
        dialog_label.AutoSize = True
        dialog_label.Margin = Padding(0, 5, 0, 0)

        # add button panel
        self.add_button_panel()

        # show the dialog
        self.dialog_window.ShowDialog()

        # return the exp name
        return self.confirmation

    def add_button_panel(self):
        # create button panel
        self.button_panel = FlowLayoutPanel()
        self.button_panel.Parent = self.dialog_window
        self.button_panel.BackColor = BUTTON_PANEL_COLOR
        self.button_panel.Dock = DockStyle.Bottom
        self.button_panel.Padding = Padding(10, 0, 10, 10)
        self.button_panel.WrapContents = False
        self.button_panel.AutoSize = True
        self.button_panel.Font = BODY_FONT
        self.button_panel.FlowDirection = FlowDirection.LeftToRight

        # add yes button
        self.yes_button = Button()
        self.yes_button.Parent = self.button_panel
        self.yes_button.Text = "Yes, Stop the Stimulation"
        self.yes_button.Click += self.on_yes_button_click
        self.yes_button.BackColor = BUTTON_COLOR
        self.yes_button.AutoSize = True

        # add cancel button
        self.cancel_button = Button()
        self.cancel_button.Parent = self.button_panel
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Click += self.on_cancel_button_click
        self.cancel_button.BackColor = BUTTON_COLOR
        self.cancel_button.Font = ERROR_FONT
        self.cancel_button.AutoSize = True

        # cancel button is activated when user presses Enter
        self.dialog_window.AcceptButton = self.cancel_button

    def on_yes_button_click(self, sender, event):
        self.confirmation = True

        # close the window
        self.dialog_window.Close()

    def on_cancel_button_click(self, sender, event):
        self.confirmation = False
        
        # close the window
        self.dialog_window.Close()