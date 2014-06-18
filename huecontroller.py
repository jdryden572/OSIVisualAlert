"""
visualhue

Brett Nelson and James Dryden
OSIsoft, LLC

An implementation of Philips Hue as a status indicator.

"Hue Personal Wireless Lighting" is a trademark owned by 
Philips Electronics N.V. See www.meethue.com for more information.
"""


import urllib.request
import atexit
import time
import re
import warnings
import logging
try:
	import requests
except:
	exit('The requests module must be installed. Try "pip install requests"')
try: 
	import phue
except:
	exit('The phue module must be installed. Visit https://github.com/studioimaginaire/phue')

logging.basicConfig(level=logging.DEBUG) # REMOVE THIS FOR PRODUCTION
logger = logging.getLogger('visualhue')
	

class BaseURLMonitor(object):
	
	""" Base Class for URL data monitors.  
	
	Defines the open_url(URL) method, which returns raw data from 
	the given URL. 
	
	"""
	
	checkInterval = 10
	
	def __init__(self):
		"""Constructor.  May be overridden."""		
		pass
	
	def open_url(self, URL):
		"""Returns raw data from given URL."""
		try:
			with urllib.request.urlopen(URL) as f:
				data = f.read()
			return data
		except Exception as e:
			logger.warning('Received Exception: {}'.format(e))
			return None
		
	def execute(self):
		"""Should be overridden by child class."""
		logger.warning('execute() method has not been overriden!')
		
	def run_forever(self):
		"""Run execute() method repeatedly with delay defined by the 
		checkInterval attribute"""
		try:
			logger.info('Running forever. Hit ^C to interrupt.')
			while True:
				tic = time.time()
				self.execute()
				toc = time.time()
				if (toc - tic) < self.checkInterval:	
					time.sleep(self.checkInterval - (toc - tic))
		except KeyboardInterrupt:
			logger.warning('Keyboard interrupt detected, stopping.')

class HueController(object):
	
	"""Main controller object. """
	
	def __init__(self, ip=None, username=None):
		""" Initialization function.
		
		userName : string, optional
		
		Will attempt to find Bridge IP automatically and connect.  Will 
		attempt to use given userName first if present.  If not, will 
		default to "newdeveloper".
		
		Once connected, instruct Bridge to search for new lights using 
		get_new_lights().
		"""
		
		self.IP = ip
		self.userName = username
		self.hue = None
		
		if self.IP:
			logger.info('Using IP: {}'.format(self.IP))
			self.hue = self.connect(self.IP)
			if self.hue is None:
				logger.warning('Given IP failed. Finding IP automatically...')
				self.IP = self.get_bridge_IP()
				logger.info('Found IP: {}'.format(self.IP))
				self.hue = self.connect(self.IP)
		self.IP = self.get_bridge_IP()
		logger.info('Found IP: {}'.format(self.IP))
		self.hue = self.connect(self.IP)
		
		self.get_new_lights()

	def connect(self, IP):
		"""Attempts to connect to Bridge"""
		if self.userName:
			hue = phue.Bridge(ip=IP, username=self.userName)
		else: 
			hue = phue.Bridge(ip=IP, username='newdeveloper')
		try:
			test = hue.get_api()
		except: 
			return None
		for line in test:
			for key in line:
				if 'error' in key:
					logger.warning('Found Bridge at {0}'.format(IP)) 
					logger.warning('Access denied to Bridge, make sure username is registered!')
					logger.warning(str(test))
					exit('Quitting.')
		return hue
	
	def get_bridge_IP(self):
		"""Attempts to automatically find a Hue Bridge on the network.
		
		Hue Bridges automatically upload their IP address daily to a Philips
		database.  Accessing http://www.meethue.com/api/nupnp returns a list 
		of Hue Bridges connected to the network you are connecting from.
		
		"""
		with urllib.request.urlopen('http://www.meethue.com/api/nupnp') as connection:
			data = str(connection.read())
		ipPatternCompiled = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
		match = ipPatternCompiled.search(data)
		if match is None:
			logger.warning('Could not find Bridge IP address automatically')
			exit('Quitting.')
		else: 
			return match.group(1)
					
	def get_new_lights(self):
		"""Instructs the Hue Bridge to search for new Hue lights.
	
		The 'find new lights' function appears to be unsupported by the phue 
		module.  This function will instruct the bridge to search for and add
		any new hue lights.  Searching continues for 1 minute and is only 
		capable of locating up to 15 new lights. To add additional lights, 
		the command must be run again.
		"""
		logger.info('Instructing Bridge to search for new lights.')
		connection = requests.post('http://' + self.IP + '/api/' + self.userName + '/lights')
		logger.info(connection.text)
		connection.close()
		
	def set_state(self, state):
		"""Accepts a state (type: dictionary) and applies it to all Hue lights."""
		logger.info('Setting lights to {}'.format(state))
		response = self.hue.set_group(0, state)
		logger.info(response)
	
	
	
	
		