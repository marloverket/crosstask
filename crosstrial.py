"""
The disappearing cross task reimplemented from Blascovich & Katkin 1993.
mattcieslak@gmail.com
"""
from fmri_trigger import TRIGGER_EVENT, RIGHT_BUTTON_EVENT, LEFT_BUTTON_EVENT
import viz, vizact, viztask, vizinfo
# Images
cue = viz.addTexture("images/cue.png")
hbar = viz.addTexture("images/hbar.png")
vbar = viz.addTexture("images/vbar.png")
cross = viz.add("images/cross.png")
# Sounds
correct_sound   = viz.addAudio("images/beep-8.wav")
incorrect_sound = viz.addAudio("images/beep-3.wav")

# Text for feedback
block_text = viz.addText("",parent=viz.SCREEN)
block_text.setPosition(0.5,0.8)
block_text.alignment(viz.ALIGN_CENTER_CENTER)
block_text.font("times.ttf")
MESSAGE_TIME = 1

# ---------- Configure so responses are mapped to cross components --
HBAR_RESPONSE = viztask.waitEvent(LEFT_BUTTON_EVENT,all=True)
VBAR_RESPONSE = viztask.waitEvent(RIGHT_BUTTON_EVENT,all=True)
# -------------------------------------------------------------------

#Add quad to screen
quad = viz.addTexQuad( viz.SCREEN , pos=(0.5,0.5,0) , scale=(5,5,5) )
#quad.texture(cross)
def training_display(rt,acc):
	print "acc",acc
	if acc:
		msg = "RIGHT"
		correct_sound.play()
	else:
		msg = "WRONG"
		incorrect_sound.play()
	block_text.message(msg + " %.2fs"%rt)
	vizact.ontimer2(rate=MESSAGE_TIME, repeats=0,func=clear_text)
	
def success_display():
	 #block_text.message("Success")
	 #vizact.ontimer2(rate=MESSAGE_TIME, repeats=0,func=clear_text)
	 pass
def fail_display():
	#block_text.message("Failure")
	#vizact.ontimer2(rate=MESSAGE_TIME, repeats=0,func=clear_text)
	pass
	
def end_block(correct,ntrials):
	block_text.message("SCORE: %i/%i"%(correct,ntrials))
	#block_text.visible(True)
	#viztask.waitTime(1)
	#block_text.visible(False)
	
def clear_text():
	block_text.message("")

def cross_trial(start_time, wait_time, rt_deadline, remove, 
					message="",training=False):
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
			
	# ---- If there's a message, display it for MESSAGE_TIME
	block_text.message(message)
	vizact.ontimer2(rate=MESSAGE_TIME, repeats=0,func=clear_text)
	
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

	#Wait for a reaction
	reaction = yield viztask.waitAny( 
		[HBAR_RESPONSE,
		 VBAR_RESPONSE] )
	time_at_response, = reaction.data.data[0]

	# How did they do??
	# -> Hbar remains
	if reaction.condition is HBAR_RESPONSE:
		descr["acc_success"] = remove == "vbar"
		response = "hbar"
	# -> vbar remains
	if reaction.condition is VBAR_RESPONSE:
		descr["acc_success"] = remove == "hbar"
		response = "vbar"
		
	print "removed:", remove,"responded:",response
	#Calculate reaction time
	reactionTime = time_at_response - displayTime
	descr["speed_success"] = reactionTime < rt_deadline
	success = descr["speed_success"] and descr["acc_success"]
	# What sort of feedback to give?
	if training:
		# In training blocks, show the rt
		yield training_display(reactionTime,descr["acc_success"])
	else:
		if success:
			yield success_display()
		else:
			yield fail_display()
	
	quad.texture(cross)
	descr["response"]   = response
	descr["success"]    = success
	descr["rt"]         = reactionTime
	descr["rt_deadline"]= rt_deadline
	descr["changetime"] = d.time
	viztask.returnValue(descr)
	
def cross_block(list_of_trials,training=False):
	# keep track of trial results
	results = []
	successes = 0
	# Keep the duration text visible for the first trial
	res = yield cross_trial(*list_of_trials[0],
			message="DEADLINE: %.2f"%list_of_trials[0][2],training=training)
	print "type res:", type(res)
	print res
	results.append(res)
	successes += results[0]["success"]
	# Loop over the rest of the trials
	for trial in list_of_trials[1:]:
		res = yield cross_trial(*trial,training=training)
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
			results += yield cross_block(block,training=True)
		viztask.returnValue(results)
	res = viztask.schedule(multitrial())