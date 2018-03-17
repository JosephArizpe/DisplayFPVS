# Author: Joseph M. Arizpe at Harvard Medical School.  The code draws some lines from John Naulty Jr.'s SSVEP code for openBCI from GitHub
#
# Made with PsychoPy Version 1.84.2
# Date: May-June 2017...ah, fun times.

from psychopy import visual, core, event, gui, logging
import os
import sys
import random
import math
import csv
import imghdr

ACTUAL_SCREEN_RESOLUTION = [5120,2880] # Change this to reflect the actual screen resolution, or else your stimuli will be the wrong sizes

class SSVEP:
	#init sets the window(mywin), and the frequency of the flashing (frame_on => number of frames that the image is visible, frame_off => number of frames that only the background is visible)
	#Frame duration in seconds = 1/monitorframerate(in Hz)
	#Thus the fastest frame rate could be 1 frame on 1 frame off
	
	
	# IMPORTANT NOTE:  The values between the parentheses just below in this initialization set the DEFAULT values, NOT necessarily the ACTUAL values for your run, which can be set in the instatiation at the BOTTOM of this script
	# IN OTHER WORDS:  Do NOT touch these default init values, unless you know what you are doing.
	def __init__(self, mywin=visual.Window(size=ACTUAL_SCREEN_RESOLUTION,color=[138,138,138], colorSpace='rgb255', fullscr=False , monitor='testMonitor',units='deg'),
				frame_off=1, target_freq=6, blockdur = 5.0, port='/dev/ttyACM0',
				fname='SSVEP', numblocks=1, waitdur=2, randomlyVarySize=False, isSinusoidalStim=True, doFixationTask=True, numFixColorChanges=8, fixChangeDurSecs=0.2, minSecsBtwFixChgs=1.2, showDiodeStimulator=True):
		
		self.baseStimDir = 'stimuli'#'stimuli'  # folder containing the image directories for each category
		self.StimDir = ['objects','faces'] # the image category directory names
		self.StimPattern = [4, 1] # [n base images - n oddball images] -> change this to change the oddball pattern
		self.doRandomList = False # i.e. no periodic pattern for the oddball.  Use this for making a "base rate" condition.
		self.mywin = mywin
		self.stimSize = [6.53,6.53]
		self.randomlyVarySize = randomlyVarySize
		self.fadeIn = True
		self.fadeInCycles = 2.0 # important: put the decimal
		self.fadeOut = True
		self.fadeOutCycles = 2.0 # important: put the decimal
		self.sizePercentRange = [74, 120]
		self.sizePercentSteps = 2
		self.isSinusoidalStim = isSinusoidalStim
		self.doFixationTask = doFixationTask
		self.normalFixColor = [0,0,0]
		self.detectFixColor = [255,0,0]
		self.showDiodeStimulator = showDiodeStimulator
		self.diodeOnStimColor = [255,255,255]
		self.diodeOffStimColor = [0,0,0]
		self.respondChar = 'space'
		
