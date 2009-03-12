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

class Color:
	red = (1.0, 0.0, 0.0)
	white = (1.0, 1.0, 1.0)
	gray = (0.5, 0.5, 0.5)

class GameEvent(Repr):
	"""
	The main base class for all game events.

	@param tick: Time of the event relative to the beginning of the beat or song.
	@type tick: integer in milliseconds
	"""
	tick = 0

	def __init__(self, tick = 0):
		self.tick = tick

	def __cmp__(self, other):
		tickcmp = cmp(self.tick, other.tick)
		if tickcmp == 0:
			return cmp(id(self), id(other))

class GLObject(Repr):
	numDLists = 0
	displayList = 0
	glCreationFunc = None
	created = False

	def __init__(self, glCreationFunc, numDLists):
		"""
		@param glCreationFunc: This function will be used to "draw" something
			to an OpenGL display list.
		@type glCreationFunc: A function that draws OpenGL objects
		@param *funcArgs: The arguments to glCreationFunc
		"""
		if not pygame.display.get_init():
			raise pygame.error("Display must be initialized before using OpenGL")

		self.numDLists = numDLists
		self.displayList = glGenLists(self.numDLists)
		self.glCreationFunc = glCreationFunc

		# createGLDisplayList must be called before draw.
		self.created = False

	def __del__(self):
		if self.displayList != 0:
			glDeleteLists(self.displayList, self.numDLists)
	
	def createGLDisplayList(self, dListNum, *funcArgs):
		glNewList(self.displayList + dListNum, GL_COMPILE)
		self.glCreationFunc(*funcArgs)
		glEndList()

		self.created = True
	
	def draw(self):
		if not self.created:
			raise Exception("Must call createGLDisplayList before calling draw")

		for i in range(self.numDLists):
			glCallList(self.displayList + i)

class Note(Repr, GameEvent, GLObject):
	"""
	@param position: A fraction representing where on the chart to place the note.
		For example, a note with position 3/8 would be the third eight-note.
	"""
	color = "notacolor"
	position = 0.0

	def __init__(self, tick, color, position):
		GameEvent.__init__(self, tick)
		GLObject.__init__(self, GL_QUAD_RECT_PRISM, numDLists = 1)

		self.color = color
		self.position = position
		# The enclosing Beat object needs to call createGLDisplayList.

def BEATS_PER_SECOND(bpm):
	return bpm * 60.0

class Beat(Repr, GLObject):
	"""
	The Beat class is all of the notes will go.
	@param bpm: BPM for this beat.
	@type bpm: positive integer
	@param notesList: Sorted list of notes local to this beat.
	"""
	bpm = 0
	notesList = None
	width = 0.0
	height = 0.0
	wLane = 0.0

	def __init__(self, bpm, *notes):
		GLObject.__init__(self, self.GL_BEAT, numDLists = 1)

		self.bpm = bpm
		self.notesList = SortedList(notes)
		self.width = W_CHART
		self.height = SPD_CHART / BEATS_PER_SECOND(bpm)
		numLanes = self.numLanes()
		self.wLane = (W_CHART - (numLanes + 1) * W_LINE) / numLanes

		self.createGLDisplayList(1)

		for note in notes:	
			wLane = self.wLane
			# Multiply by 4 since each beat is the beginning of a quarter note.
			yNote = 4.0 * note.position * self.height
			noteLane = self.noteLane(note.color)

			if noteLane() > 0:
				xNote = (noteLane - 1) * wLane + (noteLane * W_LINE)
				wNote = wLane
				hNote = H_FAT_NOTE
			else:
				xNote = 0.0
				wNote = W_CHART
				hNote = H_SKINNY_NOTE

			note.createGLDisplayList(1, xNote, yNote, 0.0, wNote, hNote, hNote)

	def numLanes(self):
		"""
		Abstract class.
		"""
		pass
	def noteLane(self, color):
		"""
		Abstract class.
		"""
		pass

	def GL_BEAT(self):
		numLanes = self.numLanes()

		# Draw the vertical lines that define the lanes.
		glColor(Color.white)
		for i in range(numLanes + 1):
			GL_QUAD_RECT_PRISM(i * self.wLane, 0.0, 0.0,
				W_LINE, self.height, W_LINE)

		# Draw the full-beat horizontal line.
		GL_QUAD_RECT_PRISM(0.0, 0.0, 0.0, self.width, W_LINE, W_LINE)

		# Draw the half-beat horizontal line.
		glColor(Color.gray)
		GL_QUAD_RECT_PRISM(0.0, self.height / 2.0, 0.0,
			self.width, W_LINE, W_LINE)

class DrumsBeat(Beat):
	def __init__(self, bpm, *notes):
		Beat.__init__(self, bpm, *notes)

	def numLanes(self):
		return 4

	def noteLane(self, color):
		"""
		Return the lane that the note goes in.  Lane 0 is the whole chart.
		"""

		return { "red": 1, "yellow": 2, "blue": 3, "green": 4, "orange": 0 }[color]
if __name__ == "__main__":
	import random
	sortedList = SortedList()

	unsortedList = [random.randint(0, 10) for x in range(20)]

	map(sortedList.add, unsortedList)

	print("unsorted: %s\nsorted: %s" % (unsortedList, sortedList.items))
