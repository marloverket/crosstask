"""
The disappearing cross task reimplemented from Blascovich & Katkin 1993.
mattcieslak@gmail.com
"""
from fmri_trigger import TRIGGER_EVENT
import viz, vizact, viztask, vizinfo
#CENTER = 
cue = viz.addTexture("images/cue.png")
hbar = viz.addTexture("images/hbar.png")
vbar = viz.addTexture("images/vbar.png")
cross = viz.add("images/cross.png")

#Add quad to screen
quad = viz.addTexQuad( viz.SCREEN , pos=(0.5,0.5,0) , scale=(5,5,5) )
quad.texture(cross)

def success_display():
	print "SUCCESS"
	
def fail_display():
	print "FAILURE"

def cross_trial(start_time, wait_time, rt_deadline, remove):
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
	
	new_texture = hbar if remove == "vbar" else vbar
	if start_time == 0:
		yield vizact.waitsignal(TRIGGER_EVENT)
	else:
		while viz.tick() < start_time:
			yield viz.waitTime(0.01)

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
		yield success_display()
	else:
		yield fail_display()
	quad.texture(cross)
	
if  __name__ == "__main__":
	viz.go()
	viz.clearcolor(viz.GRAY)
	def multitrial():
		tasks = [[3,6,.6,"hbar"],
				 [14,2,.5,"vbar"],
				 [21,6,.6,"hbar"],
				 [30,2,.5,"vbar"],
				]
		for task in tasks:
			yield cross_trial(*task)
	viztask.schedule(multitrial())