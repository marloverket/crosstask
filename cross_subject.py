from subject import Subject
import os
design_dir = os.path.join(os.getcwd(),"design_files")
def design_parse(path):
	# FORMAT: 
	# onset, wait time, re_deadline, disappearing_part
	# 3,6,.6,"hbar"
	fop = open(path,"r")
	trials = []
	for line in fop:
		spl= line.split()
		trials.append(
		  [float(spl[0]),float(spl[1]),float(spl[2]),spl[3]])
	return trials

class CrossSubject(Subject):
	def __init__(self):
		""" Subject class for the redo of the 
		Katkin and Blascovich 1993 Cross experiment.
		"""
		super(Subject,self).__init__()
		
	def get_experiment(self):
		design_file = ".".join(
			[self.subject_id, self.day_num, self.run_num,"txt"])
		self.design_file = os.path.join(design_dir,design_file)
		