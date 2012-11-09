import viz
import vizact
import SerialPort_win
import viztask
import time
import numpy as np

DEVICE   = "COM3"
TIMEOUT  = 0
SPEED    = 19200
TRIGGER_DOWN       = "5"
RIGHT_BUTTON_DOWN  = "4"  #4--scanner  #3
RIGHT_BUTTON_UP    = "4"
LEFT_BUTTON_DOWN   = "1" #--scanner
LEFT_BUTTON_UP     = "1" #2
TRIGGER_EVENT = viz.getEventID("PULSE_EVENT")
RIGHT_BUTTON_EVENT = viz.getEventID("RIGHT_B_EVENT")
LEFT_BUTTON_EVENT = viz.getEventID("LEFT_B_EVENT")

"""
Classes for interacting with the Lumina system in the UCSB
Brain Imaging Center in vizard.
"""
	

class FmriTrigger(object):	
	def __init__(self):
		self.port = SerialPort_win.SerialPort(
					DEVICE,TIMEOUT,SPEED)
		self.event_count = 0
		self.go = False
		self.right_button = False
		self.left_button = False
		self.rt=[]
		self.events=[]
		self.state = []
		self.triggertime=0

	def start(self):
		vizact.onupdate(0,self.check_pulse)
		
	def check_pulse(self):
		state = self.port.read()
		self.triggertime = viz.tick()
		#print state
		if state:
			self.go = True 
			#print "fmri trigger state", state
			if state == TRIGGER_DOWN:
				viz.sendEvent(TRIGGER_EVENT)
				self.event_count += 1
				self.rt.append(self.triggertime)
				#self.rt = np.append(self.rt,self.event_count)
				self.events.append(self.event_count)
				#print self.rt
				#print rt
				#print 'triggered at', self.triggertime, 'seconds'
				
			elif state == "4":
				#self.right_button = True
				#print 'sent right'
				viz.sendEvent(RIGHT_BUTTON_EVENT)
			elif state == "1":
				#self.left_button = True
				viz.sendEvent(LEFT_BUTTON_EVENT)
			#elif state == RIGHT_BUTTON_UP:
			#	self.right_button = False
			elif state == LEFT_BUTTON_DOWN:
				self.left_button = False
			
class FakeFmriTrigger(FmriTrigger):
	def __init__(self):
		# start a timer that sends fake triggers
		vizact.ontimer(2,self.sendit)
		# same
		self.event_count = 0
		self.right_button = False
		self.left_button = False
		self.go = False
		self.triggertime = 0
		self.events = []
		self.rt=[]
	def sendit(self):
		sendit = viz.sendEvent(TRIGGER_EVENT)
	def check_pulse(self):
		#if state:
		#print "fmri trigger state", state
		#if state == "5":
		#	self.event_count += 1
		#	viz.sendEvent(self.TRIGGER_EVENT,)
		if state == RIGHT_BUTTON_DOWN:
			self.right_button = True
			viz.sendEvent(RIGHT_BUTTON_EVENT)
		elif state == LEFT_BUTTON_DOWN:
			self.left_button = True
			viz.sendEvent(LEFT_BUTTON_EVENT)
		elif state == RIGHT_BUTTON_UP:
			self.right_button = False
		elif state == LEFT_BUTTON_DOWN:
			self.left_button = False
			
			
if __name__ == "__main__":
	viz.go()
	ft = FmriTrigger()
	vizact.ontimer(0,ft.check_pulse)
	