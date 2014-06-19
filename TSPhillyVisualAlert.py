import huecontroller
import re
import sys
import logging
import time
import atexit

args = set(sys.argv)
if '-d' in args or '--debug' in args:
	logging.basicConfig(level=logging.DEBUG)
elif '-i' in args or '--info' in args:
	logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TSPhillyVisualAlert')

phoneQueueConfig = {
'lightStates': 
	{
	'red': 			{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.8, 0.3]},
	'orange': 		{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.6, 0.4]},
	'yellow':		{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.55, 0.46]},
	'green':		{'on': True, 'bri': 100, 'sat': 255, 'transitiontime': 4, 'xy': [0.5, 0.8]},
	'white':		{'on': True, 'bri':  50, 'sat': 255, 'transitiontime': 2, 'ct': 200},
	'allOn':		{'on': True, 'bri':  50, 'sat': 255, 'transitiontime': 2, 'ct': 250},
	'noConnect':	{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'effect': 'colorloop'},
	'allOff':		{'on': False}
	}
}

controllerConfig = {
'delayTime': 1,
'maxDisconnectTime': 15,
'ipPattern': r'(\d+\.\d+\.\d+\.\d+)',
'manualBridgeIP': None,
'userName': 'ositechsupport'
}

class PhoneStatusMonitor(huecontroller.BaseURLMonitor):
	"""
	Monitors the Tech Support phone queues and sends light state commands
	to the HueController.
	
	"""
	
	def __init__(self, controller):
		self.URL = 'http://osi-cc100:9080/stats'
		callPattern = r'(\d*) CALLS WAITING FOR (\d*):(\d*)'
		self.callPatternCompiled = re.compile(callPattern)
		self.states = phoneQueueConfig['lightStates']
		self.controller = controller
		self.standby = False
		self.state = None
		self.failCount = 0
		self.checkInterval = controllerConfig['delayTime']
		self.maxDisconnectTime = controllerConfig['maxDisconnectTime']
		
	def get_phone_data(self):
		"""Gets the state of the North America English tech support phone
		queue.
		
		Returns calls, timeSeconds, connectionFailed
		"""
		
		logger.debug('Accessing source URL...')		
		rawData = str(self.open_url(self.URL))
		try:
			calls, minutes, seconds = self.callPatternCompiled.search(rawData).groups()
		except:
			logger.warning('CANNOT CONNECT TO PHONE QUEUE STATUS PAGE')
			logger.warning('URL: {} Check network connection and destination URL.'.format(self.URL))
			return None, None, True
		logger.debug('Success.')
		logger.info(' {0:s} calls waiting for {1:s}:{2:s}'.format(calls, minutes, seconds))
		timeSeconds = int(minutes)*60 + int(seconds)
		return int(calls), timeSeconds, False
	
	def calculate_points(self, calls, waitTime):
		"""Determine call system priority points based on # of calls waiting
		and wait time of longest waiting call.
		"""
		callPoints = calls
		timePoints = waitTime // 60
		return callPoints + timePoints
	
	def determine_state(self, points, connectionFailure):
		"""Choose the Hue light state based on the point count and whether the 
		connection has been lost.
		"""
		
		if connectionFailure:
			return self.states['noConnect']
		elif points == 0:
			return self.states['white']
		elif points >= 0 and points < 4:
			return self.states['green']
		elif points >= 4 and points < 7:
			return self.states['yellow']
		elif points >= 7 and points < 9:
			return self.states['orange']
		elif points >= 9:
			return self.states['red']
		
	def is_operating_hours(self):
		"""Determines whether the the time is currently during office hours.

		Returns boolean True or False.
		"""
		isWeekday 	= (0  <= time.localtime()[6] <  5)	# checks if today is a weekday
		is7to7		= (7  <= time.localtime()[3] < 19)	# checks if currently between 7am and 7pm
		is11to8		= (11 <= time.localtime()[3] < 21)	# checks if currently between 11am and 8pm
		return (isWeekday and is7to7) or (not isWeekday and is11to8)
		
	def execute(self):
		if not self.is_operating_hours():
			logger.info('Not during office hours. Lights off.')
			self.state = self.states['allOff']
			self.controller.set_state(self.state)
			self.standby = True
			time.sleep(30)
			return
		if self.standby:
			self.state = self.states['allOn']
			self.controller.set_state(self.state)
			self.standby = False
			return
		calls, time, connectFailed = self.get_phone_data()
		if connectFailed:
			self.failCount += 1
		connectionFailure = self.failCount * self.checkInterval >= self.maxDisconnectTime
		points = self.calculate_points(calls, time)
		newState = self.determine_state(points, connectionFailure)
		logger.debug('New state: {}'.format(str(newState)))
		if newState != self.state:
			self.state = newState
			logger.info('Setting state: {}'.format(str(self.state)))
			self.controller.set_state(self.state)
	
	def reset_lights(self):
		try:
			self.state = self.states['allOff']
			self.controller.set_state(self.state)
		except:
			pass
			
if __name__ == '__main__':
	import huecontroller
	controller = huecontroller.HueController(username=controllerConfig['userName'])
	monitor = PhoneStatusMonitor(controller)
	atexit.register(monitor.reset_lights)
	monitor.run_forever()
	
	
		
		