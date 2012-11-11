import viz
import vizact
import SerialPort_win
import viztask


# ------ Configuration for the lumina box ------------
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
FIRST_TRIGGER_EVENT = viz.getEventID("FIRST_PULSE_EVENT")
# ----------------------------------------------------

# ----- Configuration for fake scanner triggers ------
LEFT_KEY = "a"
RIGHT_KEY = "'"
# ----------------------------------------------------

"""
Classes for interacting with the Lumina system in the UCSB
Brain Imaging Center in vizard. If you're testing this without
the scanner, use FakeFmriTrigger
"""

class FmriTrigger(object):	
	def __init__(self):
		self.port = SerialPort_win.SerialPort(DEVICE,TIMEOUT,SPEED)
		self.received_triggers = []
		self.events=[]
		self.event_count = 0

	def start(self):
		vizact.onupdate(0,self.check_pulse)
		
	def check_pulse(self):
		state = self.port.read()
		triggertime = viz.tick()
		if state:
			if state == TRIGGER_DOWN:
				viz.sendEvent(TRIGGER_EVENT)
				self.event_count += 1
				self.received_triggers.append(triggertime)
			elif state == RIGHT_BUTTON_DOWN:
				viz.sendEvent(RIGHT_BUTTON_EVENT)
				self.events.append((RIGHT_BUTTON_DOWN,triggertime))
			elif state == LEFT_BUTTON_DOWN:
				viz.sendEvent(LEFT_BUTTON_EVENT)
				self.events.append((LEFT_BUTTON_DOWN,triggertime))
			
class FakeFmriTrigger(FmriTrigger):
	def __init__(self):
		vizact.onkeydown(RIGHT_KEY,self.sendright)
		vizact.onkeydown(LEFT_KEY,self.sendleft)
		self.events = []
		self.received_triggers = []
		
	def sendit(self):
		# start a timer that sends fake triggers
		sendit = viz.sendEvent(TRIGGER_EVENT)
		self.received_triggers.append(viz.tick())
		
	def start(self):
		vizact.ontimer(2,self.sendit)
		
	def sendright(self):
		triggertime=viz.tick()
		viz.sendEvent(RIGHT_BUTTON_EVENT)
		self.events.append((RIGHT_BUTTON_DOWN,triggertime))
		
	def sendleft(self):
		triggertime=viz.tick()
		viz.sendEvent(LEFT_BUTTON_EVENT)
		self.events.append((LEFT_BUTTON_DOWN,triggertime))



if __name__ == "__main__":
	viz.go()