#		self.pattern1 = visual.GratingStim(win=self.mywin, name='pattern1',units='deg',
#						tex=None, pos=[0, 0], size=self.stimSize, color=self.mywin.color, colorSpace='rgb255',
#						opacity=1,interpolate=True)
		self.pattern2 = visual.ImageStim(win=self.mywin, name='pattern2',units='deg',
						pos=[0, 0], size=self.stimSize,
						opacity=1,interpolate=True)
		#self.fixation = visual.GratingStim(win=self.mywin, name='fixation', size = 0.3, pos=[0,0], sf=0, color=[0,0,0], colorSpace='rgb255')
		self.fixation = visual.TextStim(win=self.mywin, text='+', name='fixation', units='deg', height = 0.5, pos=[0,0], color=self.normalFixColor, colorSpace='rgb255')
		self.diodeStimulator = visual.GratingStim(win=self.mywin, name='diodeStim',units='norm',
						tex=None, pos=[-1, -1], size=[0.1,0.1], color=[0,0,0], colorSpace='rgb255',
						opacity=1,interpolate=True)
		self.frame_off = frame_off
		self.frameRate = self.mywin.getActualFrameRate()
		print "Detected Monitor Refresh: " + str(self.frameRate)
		self.targFreq = target_freq
		self.StimulationFreq = self.frameRate/(round(self.frameRate/self.targFreq)) #calculate actual stimulation frequency rounded to the screen refresh rate
		print "Actual Stimulation Frequency: " + str(self.StimulationFreq)
		self.framesPerCycle = round(self.frameRate/self.targFreq) # rounded to the screen refresh rate
		print "Frames Per Individual Stimulus Cycle: " + str(self.framesPerCycle)
		self.frame_on = int(self.framesPerCycle) - self.frame_off
		self.blockdur = blockdur
		self.fname = fname
		self.numblocks = numblocks
		self.waitdur = waitdur
		self.port = port
		
		# -------------  Uncomment only the relevant line for your experiment!!!  -------------
		#self.stimFileName = self.Generate_stimListOddball()  # Uncomment for exemplar oddball experiments
		self.stimFileName = self.Generate_stimList()  # Uncomment for base category vs. oddball category experiments
		# -------------------------------------------------------------------------------------
		
		kHandle = open(self.stimFileName)
		kReader = csv.reader(kHandle,'excel-tab')
		self.stimMat = []
		for row in kReader:
			self.stimMat.append(row[0])
		#print self.stimMat
		
		self.fixChangeDurSecs = fixChangeDurSecs
		self.minSecsBtwFixChgs = minSecsBtwFixChgs
		if self.doFixationTask:
			framesPerSec = self.StimulationFreq * self.framesPerCycle
			self.numFixColorChanges = numFixColorChanges
			self.numFramesFixChange = int(round(framesPerSec*fixChangeDurSecs))
			print "Num Frames Each Fix Color Change: "+str(self.numFramesFixChange)
			self.minFramesBtwFixChgs = int(math.ceil(framesPerSec*minSecsBtwFixChgs))
			
			totFrames = len(self.stimMat) * self.framesPerCycle
			print "Total Frames: "+str(totFrames)
			self.fixChgFrames = []
			tooManyTries = 1000
			for fixChangeInd in range(self.numFixColorChanges):
				thisChgFrame = random.randint(self.numFramesFixChange,totFrames-self.numFramesFixChange-self.minFramesBtwFixChgs)
				if fixChangeInd > 0:
					moreThanOneSecDiffsFromThis = [abs(x - thisChgFrame) > self.minFramesBtwFixChgs for x in self.fixChgFrames]
					howManyTries = 0
					while not all(moreThanOneSecDiffsFromThis):
						thisChgFrame = random.randint(self.numFramesFixChange,totFrames-self.numFramesFixChange-self.minFramesBtwFixChgs)
						moreThanOneSecDiffsFromThis = [abs(x - thisChgFrame) > self.minFramesBtwFixChgs for x in self.fixChgFrames]
						#print moreThanOneSecDiffsFromThis
						howManyTries = howManyTries + 1
						if howManyTries >= tooManyTries:
							print "ERROR: You put too many fixation color change events and/or set too wide a minimum spacing between the events to actually fit in the experiment."
							print "Adjust these parameters or you will likely run into this problem again!!!"
							sys.exit()
				self.fixChgFrames.append(thisChgFrame)
			self.fixChgFrames.sort()
			self.fixChgBackFrames = [x + self.numFramesFixChange for x in self.fixChgFrames]
			self.fixChgsDetected = [0] * len(self.fixChgFrames)
			#print self.fixChgFrames
			#print self.fixChgBackFrames
		
		if self.randomlyVarySize:
			self.sizesFileName = "SizesOf"+self.stimFileName
			possiblePercentVals = range(self.sizePercentRange[0],self.sizePercentRange[1]+self.sizePercentSteps,self.sizePercentSteps)
			self.randScalingVals = []
			for i in range(len(self.stimMat)):
				nextVal = random.choice(possiblePercentVals)*0.01
				while i > 0 and nextVal == self.randScalingVals[-1]:
					nextVal = random.choice(possiblePercentVals)*0.01
				self.randScalingVals.append(nextVal)
			with open(self.sizesFileName,"w") as saveFile:
				for size in	self.randScalingVals:
					saveFile.write("%s\n" % size)
		else:
			self.sizesFileName = "Not Applicable"
			self.sizePercentRange = [100, 100]
			self.sizePercentSteps = 0

	def Generate_stimList(self):
		self.tryNum = 1
		ListSaveName = "Stimuli_list_"+self.fname+"_"+str(self.tryNum)+".txt" # saves a list of your stimuli to be used during presentation
		while os.path.isfile(ListSaveName):
			self.tryNum = self.tryNum + 1
			ListSaveName = "Stimuli_list_"+self.fname+"_"+str(self.tryNum)+".txt" # saves a list of your stimuli to be used during presentation
		
		#calculate n of stims needed
		#NbStims = int(math.ceil(self.blockdur*self.StimulationFreq)) #calculate n of stimuli to display sequence duration
		NbPatterns = self.numblocks*int(math.ceil(self.blockdur*self.StimulationFreq/sum(self.StimPattern))) #(NbStims / sum(self.StimPattern))
		
		# Get names of all stimuli in directories and shuffle the order within each stimulus type
		AllStims = []
		for e in range(len(self.StimDir)):
			AllStims.append([])
			files = [f for f in os.listdir(os.path.join(self.baseStimDir,self.StimDir[e])) if (os.path.isfile(os.path.join(self.baseStimDir,self.StimDir[e], f))  and (imghdr.what(os.path.join(self.baseStimDir,self.StimDir[e], f)) is not None))] # get names of all stimuli in directories
			random.shuffle(files)
			for i in range(len(files)):
				AllStims[e].append(os.path.join(self.baseStimDir,self.StimDir[e], files[i]))

		StimList = []
		stimInds = [0, 0]
		for i in range(NbPatterns):
			for stimType in range(len(self.StimPattern)):
				for stimRep in range(self.StimPattern[stimType]):
					#print stimInds[stimType]
					StimList.append(AllStims[stimType][stimInds[stimType]])
					stimInds[stimType] += 1
					if stimInds[stimType] >= len(AllStims[stimType]):
						stimInds[stimType] = 0
						random.shuffle(AllStims[stimType])
						while StimList[-1] is AllStims[stimType][0]: # while the last stimulus is the same as the next random one for this stimulus type, re-randomize so as to avoid repeats of identical stimuli
							random.shuffle(AllStims[stimType])

		if self.doRandomList:
			random.shuffle(StimList)
			
		with open(ListSaveName,"w") as saveFile:
			for stim in StimList:
				saveFile.write("%s\n" % stim)

		return ListSaveName

	def waitForTrigger(self):
		self.instructions	= visual.TextStim(self.mywin, text	= "Waiting for trigger",pos = [0,0])
		self.triggerChar = 't'
		response = False
		self.mywin.clearBuffer()
		self.instructions.draw()
		self.mywin.update()
		
		notTriggered = 1
		while notTriggered:
			self.response = event.getKeys()
			if self.response:
				if self.response[0] == 'escape':
					sys.exit()
				elif self.response[0] == self.triggerChar:
					notTriggered = 0

	def Generate_stimListOddball(self):
		self.tryNum = 1
		ListSaveName = "OddballStimuli_list_"+self.fname+"_"+str(self.tryNum)+".txt" # saves a list of your stimuli to be used during presentation
		while os.path.isfile(ListSaveName):
			self.tryNum = self.tryNum + 1
			ListSaveName = "OddballStimuli_list_"+self.fname+"_"+str(self.tryNum)+".txt" # saves a list of your stimuli to be used during presentation
			
		#calculate n of stims needed
		NbPatterns = self.numblocks*int(math.ceil(self.blockdur*self.StimulationFreq/sum(self.StimPattern))) #(NbStims / sum(self.StimPattern))
		
		# Get names of all stimuli in directories and shuffle the order within each stimulus type
		AllStims = []
		AllStims.append([])
		AllStims.append([])
		files = [f for f in os.listdir(self.baseStimDir) if (os.path.isfile(os.path.join(self.baseStimDir, f)) and (imghdr.what(os.path.join(self.baseStimDir, f)) is not None))] # get names of all stimuli in directories
		random.shuffle(files)
		for i in range(len(files)):
			AllStims[1].append(os.path.join(self.baseStimDir, files[i]))
		# choose the random one that will be the "base" (i.e, not oddball) image, and keep it separate from the others
		AllStims[0].append(AllStims[1][-1])
		del AllStims[1][-1]

		StimList = []
		stimInds = [0, 0]
		for i in range(NbPatterns):
			for stimType in range(len(self.StimPattern)):
				for stimRep in range(self.StimPattern[stimType]):
					#print stimInds[stimType]
					StimList.append(AllStims[stimType][stimInds[stimType]])
					stimInds[stimType] += 1
					if stimInds[stimType] >= len(AllStims[stimType]):
						stimInds[stimType] = 0
						if stimType == 1:
							random.shuffle(AllStims[stimType])
							while StimList[-1] is AllStims[stimType][0]: # while the last stimulus is the same as the next random one for this stimulus type, re-randomize so as to avoid repeats of identical stimuli
								random.shuffle(AllStims[stimType])

		if self.doRandomList:
			random.shuffle(StimList)
		
		with open(ListSaveName,"w") as saveFile:
			for stim in StimList:
				saveFile.write("%s\n" % stim)

		return ListSaveName

