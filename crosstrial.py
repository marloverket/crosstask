"""
The disappearing cross task reimplemented from Blascovich & Katkin 1993.
mattcieslak@gmail.com
"""
from fmri_trigger import FmriTrigger,FakeFmriTrigger

# -------- Configuration ----------------
MRI = False
# ---------------------------------------

class TriggerCounter(object):
	def __init__(self):
		pass
		



if __name__ == "__main__":
	# Create an object that sends timed trigger pulses
	if MRI:
		trigger = FmriTrigger()
	else:
		trigger = FakeFmriTrigger()
		
	