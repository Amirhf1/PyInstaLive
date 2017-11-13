import argparse
import configparser
import logging
import os.path
import sys
import subprocess

from .auth import login
from .logger import log, seperator, supports_color
from .downloader import main
from .settings import settings

script_version = "2.2.5"
python_version = sys.version.split(' ')[0]
bool_values = {'True', 'False'}

def check_ffmpeg():
	try:
		FNULL = open(os.devnull, 'w')
		subprocess.call(["ffmpeg"], stdout=FNULL, stderr=subprocess.STDOUT)
		return True
	except OSError as e:
		return False


def check_config_validity(config):
	try:
		settings.username = config.get('pyinstalive', 'username')
		settings.password = config.get('pyinstalive', 'password')



		try:
			settings.show_cookie_expiry = config.get('pyinstalive', 'show_cookie_expiry').title()
			if not settings.show_cookie_expiry in bool_values:
				log("[W] Invalid setting detected for 'show_cookie_expiry', falling back to default value (True)", "YELLOW")
				settings.show_cookie_expiry = 'true'
		except:
			log("[W] Invalid setting detected for 'show_cookie_expiry', falling back to default value (True)", "YELLOW")
			settings.show_cookie_expiry = 'true'



		try:
			settings.clear_temp_files = config.get('pyinstalive', 'clear_temp_files').title()
			if not settings.show_cookie_expiry in bool_values:
				log("[W] Invalid setting detected for 'clear_temp_files', falling back to default value (True)", "YELLOW")
				settings.show_cookie_expiry = 'true'
		except:
			log("[W] Invalid setting detected for 'clear_temp_files', falling back to default value (True)", "YELLOW")
			settings.show_cookie_expiry = 'true'



		try:
			settings.save_path = config.get('pyinstalive', 'save_path')

			if (os.path.exists(settings.save_path)):
				pass
			else:
				log("[W] Invalid setting detected for 'save_path', falling back to location: " + os.getcwd(), "YELLOW")
				settings.save_path = os.getcwd()

			if not settings.save_path.endswith('/'):
				settings.save_path = settings.save_path + '/'
		except:
			log("[W] Invalid setting detected for 'save_path', falling back to location: " + os.getcwd(), "YELLOW")
			settings.save_path = os.getcwd()

		if not (len(settings.username) > 0):
			log("[E] Invalid setting detected for 'username'.", "RED")
			return False

		if not (len(settings.password) > 0):
			log("[E] Invalid setting detected for 'password'.", "RED")
			return False

		return True
	except KeyError as e:
		return False


def run():

	log('PYINSTALIVE (SCRIPT V{} - PYTHON V{})'.format(script_version, python_version), "GREEN")
	seperator("GREEN")

	logging.disable(logging.CRITICAL)
	config = configparser.ConfigParser()

	if os.path.exists('pyinstalive.ini'):
		try:
			config.read('pyinstalive.ini')
		except Exception:
			log("[E] Could not read configuration file. Try passing the required arguments manually.", "RED")
			seperator("GREEN")
	else:
		log("[W] Could not find configuration file, creating a default one ...", "YELLOW")
		try:
			config_template = "[pyinstalive]\nusername = johndoe\npassword = grapefruits\nsave_path = /\nshow_cookie_expiry = true"
			config_file = open("pyinstalive.ini", "w")
			config_file.write(config_template)
			config_file.close()
			log("[W] Edit the created 'pyinstalive.ini' file and run this script again.", "YELLOW")
			seperator("GREEN")
			sys.exit(0)
		except Exception as e:
			log("[E] Could not create default config file: " + str(e), "RED")
			log("[W] You must manually create and edit it with the following template: ", "YELLOW")
			log("", "GREEN")
			log(config_template, "YELLOW")
			log("", "GREEN")
			log("[W] Save it as 'pyinstalive.ini' and run this script again.", "YELLOW")
			log("", "GREEN")
			sys.exit(1)


	parser = argparse.ArgumentParser(description='You are running PyInstaLive ' + script_version + " with Python " + python_version)
	parser.add_argument('-u', '--username', dest='username', type=str, required=False, help="Instagram username to login with.")
	parser.add_argument('-p', '--password', dest='password', type=str, required=False, help="Instagram password to login with.")
	parser.add_argument('-r', '--record', dest='record', type=str, required=False, help="The username of the Instagram whose livestream or replay you want to save.")
	parser.add_argument('-i', '--info', dest='info', action='store_true', help="View information about PyInstaLive.")

	args = parser.parse_args()


	if check_config_validity(config):

		def show_info():
			log("[I] To see all the available flags, use the -h flag.", "BLUE")
			log("", "GREEN")
			log("[I] PyInstaLive version:    " + script_version, "GREEN")
			log("[I] Python version:         " + python_version, "GREEN")
			if check_ffmpeg() == False:
				log("[E] FFmpeg available:       False", "RED")
			else:
				log("[I] FFmpeg available:       True", "GREEN")
			if not os.path.isfile('credentials.json'):
				log("[I] Cookie file:            Not available", "GREEN")
			else:
				log("[I] Cookie file:            Available", "GREEN")
			log("[I] CLI supports color:     " + str(supports_color()), "GREEN")
			log("[I] Config file:", "GREEN")
			log("", "GREEN")
			with open('pyinstalive.ini') as f:
				for line in f:
					log("    " + line.rstrip(), "YELLOW")
			log("", "GREEN")
			log("[I] End of PyInstaLive information screen.", "GREEN")
			seperator("GREEN")


		if (args.username == None and args.password == None and args.record == None and args.info == False) or (args.info != False):
			show_info()
			sys.exit(0)

		if check_ffmpeg() == False:
			log("[E] Could not find ffmpeg, the script will now exit. ", "RED")
			seperator("GREEN")
			sys.exit(1)

		if (args.username is not None) and (args.password is not None):
			api = login(args.username, args.password, settings.show_cookie_expiry)
		else:
			api = login(settings.username, settings.password, settings.show_cookie_expiry)

		main(api, args.record, settings)
	else:
		log("[E] The configuration file is not valid. Please check your configuration settings and try again.", "RED")
		seperator("GREEN")
		sys.exit(0)