#	def collecting(self):
#		self.collector = csv_collector.CSVCollector(fname=self.fname, port= self.port)
#		self.collector.start()
#
#	def epoch(self, mark):
#		self.collector.tag(mark)

	def stop(self):
		self.mywin.close()
		core.quit()
   
	def start(self):
		self.Trialclock = core.Clock()
		self.waitClock = core.Clock()
		#start saving data from EEG device.
		#self.collecting()

		self.count = 0
		self.stimNum = 0
		self.stimulusNumberError = False
		self.stimulusNumberErrorKind = "Not Applicable"
		if self.doFixationTask:
			self.fixChgTimes = [0] * len(self.fixChgFrames)
			self.responseFrameNums = [0] * len(self.fixChgFrames)
			self.responseTimes = [0] * len(self.fixChgFrames)
			self.fixHasChangedThisBlock = False
		
		#pre-calculate the sinusoidal opacity scaling vals
		if self.isSinusoidalStim:
			self.sinPhaseStepSize = 2.0*math.pi/(self.frame_on+1.0)
			self.sinPhaseStep = self.sinPhaseStepSize # start at the step after 0 radians because the frame_off frames aleady constitute the 0 opacity display
			self.OpacityScaleVals = []
			for frameOnNum in range(self.frame_on):
				self.OpacityScaleVals.append((math.cos(self.sinPhaseStep + math.pi)+1.0)/2.0) # the function is adjusted to start at a min of 0 and have a max of 1 mid-way
				self.sinPhaseStep = self.sinPhaseStep + self.sinPhaseStepSize
			self.OpacityScaleVals[self.OpacityScaleVals.index(max(self.OpacityScaleVals))] = 1.0 # Enforce that the max opacity scale val is always 1.0, even when the phase step size would not otherwise allow for it.  If there are two max values, it changes just the first max value to 1.  In practice though there is usually just one max value, even though with an odd number of frame_on frames that max may differ only by a practically infinitesmal amount from another number in the array.  That max is not always the first occuring between those two near identical values.
			print self.OpacityScaleVals
			print "Sinusoidal phase step size (radians): "+str(self.sinPhaseStepSize)
		print "Total number of stimuli (including repeats): "+str(len(self.stimMat))
		totStimuliPrepped = len(self.stimMat)
		self.fadeOutDur = self.fadeOutCycles*sum(self.StimPattern)/self.StimulationFreq
		self.waitForTrigger()
		
		self.diodeStimulator.setAutoDraw(self.showDiodeStimulator)
		while self.count<self.numblocks:
			#self.fixation.setAutoDraw(True) ###
			#clean black screen off
			self.fixation.color = self.normalFixColor
			self.fixation.draw()
			self.mywin.flip()
			
			if self.count == 0:
				self.thisFrameInd = 0
				self.thisFixChangeInd = 0
			
			#wait certain time for next block
			#core.wait(self.waitdur)
			self.waitClock.reset()
			while self.waitClock.getTime()<self.waitdur:
				self.response = event.getKeys()
				if self.response:
					if self.response[0] == 'escape':
						sys.exit()
					elif self.doFixationTask and self.response[0] == self.respondChar and self.thisFixChangeInd > 0 and self.fixHasChangedThisBlock and not self.fixChgsDetected[self.thisFixChangeInd-1]:
						self.timeSinceLastFixChange = self.Trialclock.getTime() - self.timeofLastFixChange
						self.responseTimes[self.thisFixChangeInd-1] = self.timeSinceLastFixChange
						self.responseFrameNums[self.thisFixChangeInd-1] = self.thisFrameInd
						self.fixChgsDetected[self.thisFixChangeInd-1] = 1
					else:
						event.clearEvents()
			
			#reset tagging
			self.should_tag = False
			#self.epoch(0)
			
			self.firstStimNumOfBlock = self.stimNum
			#self.lastStimNumOfBlock = self.firstStimNumOfBlock + totStimuliPrepped/self.numblocks - 1
			self.fixHasChangedThisBlock = False
			#reset clock for next block
			self.Trialclock.reset()
			while self.Trialclock.getTime()<self.blockdur:

				#draws square
				#self.pattern1.setAutoDraw(True)

				"""		 
				###Tagging the data with the calculated frequency###
				Attempting to only get 1 sample tagged, however, this is hard.
				"""		 
				"""alternative way to tag
				if self.should_tag == False:
					#self.epoch(self.freq)
					self.epoch(70)
					self.mywin.flip()
				
				self.epoch(0)
				self.should_tag = True
				"""
				#self.epoch(70)
				
				if self.showDiodeStimulator:
					shownDiodeStim = False
					self.diodeStimulator.color = self.diodeOffStimColor
				
				for frameN in range(self.frame_off):
					if self.doFixationTask:
						if self.thisFixChangeInd < self.numFixColorChanges:
							if self.fixChgFrames[self.thisFixChangeInd] == self.thisFrameInd:
								self.fixation.color = self.detectFixColor
								self.timeofLastFixChange = self.Trialclock.getTime()
								self.fixChgTimes[self.thisFixChangeInd] = self.timeofLastFixChange
								self.fixHasChangedThisBlock = True
								event.clearEvents() # clear responses so any made just before this fix change are not recorded as the response
							elif self.fixChgBackFrames[self.thisFixChangeInd] == self.thisFrameInd:
								self.fixation.color = self.normalFixColor
								self.thisFixChangeInd = self.thisFixChangeInd + 1
								#print self.thisFixChangeInd
				
					self.fixation.draw()
					self.mywin.flip()
					
					self.response = event.getKeys()
					if self.response:
						if self.response[0] == 'escape':
							sys.exit()
						elif self.doFixationTask and self.response[0] == self.respondChar and self.thisFixChangeInd > 0 and self.fixHasChangedThisBlock and not self.fixChgsDetected[self.thisFixChangeInd-1]:
							self.timeSinceLastFixChange = self.Trialclock.getTime() - self.timeofLastFixChange
							self.responseTimes[self.thisFixChangeInd-1] = self.timeSinceLastFixChange
							self.responseFrameNums[self.thisFixChangeInd-1] = self.thisFrameInd
							self.fixChgsDetected[self.thisFixChangeInd-1] = 1
						else:
							event.clearEvents()
		
					self.thisFrameInd = self.thisFrameInd + 1
			
				if self.stimNum >= totStimuliPrepped:
					print "ERROR: The script is trying to show more stimuli than the number originally prepared"
					print "This error is likely due to the actual screen refresh rate not being stable across the run.  To salvage any task data and prevent the code from breaking, no more images will be displayed for the rest of the run!"
					self.stimulusNumberError = True
					self.stimulusNumberErrorKind = "Too few prepped"
					break
				self.pattern2.image = self.stimMat[self.stimNum]
				if self.randomlyVarySize:
					self.pattern2.size = [self.stimSize[0]*self.randScalingVals[self.stimNum],self.stimSize[1]*self.randScalingVals[self.stimNum]]
				
				if self.fadeIn and self.stimNum == self.firstStimNumOfBlock:
					self.stimPeakOpacity = 0.0
				if self.fadeIn and self.stimNum-self.firstStimNumOfBlock < sum(self.StimPattern)*self.fadeInCycles:
					self.stimPeakOpacity = self.stimPeakOpacity + 1.0/(sum(self.StimPattern)*self.fadeInCycles)
				elif self.fadeOut and self.fadeOutDur >= self.blockdur-self.Trialclock.getTime(): #self.stimNum >= (self.lastStimNumOfBlock-sum(self.StimPattern)*self.fadeOutCycles):
					#print self.blockdur-self.Trialclock.getTime()
					self.stimPeakOpacity = self.stimPeakOpacity - 1.0/(sum(self.StimPattern)*self.fadeOutCycles)
					#print self.stimPeakOpacity
				else:
					self.stimPeakOpacity = 1.0
					#print self.stimPeakOpacity
				#print self.pattern2.image
				self.stimNum += 1
				#print self.stimNum
				
				#self.pattern1.setAutoDraw(False)
				#self.pattern2.setAutoDraw(True) ###
				
				if not self.isSinusoidalStim:
					self.pattern2.opacity = self.stimPeakOpacity
				for frameN in range(self.frame_on):
					if self.isSinusoidalStim:
						self.pattern2.opacity = self.stimPeakOpacity * self.OpacityScaleVals[frameN]
						#print self.pattern2.opacity
					if self.showDiodeStimulator:
						if not shownDiodeStim and self.pattern2.opacity == self.stimPeakOpacity:
							self.diodeStimulator.color = self.diodeOnStimColor
							shownDiodeStim = True
						else:
							self.diodeStimulator.color = self.diodeOffStimColor
					if self.doFixationTask:
						if self.thisFixChangeInd < self.numFixColorChanges:
							if self.fixChgFrames[self.thisFixChangeInd] == self.thisFrameInd:
								self.fixation.color = self.detectFixColor
								self.timeofLastFixChange = self.Trialclock.getTime()
								self.fixChgTimes[self.thisFixChangeInd] = self.timeofLastFixChange
								self.fixHasChangedThisBlock = True
								event.clearEvents() # clear responses so any made jsut before this fix change are not recorded as the response
							elif self.fixChgBackFrames[self.thisFixChangeInd] == self.thisFrameInd:
								self.fixation.color = self.normalFixColor
								self.thisFixChangeInd = self.thisFixChangeInd + 1
								#print self.thisFixChangeInd
					
					self.pattern2.draw() # do not set these to auto-draw because then the image always gets drawn over the fixation
					self.fixation.draw() # for the same reason, draw the fixation second
					self.mywin.flip()

					self.response = event.getKeys()
					if self.response:
						if self.response[0] == 'escape':
							sys.exit()
						elif self.doFixationTask  and self.response[0] == self.respondChar and self.thisFixChangeInd > 0  and self.fixHasChangedThisBlock and not self.fixChgsDetected[self.thisFixChangeInd-1]:
							self.timeSinceLastFixChange = self.Trialclock.getTime() - self.timeofLastFixChange
							self.responseTimes[self.thisFixChangeInd-1] = self.timeSinceLastFixChange
							self.responseFrameNums[self.thisFixChangeInd-1] = self.thisFrameInd
							self.fixChgsDetected[self.thisFixChangeInd-1] = 1
						else:
							event.clearEvents()
					
					self.thisFrameInd = self.thisFrameInd + 1
		
				#self.pattern2.setAutoDraw(False) ###
				#print "current frame Num: "+str(self.thisFrameInd)
			#self.epoch(0)
			#count number of blocks
			self.count+=1
	 
			"""
			###Tagging the Data at end of stimulus###
			"""
		print "Last Frame Num: "+str(self.thisFrameInd)
		print "Last Stim Num: "+str(self.stimNum)
		print "Actual Number of Fix Color Changes: "+str(self.thisFixChangeInd)
		
		#self.collector.disconnect()
		#clean black screen off
		self.fixation.color = self.normalFixColor
		self.fixation.draw()
		self.mywin.flip()
		
		#wait certain time for next block
		#core.wait(self.waitdur)
		self.waitClock.reset()
		while self.waitClock.getTime()<self.waitdur:
			self.response = event.getKeys()
			if self.response:
				if self.response[0] == 'escape':
					sys.exit()
				elif self.doFixationTask and self.response[0] == self.respondChar and self.thisFixChangeInd > 0 and self.fixHasChangedThisBlock and not self.fixChgsDetected[self.thisFixChangeInd-1]:
					self.timeSinceLastFixChange = self.Trialclock.getTime() - self.timeofLastFixChange
					self.responseTimes[self.thisFixChangeInd-1] = self.timeSinceLastFixChange
					self.responseFrameNums[self.thisFixChangeInd-1] = self.thisFrameInd
					self.fixChgsDetected[self.thisFixChangeInd-1] = 1
				else:
					event.clearEvents()

		if self.stimNum < totStimuliPrepped:
			self.stimulusNumberError = True
			self.stimulusNumberErrorKind = "More prepped than shown"
		
		if self.doFixationTask:
			self.runData = []
			self.runData.append(self.fixChgFrames)
			self.runData.append(self.fixChgBackFrames)
			self.runData.append(self.fixChgTimes)
			self.runData.append(self.responseFrameNums)
			self.runData.append(self.fixChgsDetected)
			self.runData.append(self.responseTimes)
			#print self.runData
			self.runData = zip(*self.runData) # "transpose" this matix for saving
			#print self.runData
			
