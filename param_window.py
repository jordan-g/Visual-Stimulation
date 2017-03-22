import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System import Array
from System.Windows.Forms import Application, Form, Panel, TableLayoutPanel, FlowLayoutPanel
from System.Windows.Forms import Button, Label, Control, ComboBox, TextBox, TrackBar
from System.Windows.Forms import AnchorStyles, DockStyle, FlowDirection, BorderStyle, ComboBoxStyle, Padding, FormBorderStyle, FormStartPosition, DialogResult
from System.Drawing import Color, Size, Font, FontStyle, Icon, SystemFonts, FontFamily, ContentAlignment

# set fonts
header_font = Font("Segoe UI", 9, FontStyle.Bold)
body_font   = Font("Segoe UI", 9, FontStyle.Regular)
error_font  = Font("Segoe UI", 9, FontStyle.Bold)

# set colors
choice_panel_color = Color.WhiteSmoke
button_panel_color = Color.WhiteSmoke
param_panel_color  = Color.White
button_color       = Color.White
dialog_color       = Color.White
textbox_color      = Color.WhiteSmoke

# set stim color accents
looming_dot_color = Color.PaleGreen
moving_dot_color  = Color.LightCoral
grating_color     = Color.LightBlue
delay_color       = Color.Gainsboro

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
		self.panel.BackColor = dialog_color
		self.panel.Dock = DockStyle.Top
		self.panel.Padding = Padding(10, 10, 0, 10)
		self.panel.FlowDirection = FlowDirection.TopDown
		self.panel.WrapContents = False
		self.panel.AutoSize = True
		self.panel.Font = body_font

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
		self.exp_name_box.BackColor = button_panel_color
		self.exp_name_box.Font = Font(body_font.FontFamily, 18)

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
		self.save_button_panel.BackColor = button_panel_color
		self.save_button_panel.Dock = DockStyle.Bottom
		self.save_button_panel.Padding = Padding(10, 0, 10, 10)
		self.save_button_panel.WrapContents = False
		self.save_button_panel.AutoSize = True
		self.save_button_panel.Font = body_font
		self.save_button_panel.FlowDirection = FlowDirection.LeftToRight

		# add save button
		self.save_button = Button()
		self.save_button.Parent = self.save_button_panel
		self.save_button.Text = "Save"
		self.save_button.Click += self.on_save_button_click
		self.save_button.BackColor = button_color
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
			self.invalid_name_label.Font = error_font
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
		self.panel.BackColor = dialog_color
		self.panel.Dock = DockStyle.Top
		self.panel.Padding = Padding(10, 10, 0, 10)
		self.panel.FlowDirection = FlowDirection.TopDown
		self.panel.WrapContents = False
		self.panel.AutoSize = True
		self.panel.Font = body_font

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
		self.config_name_box.BackColor = button_panel_color
		self.config_name_box.Font = Font(body_font.FontFamily, 18)

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
		self.save_button_panel.BackColor = button_panel_color
		self.save_button_panel.Dock = DockStyle.Bottom
		self.save_button_panel.Padding = Padding(10, 0, 10, 10)
		self.save_button_panel.WrapContents = False
		# self.save_button_panel.Height = 40
		self.save_button_panel.Font = body_font
		self.save_button_panel.FlowDirection = FlowDirection.LeftToRight
		self.save_button_panel.AutoSize = True

		# add save button
		self.save_button = Button()
		self.save_button.Parent = self.save_button_panel
		self.save_button.Text = "Save"
		self.save_button.Click += self.on_save_button_click
		self.save_button.BackColor = button_color
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
			self.invalid_name_label.Font = error_font
			self.invalid_name_label.Padding = Padding(5)
			self.invalid_name_label.ForeColor = Color.Red
			self.invalid_name_label.AutoSize = True

		# set invalid name label text
		self.invalid_name_label.Text = "Config name is taken."

	def remove_invalid_name_text(self):
		if self.invalid_name_label:
			# clear invalid name label text
			self.invalid_name_label.Text = ""

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
			self.stim_type = "Looming Dot"
			self.stim_duration = 10
			self.stim_parameters = {'looming_dot_init_x_pos': 0.0,
									'looming_dot_init_y_pos': 0.0,
									'l_v': 20,
									'looming_dot_brightness': 1.0,
									'background_brightness': 1.0}	#changed from cont...

			# add the stim to the config params
			self.controller.add_stim(self.stim_name, self.stim_type, self.stim_duration, self.stim_parameters)

		# create the form
		self.dialog_window = Form()
		self.dialog_window.FormBorderStyle = FormBorderStyle.FixedSingle
		self.dialog_window.Text = "{} Parameters".format(self.stim_name)
		self.dialog_window.StartPosition = FormStartPosition.CenterScreen
		self.dialog_window.Width = 400

		# add & populate stim choice panel
		self.add_stim_choice_panel()
		self.populate_stim_choice_panel()

		# add & populate stim param panel
		self.add_stim_param_panel()
		self.populate_stim_param_panel()

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
		self.stim_choice_panel.BackColor = choice_panel_color
		self.stim_choice_panel.Dock = DockStyle.Bottom
		self.stim_choice_panel.Padding = Padding(10)
		self.stim_choice_panel.FlowDirection = FlowDirection.TopDown
		self.stim_choice_panel.WrapContents = False
		self.stim_choice_panel.AutoSize = True
		self.stim_choice_panel.Font = body_font

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
		self.stim_chooser.Items.AddRange(("Looming Dot", "Moving Dot", "Combined Dots", "Grating", "Delay", "Black Flash", "White Flash"))
		self.stim_chooser.SelectionChangeCommitted += self.on_stim_choice
		self.stim_chooser.Text = self.stim_type
		self.stim_chooser.Width = self.dialog_window.Width - 40
		self.stim_chooser.AutoSize = True
		self.stim_chooser.Font = Font(body_font.FontFamily, 18)

	def add_stim_param_panel(self):
		# create stim param panel
		self.stim_param_panel = FlowLayoutPanel()
		self.stim_param_panel.Parent = self.dialog_window
		self.stim_param_panel.BackColor = param_panel_color
		self.stim_param_panel.Dock = DockStyle.Bottom
		self.stim_param_panel.Padding = Padding(10)
		self.stim_param_panel.FlowDirection = FlowDirection.TopDown
		self.stim_param_panel.WrapContents = False
		self.stim_param_panel.AutoScroll = True
		self.stim_param_panel.Font = body_font
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
		self.name_textbox.BackColor = button_panel_color
		self.name_textbox.Font = Font(body_font.FontFamily, 18)

		# add duration label & textbox
		add_param_label('Duration (s):', self.stim_param_panel)
		self.duration_textbox = TextBox()
		self.duration_textbox.Parent = self.stim_param_panel
		self.duration_textbox.Text = str(self.stim_duration)
		self.duration_textbox.AutoSize = True
		self.duration_textbox.BackColor = button_panel_color
		self.duration_textbox.Font = Font(body_font.FontFamily, 18)

		# add parameters heading label
		if self.stim_type not in ("Delay", "Black Flash", "White Flash"):
			add_heading_label("{} Parameters".format(self.stim_type), self.stim_param_panel)

		# add param labels & textboxes
		if self.stim_type == "Looming Dot":
			self.add_stim_param_to_window('looming_dot_init_x_pos', 'Initial x position (deg)')
			self.add_stim_param_to_window('looming_dot_init_y_pos', 'Initial y position (deg)')
			self.add_stim_param_to_window('l_v', 'l/v (ms)')
			self.add_stim_param_to_window('looming_dot_brightness', 'Dot brightness (0 - 1)') #Will need to change to brightness ie moving dot
			self.add_stim_param_to_window('background_brightness', 'Background brightness (0 - 1)')		#here is the background_brightness problem
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
		self.stim_param_textboxes[name].BackColor = textbox_color
		self.stim_param_textboxes[name].Font = Font(body_font.FontFamily, 18)

	def on_stim_choice(self, sender, event):
		# get selected stim type
		new_stim_type = self.stim_chooser.SelectedItem.ToString()

		if new_stim_type != self.stim_type:
			# update stim type
			self.stim_type = new_stim_type

			# create stim parameters
			if self.stim_type == "Looming Dot":
				self.stim_parameters = {'looming_dot_init_x_pos': 0.0,
											   'looming_dot_init_y_pos': 0.0,
											   'l_v': 20,				## changed from 150 to 20
											   'looming_dot_brightness': 1.0,
											   'background_brightness': 0}
			elif self.stim_type == "Moving Dot":
				self.stim_parameters = {'radius': 10.0,
											   'moving_dot_init_x_pos': 0.0,
											   'moving_dot_init_y_pos': 0.0,
											   'v_x': 1.0,
											   'v_y': 0.0,
											   'moving_dot_brightness': 1.0,
											   'background_brightness': 0}
			elif self.stim_type == "Combined Dots":     ##Should give initial params?
				self.stim_parameters = {'radius': 10.0,     ##moving dot from here
											   'moving_dot_init_x_pos': 0.0,
											   'looming_dot_init_x_pos': 0.0,
											   'moving_dot_init_y_pos': 0.0,
											   'looming_dot_init_y_pos': 0.0,
											   'v_x': 0.01,
											   'v_y': 0.0,
											   'l_v': 20,
											   'moving_dot_brightness': 1.0,
											   'looming_dot_brightness': 1.0,
											   'background_brightness': 0} ## moving dot to here
			# elif self.stim_type == "Multiple Moving Dots":     ##Should give initial params?
			# 	self.stim_parameters = {'dot_params': [{'radius': 10.0,     ##moving dot from here
			# 								            'moving_dot_init_x_pos': 0.0,
			# 								            'moving_dot_init_y_pos': 0.0,
			# 								            'v_x': 0.01,
			# 								            'v_y': 0.0,
			# 								            'l_v': 150,
			# 								            'moving_dot_brightness': 1.0},
			# 								            {'radius': 10.0,     ##moving dot from here
			# 								            'moving_dot_init_x_pos': 0.0,
			# 								            'moving_dot_init_y_pos': 0.0,
			# 								            'v_x': 0.01,
			# 								            'v_y': 0.0,
			# 								            'l_v': 150,
			# 								            'moving_dot_brightness': 1.0}]} ## moving dot to here
			elif self.stim_type == "Grating":
				self.stim_parameters = {'frequency': 1,
											   'init_phase': 0.0,
											   'velocity': 0.02,
											   'contrast': 1.0}
			elif self.stim_type in ("Delay", "Black Flash", "White Flash"):
				self.stim_parameters = {}

			# refresh panel
			self.stim_choice_panel.Refresh()

			# populate stim param panel
			self.populate_stim_param_panel()

	def add_save_button_panel(self):
		# create save button panel
		self.save_button_panel = FlowLayoutPanel()
		self.save_button_panel.Parent = self.dialog_window
		self.save_button_panel.BackColor = button_panel_color
		self.save_button_panel.Dock = DockStyle.Bottom
		self.save_button_panel.Padding = Padding(10)
		self.save_button_panel.WrapContents = False
		self.save_button_panel.AutoSize = True
		self.save_button_panel.Font = body_font

		# add save button
		self.save_button = Button()
		self.save_button.Parent = self.save_button_panel
		self.save_button.Text = "Save"
		self.save_button.Click += self.on_save_button_click
		self.save_button.BackColor = button_color
		self.save_button.AutoSize = True

		# save button is activated when user presses Enter
		self.dialog_window.AcceptButton = self.save_button

		# add close button
		self.close_button = Button()
		self.close_button.Parent = self.save_button_panel
		self.close_button.Text = "Close"
		self.close_button.DialogResult = DialogResult.Cancel
		self.close_button.BackColor = button_color
		self.close_button.AutoSize = True

	def on_save_button_click(self, sender, event):
		# save stim params
		self.success = self.save_stim_params(sender, event)

		if self.success:
			# saving was successful; close the window
			self.dialog_window.Close()

	def save_stim_params(self, sender, event):
		# stop any running stim
		self.controller.running_stim = False

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
		elif stim_type in ("Delay", "Black Flash", "White Flash"):
			stim_params_are_valid = True

		return stim_params_are_valid

	def add_invalid_params_text(self):
		if not self.invalid_params_label:
			# add invalid params label
			self.invalid_params_label = Label()
			self.invalid_params_label.Parent = self.save_button_panel
			self.invalid_params_label.Font = error_font
			self.invalid_params_label.Padding = Padding(5)
			self.invalid_params_label.ForeColor = Color.Red
			self.invalid_params_label.AutoSize = True

		# set invalid param label text
		self.invalid_params_label.Text = "Invalid parameters."

	def remove_invalid_params_text(self):
		if self.invalid_params_label:
			# clear invalid param label text
			self.invalid_params_label.Text = ""

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
		self.TTL_param_panel.BackColor = param_panel_color
		self.TTL_param_panel.Dock = DockStyle.Bottom
		self.TTL_param_panel.Padding = Padding(10)
		self.TTL_param_panel.FlowDirection = FlowDirection.TopDown
		self.TTL_param_panel.WrapContents = False
		self.TTL_param_panel.AutoScroll = True
		self.TTL_param_panel.Font = body_font
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
		self.TTL_param_textboxes[name].BackColor = textbox_color
		self.TTL_param_textboxes[name].AutoSize = True
		self.TTL_param_textboxes[name].Font = Font(body_font.FontFamily, 18)

	def add_save_button_panel(self):
		# create save button panel
		self.save_button_panel = FlowLayoutPanel()
		self.save_button_panel.Parent = self.dialog_window
		self.save_button_panel.BackColor = button_panel_color
		self.save_button_panel.Dock = DockStyle.Bottom
		self.save_button_panel.Padding = Padding(10)
		self.save_button_panel.WrapContents = False
		self.save_button_panel.AutoSize = True
		self.save_button_panel.Font = body_font

		# add save button
		self.save_button = Button()
		self.save_button.Parent = self.save_button_panel
		self.save_button.Text = "Save"
		self.save_button.Click += self.on_save_button_click
		self.save_button.BackColor = button_color
		self.save_button.AutoSize = True

		# save button is activated when user presses Enter
		self.dialog_window.AcceptButton = self.save_button

		# add close button
		self.close_button = Button()
		self.close_button.Parent = self.save_button_panel
		self.close_button.Text = "Close"
		self.close_button.DialogResult = DialogResult.Cancel
		self.close_button.BackColor = button_color
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
			self.invalid_params_label.Font = error_font
			self.invalid_params_label.Padding = Padding(5)
			self.invalid_params_label.ForeColor = Color.Red
			self.invalid_params_label.AutoSize = True

		# set invalid param label text
		self.invalid_params_label.Text = "Invalid parameters."

	def remove_invalid_params_text(self):
		if self.invalid_params_label:
			# clear invalid param label text
			self.invalid_params_label.Text = ""

