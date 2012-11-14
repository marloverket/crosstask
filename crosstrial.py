"""
The disappearing cross task reimplemented from Blascovich & Katkin 1993.
mattcieslak@gmail.com
"""
from fmri_trigger import TRIGGER_EVENT
import viz, vizact, viztask, vizinfo
# Images
cue = viz.addTexture("images/cue.png")
hbar = viz.addTexture("images/hbar.png")
vbar = viz.addTexture("images/vbar.png")
cross = viz.add("images/cross.png")
# Text for feedback
block_text = viz.addText("",parent=viz.SCREEN)
block_text.setPosition(0.5,0.8)
block_text.alignment(viz.ALIGN_CENTER_CENTER)
block_text.font("times.ttf")

#Add quad to screen
quad = viz.addTexQuad( viz.SCREEN , pos=(0.5,0.5,0) , scale=(5,5,5) )
#quad.texture(cross)

def success_display():
	 block_text.message("Success")
	 
	
def fail_display():
	block_text.message("Failure")
	
def end_block(correct,ntrials):
	block_text.message("SCORE: %i/%i"%(correct,ntrials))
	viztask.waitTime(1)
	block_text.message("")

def cross_trial(start_time, wait_time, rt_deadline, remove, message=""):
	""" Implements a single trial
	Parameters
	==========
	start_time:float
	  IF start_time == 0, wait for the next trigger pulse. Else,
	  wait until start_time to begin the trial.
	wait_time:float
	  time to wait until the cross should remove one of its lines
	rt_deadline:float
	  if the subject did not respond more quickly than the deadline,
	  tell them they blew it
	remove:str
	  The portion of the cross to remove. Either "hbar" or "vbar".
	"""
	descr = {"onset":start_time,
			 "duration":wait_time,
			 "crossbar":remove}
	new_texture = hbar if remove == "vbar" else vbar
	if start_time == 0:
		yield vizact.waitsignal(TRIGGER_EVENT)
	else:
		while viz.tick() < start_time:
			yield viz.waitTime(0.01)
	# ---- If there's a message, set it to persist throughout 
	#	   the trial
	block_text.message(message)
	
	# ---- Flash the cue
	quad.texture(cue)
	yield viztask.waitTime(0.5)
	quad.texture(cross)
	
	# ---- Wait the required time
	yield viztask.waitTime(wait_time)
	
	# ---- Set the new texture
	quad.texture(new_texture)
	#Wait for next frame to be drawn to screen
	d = yield viztask.waitDraw()

	#Save display time
	displayTime = d.time

	#Wait for keyboard reaction
	d = yield viztask.waitKeyDown(None)

	#Calculate reaction time
	reactionTime = d.time - displayTime

	#Print reaction time
	print 'Reaction time:',reactionTime
	if reactionTime < rt_deadline:
		success = 1
		yield success_display()
	else:
		success = 0
		yield fail_display()
	quad.texture(cross)
	descr["success"]    = success
	descr["rt"]         = reactionTime
	descr["rt_deadline"]= rt_deadline
	descr["changetime"] = d.time
	viztask.returnValue(descr)
	
def cross_block(list_of_trials):
	# keep track of trial results
	results = []
	successes = 0
	# Keep the duration text visible for the first trial
	res = yield cross_trial(*list_of_trials[0],
			message="DEADLINE: %.2f"%list_of_trials[0][2])
	print "type res:", type(res)
	print res
	results.append(res)
	successes += results[0]["success"]
	# Loop over the rest of the trials
	for trial in list_of_trials[1:]:
		res = yield cross_trial(*trial)
		results.append(res)
		successes += results[-1]["success"]
	# Display successes at the end
	yield end_block(successes,len(list_of_trials))
	yield viztask.waitTime(4)
	# Clear the message
	block_text.message("")
	viztask.returnValue( results )

if  __name__ == "__main__":
	viz.go()
	viz.clearcolor(viz.GRAY)
	from design.sequence import create_full_experiment
	def multitrial():
		results = []
		blocks = create_full_experiment([0.3, 0.2, 0.4, 0.5])
		for block in blocks:
			results += yield cross_block(block)
		viztask.returnValue(results)
	res = viztask.schedule(multitrial())