#			dataSaveFile = 'runData_'+self.fname+'_run'+str(self.tryNum)+'.txt'
			runNum = 1
			dataSaveFile = 'runData_'+self.fname+'_run'+str(runNum)+'.txt'
			while os.path.isfile(dataSaveFile):
				runNum = runNum + 1
				dataSaveFile = 'runData_'+self.fname+'_run'+str(runNum)+'.txt'
			with open(dataSaveFile, 'w') as csvfile:
				writer = csv.writer(csvfile,delimiter="\t")
				[writer.writerow(r) for r in self.runData]
			print "Task data Saved to: "+dataSaveFile
			fileCorrespondSaveFile = 'runInfo_'+self.fname+'_run'+str(runNum)+'.txt'
		else:
			dataSaveFile = "Not Applicable"
			fileCorrespondSaveFile = 'runInfo_'+self.fname+'_try'+str(self.tryNum)+'.txt'
			
			
		self.runInfo = ["Task data file:   "+dataSaveFile,
					"Stimuli list file:   "+self.stimFileName,
					"Stimuli sizes file:   "+self.sizesFileName,
					"Length of blocks(secs):   "+str(self.blockdur),
					"Number of blocks:   "+str(self.numblocks),
					"Wait time before, between, after blocks (secs):   "+str(self.waitdur),
					"Actual stimulation frequency:   "+str(self.StimulationFreq),
					"Sinusoidal stimulation?:   "+str(self.isSinusoidalStim),
					"Number of frames off (i.e., no stimulus present) btw stimuli:   "+str(self.frame_off),
					"Number of frames on (i.e., stimulus visible) for each stimulus:   "+str(self.frame_on),
					"Non-periodic oddball Stimulation?:   "+str(self.doRandomList),
					"Proportion base vs oddball:   "+str(self.StimPattern[0])+" : "+str(self.StimPattern[1]),
					"Stimulus size (the central size, if varying):   "+str(self.stimSize[0])+" x "+str(self.stimSize[1]),
					"Stimulus size units:   "+self.pattern2.units,
					"Did stimulus size vary?:   "+str(self.randomlyVarySize),
					"Stimulus size range (percent of central size):   "+str(self.sizePercentRange[0])+" - "+str(self.sizePercentRange[1]),
					"Stimulus size steps (percent of central size):   "+str(self.sizePercentSteps),
					"Had fade in?:   "+str(self.fadeIn),
					"Length of fade in (in number of oddball cycles):   "+str(self.fadeInCycles),
					"Had fade out?:   "+str(self.fadeOut),
					"Length of fade out (in number of oddball cycles):   "+str(self.fadeOutCycles),
					"Had fixation task?:   "+str(self.doFixationTask),
					"Number of actual fix color changes:   "+str(self.thisFixChangeInd),
					"Length of each color change (secs):   "+str(self.fixChangeDurSecs),
					"Theoretical minimum time between color change onsets:   "+str(self.minSecsBtwFixChgs),
					"Had diode stimulator?:   "+str(self.showDiodeStimulator),
					"Stimulus Number Error Occurred?:   "+str(self.stimulusNumberError),
					"Kind of stimulus number error: "+str(self.stimulusNumberErrorKind),
					"Number of stimuli (including repeats) prepped: "+str(totStimuliPrepped),
					"Number of stimuli (including repeats) shown: "+str(self.stimNum)]
		#print self.runInfo
		with open(fileCorrespondSaveFile, 'w') as csvfile:
			writer = csv.writer(csvfile,delimiter="\n")
			writer.writerow(self.runInfo)
			#[writer.writerow(r) for r in self.runInfo]

		self.stop()

