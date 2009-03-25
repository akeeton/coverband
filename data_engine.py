from __future__ import division

import time

import pygame
from OpenGL.GL import *

from graphics import *
from globals import *

class Time():
	"""
	Manage time.
	"""
	T0 = 0

	@staticmethod
	def initT0():
		Time.T0 = int(1000.0 * time.clock())

	@staticmethod
	def ticks():
		"""
		Number of ticks since T0 was set in milliseconds.
		"""
		return Time.absTicks() - T0

	@staticmethod
	def absTicks():
		"""
		Number of ticks in milliseconds -- implementation defined.
		"""
		return int(1000.0 * time.clock())

class Repr:
	"""
	Supply a standard __repr__ string for all subclasses.
	"""
	def __repr__(self):
		return ("<Instance of %s, address %s:\n%s>" %
				(self.__class__.__name__,
					id(self),
					self.attrnames()))

	def attrnames(self):
		result = ""
		for attr in self.__dict__.keys():
			if attr.startswith("__"):
				result = result + "\tname %s = <built-in>\n" % attr
			else:
				result = result + "\tname %s = %s\n" % (attr, self.__dict__[attr])

		return result

class SortedList(Repr):
	items = []

	def __init__(self, *items):
		self.items = list(sorted(items))

	def __getitem__(self, index):
		return self.items[index]

	def __len__(self):
		return len(self.items)

	def __iter__(self):
		return self.items.__iter__()

	def add(self, item):
		"""
		Add an item to the sorted list using binary search.
		"""
		if len(self) == 0:
			self.items.append(item)
			return

		low = 0
		high = len(self.items) - 1

		if item >= self.items[high]:
			self.items.append(item)
			return
		elif item <= self.items[low]:
			self.items.insert(low, item)
			return

		while low <= high:
			mid = low + ((high - low) // 2)

			if self.items[mid] > item:
				high = mid - 1
				if high < low:
					break
			elif self.items[mid] < item:
				low = mid + 1
				if low > high:
					mid += 1
					break
			else:
				break

		self.items.insert(mid, item)
		return

	def remove(self, item):
		self.items.remove(item)

	"""
class GameEvent(Repr):
	def update(self, tick):
		raise NotImplemented()

	def getDurTicks(self):
		raise NotImplemented()
		"""

	"""
	The main base class for all game events.

	@param tick: Time of the event relative to the beginning of the beat or song.
	@type tick: integer in milliseconds
	"""
	"""
	tick = 0

	def __init__(self, tick = 0):
		self.tick = tick

	def __cmp__(self, other):
		tickcmp = cmp(self.tick, other.tick)
		if tickcmp == 0:
			return cmp(id(self), id(other))
			"""

class GLObject(Repr):
	displayList = 0
	glCreationFunc = None
	created = False

	def __init__(self, glCreationFunc):
		"""
		@param glCreationFunc: This function will be used to "draw" something
			to an OpenGL display list.
		@type glCreationFunc: A function that draws OpenGL objects
		@param *funcArgs: The arguments to glCreationFunc
		"""
		if not pygame.display.get_init():
			raise pygame.error("Display must be initialized before using OpenGL")

		self.displayList = glGenLists(1)
		self.glCreationFunc = glCreationFunc

		# createGLDisplayList must be called before draw.
		self.created = False

	def __del__(self):
		if self.displayList != 0:
			glDeleteLists(self.displayList, 1)
	
	def createGLDisplayList(self, *funcArgs):
		glNewList(self.displayList, GL_COMPILE)
		self.glCreationFunc(*funcArgs)
		glEndList()

		self.created = True
	
	def draw(self):
		if not self.created:
			raise Exception("Must call createGLDisplayList before calling draw")

		glCallList(self.displayList)

class Note(Repr, GLObject):
	"""
	@param position: A fraction representing where on the chart to place the note.
		The value is clamped to the range [0, 1]
	"""
	color = "red"
	position = 0.0
	hit = False
	miss = False
	(x, y, z) = (0.0, 0.0, 0.0)
	(xlen, ylen, zlen) = (0.0, 0.0, 0.0)

	# Set after __init__
	tick = 0

	def __init__(self, color, position):
		GLObject.__init__(self, GL_QUAD_RECT_PRISM)

		self.color = color

		if position < 0.0:
			position = 0.0
		elif position > 1.0:
			position = 1.0

		self.position = position
		self.hit = False
		self.miss = False
		# The enclosing Beat object needs to call createGLDisplayList and
		# set (x, y, z) and (xlen, ylen, zlen).
	
	def __cmp__(self, other):
		positioncmp = cmp(self.position, other.position)
		if positioncmp == 0:
			colorcmp = cmp(self.color, other.color)
			if colorcmp == 0:
				return cmp(id(self), id(other))
			else:
				return colorcmp
		else:
			return positioncmp
	
	def createGLDisplayList(self, x, y, z, xlen, ylen, zlen, *funcArgs):
		self.setCoords(x, y, z)
		self.setDimensions(xlen, ylen, zlen)

		GLObject.createGLDisplayList(self, self.x, self.y, self.z,
				self.xlen, self.ylen, self.zlen, *funcArgs)

	def draw(self):
		if not self.hit:
			GLObject.draw(self)

	def setCoords(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def setDimensions(self, xlen, ylen, zlen):
		self.xlen = xlen
		self.ylen = ylen
		self.zlen = zlen

	def setHit(self):
		self.hit = True

	def setMiss(self):
		self.createGLDisplayList(self.x, self.y, self.z,
				self.xlen, self.ylen, self.zlen, Color.colors['gray'])
		self.miss = True

	def setTick(self, tick):
		self.tick = tick

	def getTick(self):
		return self.tick

	def getPosition(self):
		return self.position

	def getHit(self):
		return self.hit

	def getMiss(self):
		return self.miss

	def getColor(self):
		return self.color

def BEATS_PER_SECOND(bpm):
	return bpm / 60.0
def MILLISECONDS_PER_BEAT(bpm):
	return 60000 // bpm

class Beat(Repr, GLObject):
	"""
	The Beat class is where all of the notes will go.
	@param bpm: BPM for this beat.
	@type bpm: positive integer
	@param notesList: Sorted list of notes local to this beat.
	"""
	bpm = 0
	durTicks = 0
	notesList = None
	width = 0.0
	height = 0.0
	wLane = 0.0

	# Set after construction.
	tick = 0

	def __init__(self, bpm, *notes):
		GLObject.__init__(self, GL_BEAT)

		numLanes = self.numLanes()

		self.bpm = bpm
		self.durTicks = MILLISECONDS_PER_BEAT(bpm)
		# TODO: SortedList needed?
		self.notesList = list(notes)	# SortedList(*notes)
		self.width = W_CHART
		self.height = SPD_CHART / BEATS_PER_SECOND(bpm)
		self.wLane = (W_CHART - (numLanes + 1) * W_LINE) / numLanes

		self.createGLDisplayList(self.width, self.height,
				self.wLane, self.numLanes())

		for note in self.notesList:	
			wLane = self.wLane
			noteLane = self.noteLane(note.color)

			if noteLane > 0:
				xNote = (noteLane - 1) * wLane + (noteLane * W_LINE)
				wNote = wLane
				hNote = H_FAT_NOTE
			else:
				xNote = 0.0
				wNote = W_CHART
				hNote = H_SKINNY_NOTE

			yNote = note.position * self.height - hNote / 2.0

			zNote = hNote / 2.0
			note.createGLDisplayList(xNote, yNote, zNote,
					wNote, hNote, hNote, Color.colors[note.color])

	def __iter__(self):
		return self.notesList.__iter__()

	def draw(self):
		GLObject.draw(self)
		for note in self.notesList:
			note.draw()

	def update(self, tick, yOffset):
		glPushMatrix()
		glTranslate(0.0, -SPD_CHART * tick / 1000.0 + yOffset, 0.0)
		self.draw()
		glPopMatrix()

	def setTick(self, tick):
		self.tick = tick
		for note in self.notesList:
			note.setTick(self.tick + note.getPosition() * self.durTicks)

	def getTick(self):
		return self.tick

	def getDurTicks(self):
		return self.durTicks

	def getHeight(self):
		return self.height

	def getNotesList(self):
		return self.notesList

	def numLanes(self):
		"""
		Abstract method.
		"""
		raise NotImplemented()
	def noteLane(self, color):
		"""
		Abstract method.
		Return the lane that the note goes in.  Lane 0 is the whole chart.
		"""
		raise NotImplemented()


class DrumsBeat(Repr, Beat):
	def __init__(self, bpm, *notes):
		Beat.__init__(self, bpm, *notes)

	def numLanes(self):
		return 4

	def noteLane(self, color):
		return { "red": 1, "yellow": 2, "blue": 3, "green": 4, "orange": 0 }[color]

class Chart(Repr):
	beats = []
	currentBeatIndex = 0
	ticksRemaining = 0
	lastTick = 0

	def __init__(self, *beats):
		self.beats = list(beats)
		self.currentBeatIndex = 0
		self.ticksRemaining = self.beats[self.currentBeatIndex].getDurTicks()
		self.lastTick = 0

		tick = 0
		for beat in self.beats:
			beat.setTick(tick)
			tick += beat.getDurTicks()

	def update(self, tick):
		# Check for missed notes.
		index = self.currentBeatIndex
		curBeat = self.beats[index]
		prevBeat = self.beats[index - 1] if index > 0 else None
		notes = curBeat.getNotesList() + prevBeat.getNotesList() if prevBeat else []

		for note in notes:
			noteTick = note.getTick()
			dt = tick - noteTick
			if not note.getHit() and not note.getMiss() and dt > MISS_THRESHOLD:
				note.setMiss()

		dt = tick - self.lastTick
		self.lastTick = tick

		# Update the current beat.
		self.ticksRemaining -= dt
		while (self.ticksRemaining <= 0 and
				self.currentBeatIndex + 1 < len(self.beats)):
			self.currentBeatIndex += 1
			self.ticksRemaining = self.beats[self.currentBeatIndex].getDurTicks() - self.ticksRemaining

		# Draw a line that represents the current position of the chart.
		yOffset = 0
		GL_QUAD_RECT_PRISM(0, 0, 0, W_CHART, W_LINE, W_LINE, Color.colors['yellow'])

		# Draw all of the beats.
		for beat in self.beats:
			beat.update(tick, yOffset)
			yOffset += beat.getHeight()
	
	def tryHit(self, tick, color):
		# Check the current and next beat for notes to hit.
		index = self.currentBeatIndex
		curBeat = self.beats[index]
		nextBeat = self.beats[index + 1] if index + 1 < len(self.beats) else None
		notes = curBeat.getNotesList() + nextBeat.getNotesList() if nextBeat else []

		for note in notes:
			if (not note.getMiss() and not note.getHit() and note.getColor() == color
					and abs(note.getTick() - tick) < HIT_THRESHOLD):
				note.setHit()
				break


if __name__ == "__main__":
	import random
	sortedList = SortedList()

	unsortedList = [random.randint(0, 10) for x in range(20)]

	map(sortedList.add, unsortedList)

	print("unsorted: %s\nsorted: %s" % (unsortedList, sortedList.items))