class ParamWindow(Form):
	'''
	Parameter window class.
	This is the main window that is opened.
	'''

	def __init__(self, controller):
		# set controller
		self.controller = controller

		# initialize invalid params label
		self.invalid_params_label = None

		# set window details
		self.Text = 'Parameters'
		self.StartPosition = FormStartPosition.Manual
		self.FormBorderStyle = FormBorderStyle.FixedSingle
		self.Top = 30
		self.Left = 30
		self.AutoSize = True

		# create dialogs
		self.experiment_name_dialog = ExperimentNameDialog()
		self.config_name_dialog = ConfigNameDialog()
		self.stim_dialog = StimDialog()
		self.TTL_dialog = TTLDialog()

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

	def add_exp_choice_panel(self):
		# add exp button panel
		self.exp_button_panel = FlowLayoutPanel()
		self.exp_button_panel.Parent = self
		self.exp_button_panel.BackColor = button_panel_color
		self.exp_button_panel.Padding = Padding(10, 0, 10, 10)
		self.exp_button_panel.Dock = DockStyle.Top
		self.exp_button_panel.FlowDirection = FlowDirection.LeftToRight
		self.exp_button_panel.WrapContents = False
		self.exp_button_panel.AutoSize = True
		self.exp_button_panel.Font = body_font

		# add new exp button
		new_exp_button = Button()
		new_exp_button.Parent = self.exp_button_panel
		new_exp_button.Text = "New"
		new_exp_button.AutoSize = True
		new_exp_button.Click += self.add_new_experiment
		new_exp_button.BackColor = button_color

		# add remove exp button
		self.remove_exp_button = Button()
		self.remove_exp_button.Parent = self.exp_button_panel
		self.remove_exp_button.Text = "Delete"
		self.remove_exp_button.AutoSize = True
		self.remove_exp_button.Click += self.remove_experiment
		self.remove_exp_button.BackColor = button_color

		# disable remove exp button if there is only one experiment
		if len(self.controller.experiments['experiments_list']) == 1:
			self.remove_exp_button.Enabled = False

		# add rename exp button
		rename_exp_button = Button()
		rename_exp_button.Parent = self.exp_button_panel
		rename_exp_button.Text = "Rename"
		rename_exp_button.AutoSize = True
		rename_exp_button.Click += self.rename_experiment
		rename_exp_button.BackColor = button_color

		# create exp choice panel
		self.exp_choice_panel = FlowLayoutPanel()
		self.exp_choice_panel.Parent = self
		self.exp_choice_panel.BackColor = choice_panel_color
		self.exp_choice_panel.Dock = DockStyle.Top
		self.exp_choice_panel.Padding = Padding(10, 10, 0, 10)
		self.exp_choice_panel.FlowDirection = FlowDirection.TopDown
		self.exp_choice_panel.WrapContents = False
		self.exp_choice_panel.AutoSize = True
		self.exp_choice_panel.Font = body_font

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
		self.exp_chooser.Font = Font(body_font.FontFamily, 18)

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
		# stop any running stim
		self.controller.running_stim = False

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
		# stop any running stim
		self.controller.running_stim = False

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
		self.exp_param_panel.BackColor = param_panel_color
		self.exp_param_panel.Dock = DockStyle.Top
		self.exp_param_panel.Padding = Padding(10)
		self.exp_param_panel.FlowDirection = FlowDirection.LeftToRight
		self.exp_param_panel.WrapContents = True
		# self.exp_param_panel.Height = 250
		self.exp_param_panel.AutoSize = True
		self.exp_param_panel.Font = body_font

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
		self.add_exp_param_to_window('distance', 'Screen distance (cm)')

		self.add_exp_param_slider_to_window('width', 'Viewport width', 1, 100)
		self.add_exp_param_slider_to_window('height', 'Viewport height', 1, 100)

		# add filler subpanel
		exp_param_subpanel = FlowLayoutPanel()
		exp_param_subpanel.Parent = self.exp_param_panel
		exp_param_subpanel.BackColor = param_panel_color
		exp_param_subpanel.Dock = DockStyle.Bottom
		exp_param_subpanel.Padding = Padding(0)
		exp_param_subpanel.FlowDirection = FlowDirection.TopDown
		exp_param_subpanel.WrapContents = False
		exp_param_subpanel.Width = int(self.Width/3) - 20
		# exp_param_subpanel.Height = 60
		exp_param_subpanel.AutoSize = True
		exp_param_subpanel.Font = body_font

		self.add_exp_param_slider_to_window('x_offset', 'Viewport x offset', 0, 100)
		self.add_exp_param_slider_to_window('y_offset', 'Viewport y offset', 0, 100)

	def add_exp_param_to_window(self, name, label_text):
		# create exp param panel
		exp_param_subpanel = FlowLayoutPanel()
		exp_param_subpanel.Parent = self.exp_param_panel
		exp_param_subpanel.BackColor = param_panel_color
		exp_param_subpanel.Dock = DockStyle.Bottom
		exp_param_subpanel.Padding = Padding(0)
		exp_param_subpanel.FlowDirection = FlowDirection.TopDown
		exp_param_subpanel.WrapContents = False
		exp_param_subpanel.Width = int(self.Width/3) - 20
		# exp_param_subpanel.Height = 60
		exp_param_subpanel.AutoSize = True
		exp_param_subpanel.Font = body_font

		# add param label
		add_param_label(label_text + ":", exp_param_subpanel)

		# add param textbox
		self.exp_param_textboxes[name] = TextBox()
		self.exp_param_textboxes[name].Parent = exp_param_subpanel
		self.exp_param_textboxes[name].Text = str(self.controller.experiment_params[name])
		self.exp_param_textboxes[name].Width = int(self.Width/3) - 20
		self.exp_param_textboxes[name].BackColor = button_panel_color
		self.exp_param_textboxes[name].Font = Font(body_font.FontFamily, 18)

	def add_exp_param_slider_to_window(self, name, label_text, min, max):
		# create exp param panel
		exp_param_subpanel = FlowLayoutPanel()
		exp_param_subpanel.Parent = self.exp_param_panel
		exp_param_subpanel.BackColor = param_panel_color
		exp_param_subpanel.Dock = DockStyle.Bottom
		exp_param_subpanel.Padding = Padding(0)
		exp_param_subpanel.FlowDirection = FlowDirection.TopDown
		exp_param_subpanel.WrapContents = False
		exp_param_subpanel.Width = int(self.Width/3) - 20
		# exp_param_subpanel.Height = 60
		exp_param_subpanel.AutoSize = True
		exp_param_subpanel.Font = body_font

		# add param label
		self.exp_param_slider_labels[name] = Label()
		self.exp_param_slider_labels[name].Parent = exp_param_subpanel
		self.exp_param_slider_labels[name].Text = label_text + ": " + str(self.controller.experiment_params[name])
		self.exp_param_slider_labels[name].AutoSize = True
		self.exp_param_slider_labels[name].Font = body_font
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
			self.controller.experiment_params[sender.Name] = sender.Value/100.0

			self.controller.stim_window.update_params()

	def add_config_choice_panel(self):
		# create config choice panel
		self.config_choice_panel = FlowLayoutPanel()
		self.config_choice_panel.Parent = self
		self.config_choice_panel.BackColor = choice_panel_color
		self.config_choice_panel.Dock = DockStyle.Top
		self.config_choice_panel.Padding = Padding(10, 10, 0, 10)
		self.config_choice_panel.FlowDirection = FlowDirection.TopDown
		self.config_choice_panel.WrapContents = False
		self.config_choice_panel.AutoSize = True
		self.config_choice_panel.Font = body_font

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
		self.config_chooser.Font = Font(body_font.FontFamily, 18)

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
		self.config_button_panel.BackColor = button_panel_color
		self.config_button_panel.Padding = Padding(10, 0, 10, 10)
		self.config_button_panel.Dock = DockStyle.Top
		self.config_button_panel.FlowDirection = FlowDirection.LeftToRight
		self.config_button_panel.WrapContents = False
		self.config_button_panel.AutoSize = True
		self.config_button_panel.Font = body_font

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
		new_config_button.BackColor = button_color
		new_config_button.AutoSize = True

		# add remove config button
		self.remove_config_button = Button()
		self.remove_config_button.Parent = self.config_button_panel
		self.remove_config_button.Text = "Delete"
		self.remove_config_button.Click += self.remove_config
		self.remove_config_button.BackColor = button_color
		self.remove_config_button.AutoSize = True
		if len(self.controller.configs['configs_list']) == 1:
			self.remove_config_button.Enabled = False

		# add rename config button
		rename_config_button = Button()
		rename_config_button.Parent = self.config_button_panel
		rename_config_button.Text = "Rename"
		rename_config_button.Click += self.rename_config
		rename_config_button.BackColor = button_color
		rename_config_button.AutoSize = True

	def add_new_config(self, sender, event):
		# stop any running stim
		self.controller.running_stim = False

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
		# stop any running stim
		self.controller.running_stim = False

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
		self.stim_list_panel.BackColor = param_panel_color
		self.stim_list_panel.Dock = DockStyle.Fill
		self.stim_list_panel.Padding = Padding(0)
		self.stim_list_panel.FlowDirection = FlowDirection.TopDown
		self.stim_list_panel.WrapContents = False
		self.stim_list_panel.AutoScroll = True
		self.stim_list_panel.Width = self.Width
		self.stim_list_panel.AutoSize = True
		self.stim_list_panel.Font = body_font

	def populate_stim_list_panel(self):
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

	def add_stim_to_stim_list_panel(self, i):
		# create stim subpanel
		subpanel = FlowLayoutPanel()
		subpanel.Parent = self.stim_list_panel
		subpanel.Dock = DockStyle.Fill
		subpanel.Padding = Padding(0)
		subpanel.Margin = Padding(1, 0, 1, 1)
		subpanel.FlowDirection = FlowDirection.LeftToRight
		subpanel.WrapContents = False
		subpanel.AutoSize = True
		subpanel.Font = body_font
		subpanel.Tag = i

		# get stim type
		stim_type = self.controller.config_params['types_list'][i]

		# add edit button
		edit_button = Button()
		edit_button.Parent = subpanel
		edit_button.Text = "Edit"
		edit_button.AutoSize = True
		edit_button.Click += self.edit_stim
		edit_button.BackColor = button_color

		# add edit button to list of edit buttons
		self.stim_list_edit_buttons.append(edit_button)

		# add delete button
		delete_button = Button()
		delete_button.Parent = subpanel
		delete_button.Text = "Delete"
		delete_button.AutoSize = True
		delete_button.Click += self.remove_stim
		delete_button.BackColor = button_color

		# add delete button to list of delete buttons
		self.stim_list_delete_buttons.append(delete_button)

		# add stim name label
		stim_name_label = Label()
		stim_name_label.Parent = subpanel
		stim_name_label.Text = self.controller.config_params['stim_list'][i]
		stim_name_label.Width = 120
		stim_name_label.AutoSize = True
		stim_name_label.Padding = Padding(0, 7, 0, 0)
		stim_name_label.AutoEllipsis = True

		# add stim name label to list of stim name labels
		self.stim_list_name_labels.append(stim_name_label)

		# add stim type label
		stim_type_label = Label()
		stim_type_label.Parent = subpanel
		stim_type_label.Text = stim_type
		stim_type_label.MinimumSize = Size(360, 0)
		stim_type_label.AutoSize = True
		stim_type_label.Padding = Padding(0, 7, 0, 0)

		# add stim type label to list of stim type labels
		self.stim_list_type_labels.append(stim_type_label)

		# add duration label
		duration_label = Label()
		duration_label.Parent = subpanel
		duration_label.Text = str(self.controller.config_params['durations_list'][i]) + "s"
		duration_label.AutoSize = True
		duration_label.Width = 100
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
		move_up_button.BackColor = button_color

		# add move down button
		move_down_button = Button()
		move_down_button.Parent = subpanel
		move_down_button.Text = u"\u02C5"
		move_down_button.MaximumSize = Size(40, 0)
		move_down_button.AutoSize = True
		move_down_button.Click += self.move_down_stim
		move_down_button.BackColor = button_color

		# add color accent
		if stim_type == "Looming Dot":
			color = looming_dot_color
		elif stim_type == "Moving Dot":
			color = moving_dot_color
		elif stim_type == "Grating":
			color = grating_color
		else:
			color = delay_color
		edit_button.BackColor = color

		# add subpanel to list of subpanels
		self.stim_list_subpanels.append(subpanel)

	def move_up_stim(self, sender, event):
		# stop any running stim
		self.controller.running_stim = False

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
		# stop any running stim
		self.controller.running_stim = False

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
		# stop any running stim
		self.controller.running_stim = False

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

	def edit_stim(self, sender, event):
		# stop any running stim
		self.controller.running_stim = False

		# get stim index
		stim_index = sender.Parent.Tag

		# show stim dialog
		success = self.stim_dialog.ShowDialog(self.controller, stim_index)

		# update stim subpanel controls
		self.stim_list_name_labels[stim_index].Text = str(self.controller.config_params['stim_list'][stim_index])
		self.stim_list_duration_labels[stim_index].Text = str(self.controller.config_params['durations_list'][stim_index]) + "s"

		# get stim type
		stim_type = self.controller.config_params['types_list'][stim_index]

		# update stim type label
		self.stim_list_type_labels[stim_index].Text = str(stim_type)

		# add color accent
		if stim_type == "Looming Dot":
			color = looming_dot_color
		elif stim_type == "Moving Dot":
			color = moving_dot_color
		elif stim_type == "Grating":
			color = grating_color
		else:
			color = delay_color
		self.stim_list_edit_buttons[stim_index].BackColor = color

	def add_save_button_panel(self):
		# create save button panel
		self.save_button_panel = FlowLayoutPanel()
		self.save_button_panel.Parent = self
		self.save_button_panel.BackColor = button_panel_color
		self.save_button_panel.Dock = DockStyle.Bottom
		self.save_button_panel.Padding = Padding(10)
		self.save_button_panel.WrapContents = False
		self.save_button_panel.AutoSize = True
		self.save_button_panel.Font = body_font

		# add new stim button
		self.add_stim_button = Button()
		self.add_stim_button.Parent = self.save_button_panel
		self.add_stim_button.Text = "Add Stim"
		self.add_stim_button.Click += self.add_stim
		self.add_stim_button.BackColor = button_color
		self.add_stim_button.AutoSize = True

		# add save button
		self.save_button = Button()
		self.save_button.Parent = self.save_button_panel
		self.save_button.Text = "Save"
		self.save_button.Click += self.save_experiment_params
		self.save_button.BackColor = button_color
		self.save_button.AutoSize = True

		self.AcceptButton = self.save_button

		# add start/stop button
		self.start_stop_button = Button()
		self.start_stop_button.Parent = self.save_button_panel
		self.start_stop_button.Text = "Start"
		self.start_stop_button.Click += self.start_stop_stim
		self.start_stop_button.BackColor = button_color
		self.start_stop_button.AutoSize = True

		# add edit TTL params button
		self.ttl_button = Button()
		self.ttl_button.Parent = self.save_button_panel
		self.ttl_button.Text = "TTL"
		self.ttl_button.Click += self.edit_TTL_params
		self.ttl_button.BackColor = button_color
		self.ttl_button.AutoSize = True

	def add_stim(self, sender, event):
		# stop any running stim
		self.controller.running_stim = False

		# show stim dialog
		success = self.stim_dialog.ShowDialog(self.controller, None)

		if success:
			# add stim subpanel
			self.add_stim_to_stim_list_panel(len(self.controller.config_params['stim_list'])-1)

	def save_experiment_params(self, sender, event):
		print("ParamWindow: Saving experiment params.")

		# stop any running stim
		self.controller.running_stim = False
		
		# get contents of param textboxes
		self.exp_param_values         = {key: value.Text for (key, value) in self.exp_param_textboxes.items()}
		self.exp_param_slider_values  = {key: value.Value/100.0 for (key, value) in self.exp_param_sliders.items()}

		self.exp_param_values.update(self.exp_param_slider_values)
		
		if self.are_valid_params(self.exp_param_values):
			# the params are valid

			# remove any invalid params text
			self.remove_invalid_params_text()
			
			# create new parameters dicts
			new_exp_params = {key: float(value) for (key, value) in self.exp_param_values.items()}

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
			# the params are invalid; add invalid params text
			self.add_invalid_params_text()

	def start_stop_stim(self, sender, event):
		if self.controller.running_stim:
			self.controller.running_stim = False
			self.start_stop_button.Text = "Start"
		else:
			self.controller.start_stim()
			self.start_stop_button.Text = "Stop"

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
			self.invalid_params_label.Font = error_font
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

	def Close(self):
		print("ParamWindow: Closing.")

		self.experiment_name_dialog = None
		self.config_name_dialog = None
		self.stim_dialog = None

		# save experiment params
		self.save_experiment_params(self, None)

		super(ParamWindow, self).Close()

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
	label.Font = header_font
	label.Margin = Padding(0, 5, 0, 5)

def add_param_label(text, panel):
	# add param label
	label = Label()
	label.Parent = panel
	label.Text = text
	label.AutoSize = True
	label.Font = body_font
	label.Margin = Padding(0, 5, 0, 0)
	label.Width = panel.Width
