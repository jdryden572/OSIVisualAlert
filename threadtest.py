import threading
import time
import huecontroller
import TSPhillyVisualAlert
import logging
from tkinter import *
from tkinter import ttk


controller = huecontroller.HueController(username='ositechsupport')
monitor = TSPhillyVisualAlert.PhoneStatusMonitor(controller)

class MonitorThread(threading.Thread):
	def __init__(self, threadID, name, monitor):
		threading.Thread.__init__(self)
		self.ThreadID = threadID
		self.name = name
		self.monitor = monitor
		self._stop = threading.Event()
	
	def stop(self):
		self._stop.set()
		
	def stopped(self):
		return self._stop.isSet()
	
	def run(self):
		print('Starting', self.name)
		while True:
			if self.stopped():
				print('Exiting...')
				break
			tic = time.time()
			self.monitor.execute()
			toc = time.time()
			if (toc - tic) < 1:
				time.sleep(1 - (toc - tic))
		print('Successfully exited.')
		
monitorThread = MonitorThread(1, 'PhoneStatusThread', monitor)
monitorThread.daemon = True
monitorThread.start()


class GUI(Tk):
	def __init__(self, monitor, thread):
		Tk.__init__(self)
		self.monitor = monitor
		self.thread = thread
		self.status = StringVar()
		label = ttk.Label(self, textvariable=self.status)
		label.grid(row=0, column=0, columnspan=2)
		self.status.set(self.monitor.status)
		stop = ttk.Button(self, text='Stop', command=self.thread.stop)
		stop.grid(row=1, column=0, padx=5)
		resume = ttk.Button(self, text='Resume', command=self.resume)
		resume.grid(row=1, column=1, padx=5)
	
	def stop(self):
		self.status.set('Phone monitor stopped.')
		self.thread.stop()
		self.after_cancel(self.update_status)
		
	def resume(self):
		self.thread = MonitorThread(1, 'PhoneStatusThread', self.monitor)
		self.thread.daemon = True
		self.thread.start()
		self.after(200, self.update_status)
		
	
	def update_status(self):
		self.status.set(self.monitor.status)
		self.after(200, self.update_status)

window = GUI(monitor, monitorThread)
window.after(200, window.update_status)
window.geometry('-100-100')
window.mainloop()