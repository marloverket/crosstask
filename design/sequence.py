"""
Generates a sequence of trials that satisfy
a mixed-block/event related design (Visscher et al 2003, NeuroImage).
Currently: no M-sequence. I'll look into this as the time for scanning
gets closer. For now, it's pseudo-random
"""
import random

# How long to wait before the first block of trials (seconds)
INITIAL_WAIT_TIME   = 5
# Number of blocks that will contain trials
N_TRIAL_BLOCKS      = 2
# How long should each block last? (seconds)
BLOCK_DURATION      = 40
# How many trials per block?
N_TRIALS_PER_BLOCK  = 10
# What is the minimum time a trial might take?
MIN_TRIAL_DURATION  = 1
# How long is the rest block?
REST_DURATION       = 20
# Number of inter-trial intervals in a block
N_ITIs_PER_BLOCK = N_TRIALS_PER_BLOCK - 1
# Minimum ITI length
MIN_ITI_DURATION    = 2
# What is the default RT deadline if none is specified?
DEFAULT_DEADLINE    = 1.5
# ----- 11/25/12 -- Decided we will use varying deadlines each block
MAX_DEADLINE = 0.9      # Seconds
MIN_DEADLINE = 0.25    # Seconds
stepsize = (MAX_DEADLINE-MIN_DEADLINE)/(N_TRIAL_BLOCKS-1)
DEFAULT_DEADLINES = [(n*stepsize+ MIN_DEADLINE) for n in range(N_TRIAL_BLOCKS)]
random.shuffle(DEFAULT_DEADLINES) # Shuffle the order

def random_split(time_to_fill,ntimes):
	"""Given an amount of time, split it into `ntimes` random pieces
	Parameters:
	===========
	time_to_fill:float
	  Amount of time that needs to be divided into `ntimes` pieces
	ntimes:int
	  Number of times which `time_to_fill` needs to be divided into
	  
	Example:
	========
	>>> len(random_split(30,5))
	5
	>>> sum(random_split(30,5))
	30
	"""
	# Pad with zero and the max time
	randos = [0] + sorted([random.uniform(0,time_to_fill) for n \
						in range(ntimes-1)])
	randos.append(time_to_fill)
	# split for a diff
	first = randos[:-1]
	second = randos[1:]
	return [ b-a for a,b in zip(first,second) ]

def create_block(block_onset,rt_deadline):
	"""
	Creates a block of trials with a designated RT deadline.
	Parameters:
	===========
	block_onset:float
	  Time since the experiment starts when this block of trials begins
	rt_deadline:float
	  Subject must respond faster than this time for a trial to be correct
	
	Returns:
	========
	block_trials:list
	  A list of lists that contain details of a trial. It will look like this:
	[
		[ onset_time, trial_duration, reaction_time_deadline, disappearing_part ],
		.....
	]
	"""
	# Check that it is possible to include at least the minimum duration of 
	# trials and ITI's
	min_duration = N_ITIs_PER_BLOCK*MIN_ITI_DURATION + \
					N_TRIALS_PER_BLOCK*MIN_TRIAL_DURATION

	# Number of total events per block
	n_events = N_ITIs_PER_BLOCK + N_TRIALS_PER_BLOCK
	if  min_duration > BLOCK_DURATION:
		raise ValueError(
			"""User has requested impossible parameters!\n
				Check that N_TRIALS_PER_BLOCK, N_ITIs_PER_BLOCK
				and their respective MIN DURATIONS will fit into
				BLOCK_DURATION
						""")
	# Calculate how much time we have to mess with durations
	residual_block_time = BLOCK_DURATION - min_duration
	
	# Begin with each trial it it's minumum duration
	iti_durations   = [ MIN_ITI_DURATION ] * N_ITIs_PER_BLOCK
	trial_durations = [ MIN_TRIAL_DURATION ] * N_TRIALS_PER_BLOCK
	
	# Algorithm: generate n_events random numbers 
	# between 0 and `residual_block_times`, sorts then
	# then adds the diffs to the ITI's and trial durations
	adjustments = random_split(residual_block_time,n_events)
	for n in range(N_TRIALS_PER_BLOCK):
		trial_durations[n] += adjustments.pop()
	for n in range(N_ITIs_PER_BLOCK):
		iti_durations[n] += adjustments.pop()
		
	# Now that they're adjusted to be unpredictable, get their onset
	# times in the actual experiment
	onsets = []
	_current_time = block_onset
	for duration in trial_durations:
		onsets.append(_current_time)
		if len(iti_durations): _current_time += iti_durations.pop()
		_current_time += duration

	# What's going to disappear?
	# NOTE: This is ***random***, not counterbalanced
	trial_options = ("hbar","vbar")
	disappearing_components = [ trial_options[random.randint(0,1)] for n \
								in range(N_TRIALS_PER_BLOCK) ]

	# Make the list of trial lists
	block_trials = []
	for onset, trial_duration, component in zip(
				onsets,trial_durations,disappearing_components):
		block_trials.append([onset,trial_duration,rt_deadline,component])
		
	return block_trials

def create_full_experiment(rt_deadlines):
	"""
	Reads the parameters from the beginning of this file and creates
	a big list of trials.
	
	Parameters:
	===========
	rt_deadlines:list of float
	  A list of length N_TRIAL_BLOCKS that contains the reaction time
	  deadline percentage for the subject.
	
	Returns:
	========
	experiment:list
	  A list containing all blocks for an experiment.
	"""
	experiment = []  
	_time = INITIAL_WAIT_TIME
	for n_block in range(N_TRIAL_BLOCKS):
		experiment += [create_block(_time,rt_deadlines[n_block])]
		_time += BLOCK_DURATION + REST_DURATION
		
	# Check that all blocks are accounted for
	assert len(experiment) == N_TRIAL_BLOCKS
	return experiment
		
if __name__=="__main__":
	viz.go()
	# What deadline will be used each block?
	rt_deadlines = [ 0.2, 0.5, 0.3, 0.4 ]
	experiment =  create_full_experiment(rt_deadlines)