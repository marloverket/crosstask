import viz,vizinfo,viztask,vizact
from datetime import datetime
global subj
"""
Adds a panel to the screen where the subject info gets 
filled out.
"""
info_box = vizinfo.add('')
info_box.scale(2,2)
info_box.translate(0.85,0.8)
info_box.title('Participant Info')

#Add the GUI elements to the box
id_box = info_box.add(viz.TEXTBOX,'Participant ID')
day_box = info_box.add(viz.TEXTBOX, 'Day')
run_box = info_box.add(viz.TEXTBOX, 'Run Number')
scan_box = info_box.add(viz.TEXTBOX,'Scanner')
run_button = info_box.add(viz.BUTTON,'Run')
info_box.visible(viz.OFF)

class Subject(object):
	def __init__(self):
		self.init_time = datetime.now().strftime("%Y.%m.%d.%H.%M")
		self.time_offset = -1
		
	def set_time_offset(self, timestamp):
		"""
		If the experiment relies on an external trigger
		to begin, set the timing offset, so that when we
		dump this subject's behavioral data, 
		"""
		self.time_offset = timestamp
		
	def grab_info(self):
		""" Reads the information from the vizinfo
		widgets and fills in details about this
		subject.
		"""
		self.show_gui()
		yield viztask.waitButtonUp(run_button)
		self.subject_id = "S%03i"%int(id_box.get())
		self.run_num = "R%02i"%int(run_box.get())
		self.day_num = "D%02i"%int(day_box.get())
		scanner = scan_box.get()
		self.is_scanning = (scanner == "1")
		info_box.remove()
		
	def show_gui(self):
		info_box.visible(viz.ON)
		
	def get_experiment(self):
		"""
		Experiment files should be named such that it is unambiguous
		which file should go with this subject/day/run. 
		"""
		raise NotImplementedError(
		    "Must be overwritten in subclass")

if __name__=="__main__":
	viz.go()
	viztask.schedule(experiment())