class InputBox(object):
	
	def __init__(self):
		self.myDlg = gui.Dlg(title="SSVEP Menu")
		self.myDlg.addText('Subject info')
		self.myDlg.addField('Participant:','0')
		self.myDlg.addField('Session', 001)
		self.myDlg.addField('Port', '/dev/tty/ACM0')
		self.myDlg.addText('Frequency Selection (Approximate... depends of monitor refresh rate)')
		self.myDlg.addField('Frequency Target', choices=["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","20"], initial = "6")#3
		self.myDlg.addText('Block Duration')
		self.myDlg.addField('Duration', '64')
		self.myDlg.addText('Time before/between/after block(s)')
		self.myDlg.addField('InterBlockTime', '2')
		self.myDlg.addText('Choose Number of Blocks')
		self.myDlg.addField('NumberBlocks', '1')
		self.myDlg.show()	# show dialog and wait for OK or Cancel
		if self.myDlg.OK:	# then the user pressed OK
			self.thisInfo = self.myDlg.data
			self.options = {'participant': self.thisInfo[0], 'session': self.thisInfo[1], 'port': self.thisInfo[2], 'Frequency': self.thisInfo[3], 'Duration': self.thisInfo[4], 'InterBlockTime': self.thisInfo[5], 'NumberBlocks': self.thisInfo[6]}
		else:
			print 'User Cancelled'
		
		# Setup filename for saving
		self.fname = 'sub%s_sess%s' %(self.options['participant'], self.options['session'])
		#port name
		self.port = '%s' %self.options['port']
		#target frequency
		self.target_freq = '%s' %self.options['Frequency']
		#flash duration
		self.flash_duration= '%s' %self.options['Duration']
		#number of stimulation blocks
		self.num_blocks= '%s' %self.options['NumberBlocks']
		#time to wait between blocks
		self.wait_dur= '%s' %self.options['InterBlockTime']
	
	def file(self):
		return str(self.fname)
	
	def port_name(self):
		return str(self.port)
	
	def stim_freq(self):
		return int(self.target_freq)
	
	def stim_duration(self):
		return int(self.flash_duration)
	
	def stim_blocks(self):
		return int(self.num_blocks)
	
	def waitduration(self):
		return int(self.wait_dur)


# An SSVEP object appears to have already been constructed before being instantiated, which means setting the psychoPy window to fullscreen in the initalization interferes with the dialogue box, even if SSVEP has not been instantiated before the dialogue box.  The workaround here is to initialize SSVEP without fullscreen, do the dialogue box stuff, then set the the psychoPy window to fullscreen before starting the SSVEP.

expinfos = InputBox()
filename = expinfos.file()
print expinfos.port_name()
port_addr = expinfos.port_name()
print filename
freq = expinfos.stim_freq()
flash_dur = expinfos.stim_duration()
blocknums = expinfos.stim_blocks()
waitduration = expinfos.waitduration()

stimuli=SSVEP(frame_off=1, target_freq=freq, fname=filename, port=port_addr,
			  blockdur=flash_dur, numblocks=blocknums, waitdur=waitduration, randomlyVarySize=True, isSinusoidalStim=True, doFixationTask=True, showDiodeStimulator=True)
stimuli.mywin.fullscr = True
stimuli.mywin.winHandle.set_fullscreen(True)
stimuli.mywin.flip()
stimuli.start()
