

phoneQueueConfig = {
'pageURL': 'http://osi-cc100:9080/stats',
'callPattern': r'(\d*) CALLS WAITING FOR (\d*):(\d*)',
'lightStates': 
	{
	'red': 			{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.8, 0.3]},
	'redYellow': 	{'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.6, 0.4]},
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