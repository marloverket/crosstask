﻿import viz, viztask
from cross_subject import CrossSubject 
import fmri_trigger
global subj, trigger


def get_trigger():
	global subj, trigger 
	if subj.is_scanning:
		print "USING LUMINA BOX TRIGGERS"
		trigger = fmri_trigger.FmriTrigger()
	else:
		print "USING SIMULATED TRIGGER PULSES"
		trigger = fmri_trigger.FakeFmriTrigger()
	trigger.start()
	yield

def next_block():
	global subj
	
def experiment():
	# -- Launch the vizinfo panel
	global subj, trigger
	subj = CrossSubject()
	yield subj.grab_info()
	
	# -- Where will the trigger pulses be coming from?
	yield get_trigger()
	
	# -- Start the experiment, waiting for a trigger
	for block in subj.blocks:
		yield block()
	
	# -- write the data we just collected to text
	subj.write_data()

if __name__=="__main__":
	viz.go()
	
	# ------ Options for vizard display
	viz.vsync(0)
	viz.setOption('viz.max_frame_rate',60)
	
	# ------ Run the experiment!
	viztask.schedule(experiment())