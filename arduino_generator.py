import os
import shutil

def generate_arduino_sketch(TTL_params, directory="arduino_pulse"):
	if not os.path.exists(directory):
		os.makedirs(directory)

	filename = "%s/arduino_pulse.ino" % directory
	new_filename = "%s/arduino_pulse_new.ino" % directory

	with open(filename) as script_file, open(new_filename, "w+") as output_file:
		for num, line in enumerate(script_file, 1):
			if "pulseDelay =" in line:
				output_file.write("int pulseDelay = %d;\n" % TTL_params['delay'])
			elif "pulseFrequency =" in line:
				output_file.write("int pulseFrequency = %d;\n" % TTL_params['frequency'])
			elif "pulseWidth =" in line:
				output_file.write("int pulseWidth = %d;\n" % TTL_params['pulse_width'])
			elif "pulseDuration =" in line:
				output_file.write("int pulseDuration = %d;\n" % TTL_params['duration'])
			else:
				output_file.write(line)
	os.remove(filename)
	shutil.move(new_filename, filename)