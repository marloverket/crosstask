﻿from subject import Subject
import os
from datetime import datetime
from design.sequence import create_full_experiment, DEFAULT_DEADLINES, N_TRIALS_PER_BLOCK
design_dir = os.path.join(os.path.dirname(__file__),"design_files")
rt_dir = os.path.join(os.path.dirname(__file__),"rt_data")

# ----- Can't get numpy installed on my development version of vizard
def inverse_normcdf(percentile,mu,sigma):
	# Nope. Wish I had numpy
	return percentile * mu
	

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
	def __init__(self,experimental_deadlines=False):
		""" Subject class for the redo of the 
		Katkin and Blascovich 1993 Cross experiment.
		
		If this is a training block, set RT deadlines to 
		`design.sequence.DEFAULT_DEADLINE`
		
		If this is an experimental block, set the RT deadlines to
		a percentage of the CDF of the subject's RT distribution.
		
		Parameters:
		===========
		experimental_deadlines:bool
		  Use a experimental deadlines for each trial? If True reads in
		  rt_params.txt and rt_deadlines.txt from design_dir.
		"""
		super(Subject,self).__init__()
		# deadline in seconds or percentage?
		self.experimental_deadlines = experimental_deadlines
		self.collected_data = []
	
	def get_rt_deadlines(self):
		""" Reads a test file with the RT deadlines for each block.
		If the specified RT's are in seconds"""
		
		# Use a fixed RT in a practice block
		if not self.experimental_deadlines:
			return DEFAULT_DEADLINES
		
		# Read in the RT percentages from a file for this subject
		design_file = ".".join(
			[self.subject_id, self.day_num, self.run_num,"rt_deadlines","txt"])
		rt_deadline_file = os.path.join(design_dir,design_file)
		if not os.path.exists(rt_deadline_file):
			raise WindowsError("RT deadline file %s does not exist"%rt_deadline_file)
		fop = open(rt_deadline_file,"r")
		deadlines = map(float,fop.readlines().strip().split())
			
		# The subject's mean and sd from trial runs
		params_file = ".".join(
			[self.subject_id,"rt_parameters","txt"])
		rt_param_file = os.path.join(design_dir,design_file)
		if not os.path.exists(rt_param_file):
			raise WindowsError("RT Parameters file %s does not exist"%rt_param_file)
		fop = open(rt_param_file,"r")
		self.rt_mean,self.rt_sd = map(float,fop.readlines().strip().split())
		
		return [ inverse_normcdf(dl,self.rt_mean,self.rt_sd) for dl \
					in deadlines ]
		
	def get_experiment(self):
		""" Looks for a file for this run
		"""
		design_file = ".".join(
			[self.subject_id, self.day_num, self.run_num,"txt"])
		self.design_file = os.path.join(design_dir,design_file)
		
		if not os.path.exists(self.design_file):
			if self.experimental_deadlines:
				raise ValueError("No design file exists")
			block_deadlines = self.get_rt_deadlines()
			self.blocks = create_full_experiment(block_deadlines)
		else:
			self.blocks = design_parse(self.design_file)
	
	def add_block_data(self,blocknum,data):
		for dat in data:
			dat["blocknum"] = blocknum
			dat["subject"] = self.subject_id
			self.collected_data.append(dat)
	
	def write_data(self):
		"""Writes out data for analysis in R
		"""
		output_file = ".".join(
			[self.subject_id, self.day_num, self.run_num,
			datetime.now().strftime("%Y.%m.%d.%H.%M"), "dat"])
		self.data_file = os.path.join(rt_dir,output_file)
		fop = open(self.data_file,"w")
		data_fmt = [("subject",      "%s"),             # Subject ID
					("rt",           "%.4f"),			# Response time
					("changetime",   "%.3f"),			# Time display changed
					("blocknum",     "%i"),				# Block Number
					("success",      "%i"),				# Speed & Accuracy?
					("speed_success","%i"),				# Fast enough?
					("acc_success",  "%i"),				# Accurate?
					("onset",        "%.3f"),			# Circle cue appears
					("crossbar",     "%s"),				# Disappearing part
					("duration",	 "%.3f"),			# Time b/w cue & target
					("rt_deadline",  "%.3f")			# Required Speed
					]
					
		header = "\t".join([a for a,b in data_fmt] + ["trialnum"])
		trials = []
		for trialnum,trial in enumerate(self.collected_data):
			trials.append("\t".join([fmt%trial[key] for key,fmt in data_fmt]+["%i"%trialnum]))
		fop.write("\n".join([ header ] + trials))
		fop.close()
		print "Wrote", output_file

if __name__=="__main__":
	import viz,viztask
	viz.go()
	subj = CrossSubject()
	def tester():
		yield subj.grab_info()
	viztask.schedule(tester())