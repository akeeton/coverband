from __future__ import division

import pygame
from OpenGL.GL import *

from graphics import *
from globals import *

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

class GameEvent(Repr):
	def update(self, tick):
		"""
		Abstract method.
		"""
		raise NotImplemented()

	def getDurTicks(self):
		"""
		Abstract method.
		"""
		raise NotImplemented()

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
		For example, a note with position 3/8 would be the third eight-note.
	"""
	color = "notacolor"
	position = 0.0

	def __init__(self, color, position):
		GLObject.__init__(self, GL_QUAD_RECT_PRISM)

		self.color = color
		self.position = position
		# The enclosing Beat object needs to call createGLDisplayList.
	
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

def BEATS_PER_SECOND(bpm):
	return bpm / 60.0
def MILLISECONDS_PER_BEAT(bpm):
	return 60000 // bpm

class Beat(Repr, GLObject, GameEvent):
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

	def __init__(self, bpm, *notes):
		GLObject.__init__(self, GL_BEAT)

		numLanes = self.numLanes()

		self.bpm = bpm
		self.durTicks = MILLISECONDS_PER_BEAT(bpm)
		self.notesList = SortedList(*notes)
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

			# Multiply by 4 since each beat is the beginning of a quarter note.
			#yNote = 4.0 * note.position * self.height
			yNote = note.position * self.height - hNote / 2.0

			note.createGLDisplayList(xNote, yNote, hNote / 2.0, wNote, hNote, hNote,
					Color.colors[note.color])

	def draw(self):
		GLObject.draw(self)
		for note in self.notesList:
			note.draw()

	def update(self, tick):
		glPushMatrix()
		glTranslate(0.0, -SPD_CHART * 1000.0 * tick, 0.0)

		self.draw()

		glPopMatrix()

	def getDurTicks(self):
		return self.durTicks

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
	events = []

	def __init__(self, *events):
		self.events = list(events)

	def update(self, tick):
		for event in self.events:
			event.update(tick)
			tick += event.getDurTicks()

if __name__ == "__main__":
	import random
	sortedList = SortedList()

	unsortedList = [random.randint(0, 10) for x in range(20)]

	map(sortedList.add, unsortedList)

	print("unsorted: %s\nsorted: %s" % (unsortedList, sortedList.items))
