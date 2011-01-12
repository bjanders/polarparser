#!/usr/bin/python

# Copyright (C) Bjorn Andersson <bjorn@iki.fi>

import re
import sys
from pprint import pprint


epire = re.compile('Exe(\d+)PhaseInfo(\d+)')
eire = re.compile('ExerciseInfo(\d+)')

class Section(object):
	numrowtext = None
	def __init__(self, name):
		self.name = name
		self.version = None
		self.numrows = []
		self.textrows = []

	def parseheader(self, line):
		data = line.split()
		(self.version,
		 self.inforowcount,
		 self.numrowcount,
		 self.colcount,
		 self.textrowcount,
		 self.maxtextchars) = map(int, data)		 

	def _parsedata(self, data):
		x = self.inforowcount
		for i in xrange(x, self.numrowcount + x):
			self.numrows.append(map(int, data[i].split()))
		x = x + self.numrowcount
		for i in xrange(x, len(data) - x):
			self.textrows.append(data[i])
			
	def parsedata(self, data):
		self.parseheader(data[0])
		self._parsedata(data)

	def printdata(self):
		if self.numrowtext == None:
			pprint(self.numrows)
			return
		i = 0
		for row in self.numrowtext:
			j = 0
			for col in row:
				if col is not None:
					print "%s: %d" % (col, self.numrows[i][j])
				j += 1
			i += 1
				
		

def sectionfactory(name):
	if name == 'DayInfo':
		return DayInfo(name)
	elif eire.match(name):
		return ExerciseInfo(name)
	elif epire.match(name):
		return ExecPhase(name)
	else:
		return Section(name)

class DayInfo(Section):
	numrowtext = (
		('Date', 'Number of exercises', 'Resting HR', 'Orthostatic test HR', 'Weight', 'Sleeping hours'),
		('Sleeping pattern', None, None, None, None, None),
		('Day info', None, 'HRmax-p', 'Overtraining test result', 'User item 1', 'User item 2'),
		('User item 3', None, 'OwnIndex', 'Weather', 'Temperature', None),
		(None, None, 'Number of exercise plans', None, None, None))
	
class ExerciseInfo(Section):
	numrowtext = (
		(None, 'No report', 'Not edited manually', 'Distance from HR monitor', 'Start time', 'Total time'),
		('Sport', 'Distance (depricated)', 'Feeling', 'Recovery', None, 'Energy consumption'),
		('Distance', None, None, None, 'Odometer', 'Ascent'),
		('Total exertion', 'Power avg with zero values', 'Vert speed up max', 'Vert speed down max', None, 'Vert speed up avg'),
		('Zone 0 time', 'Zone 1 time', 'Zone 3 time', 'Zone 4 time', 'Zone 5 time'),
		('Zone 6 time', 'Zone 7 time', 'Zone 8 time', 'Zone 9 time', 'Sport specific unit', None),
		('Zone 0 exertion', 'Zone 1 exertion', 'Zone 2 exertion', 'Zone 3 exertion', 'Zone 4 exertion', 'Zone 5 exertion'),
		('Zone 6 exertion', 'Zone 7 exertion', 'Zone 8 exertion', 'Zone 9 exertion', 'Recording rate', 'Original ascent'),
		('HR average', 'HR max', 'Speed average', 'Speed max', 'Cadence average', 'Cadence max'),
		('Altidute average', 'Altitude max', 'Power average', 'Power max', 'Pedaling index average', 'Pedaling index max'),
		(None, None, None, None, 'Slope count', 'Descent'),
		('Average calory rate', 'Vert speed down average', 'Beat sum', 'L/R balance average', 'L/R balance max', 'Original energy consumption'),
		('Power zone 0 time', 'Power zone 1 time', 'Power zone 2 time', 'Power zone 3 time', 'Power zone 4 time', 'Power zone 5 time'),
		('Power zone 6 time', 'Power zone 7 time', 'Power zone 8 time', 'Power zone 9 time', None, None),
		('VAM', 'Excerice ranking', 'Memory full', 'Running index', None, 'Incline max',),
		('Stride length average', 'Decline max', 'Cycling efficiency', 'Footpod calibration factor', 'Wheel size', None),
		('Excerise type', None, None, None, None, None))
		
		
	def __init__(self, name):
		match = eire.match(name)
		if not match:
			raise Exception("ExcericiseInfo name is not correct: %s" % name)
		self.exenum = match.group(1)
		Section.__init__(self, name)

class ExecPhase(Section):
	def __init__(self, name):
		match = epire.match(name)
		if not match:
			raise Exception("ExePhaseInfo name is not correct: %s" % name)
		self.exenum = match.group(1)
		self.phasenum = match.group(2)
		Section.__init__(self, name)
		
	def parsedata(self, data):
		self.inforowcount = 0
		self.numrowcount = 23
		self._parsedata(data)


class DiaryData(object):
	dayinfo = None
	exericesplans = []
	exercises = []

class WeeklyData(object):
	pass

def parsefile(f):
	r = re.compile("\[(\w+)\]")
	sects = []
	sect = None
	for line in f:
		line = line.strip()
		match = r.match(line)
		if match:
			if sect:
				sect.parsedata(data)
				sects.append(sect)
				sect.printdata()
				print
			data = []
			sect = sectionfactory(match.group(1))
			print sect.name
		else:
			data.append(line)
	if sect:
		sect.parsedata(data)
		sects.append(sect)
		sect.printdata()

if __name__ == '__main__':
	f = open(sys.argv[1])
	parsefile(f)
	f.close()
