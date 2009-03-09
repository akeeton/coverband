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
	# The point (x, y, z) defines the center of the object.
	(x, y, z) = (0.0, 0.0, 0.0)
	numDLists = 0
	displayList = 0

	def __init__(self, x = 0.0, y = 0.0, z = 0.0, numDLists = 0):
		"""
		@param glCreationFunc: This function will be used to "draw" something
			to an OpenGL display list.
		@type glCreationFunc: A function that draws OpenGL objects
		@param *funcArgs: The arguments to glCreationFunc
		"""
		if not pygame.display.get_init():
			raise pygame.error("Display must be initialized before using Opengl")

		self.x = x
		self.y = y
		self.z = z
		self.numDLists = numDLists
		self.displayList = glGenLists(self.numDLists)

	def __del__(self):
		if self.displayList != 0:
			glDeleteLists(self.displayList, self.numDLists)
	
	def createGLDisplayList(self, dListNum, glCreationFunc, *funcArgs):
		glNewList(self.displayList + dListNum, GL_COMPILE)
		glCreationFunc(self.x, self.y, self.z, *funcArgs)
		glEndList()
	
	def draw(self, dListNum):
		glCallList(self.displayList + dListNum)

class Note(Repr, GameEvent, GLObject):
	(xlen, ylen, zlen) = (0.0, 0.0, 0.0)

	def __init__(self, tick, x, y, z, xlen = 1.0, ylen = 1.0, zlen = 1.0):
		GameEvent.__init__(self, tick)
		GLObject.__init__(self, x, y, z, numDLists = 1)

		self.xlen = xlen
		self.ylen = ylen
		self.zlen = zlen

		self.createGLDisplayList(0, QUAD_RECT_PRISM, xlen, ylen, zlen)

		print(self)

	def draw(self):
		GLObject.draw(self, 0)

def BEATS_PER_SECOND(bpm):
	return bpm * 60.0

class Beat(Repr, GLObject):
	"""
	The Beat class is where most of the events (Notes) will go.
	@param bpm: BPM for this beat.
	@type bpm: positive integer
	@param eventsList: Sorted list of events local to this beat.
	@param (x, y, z): Center of the base of the beat.
	"""
	bpm = 120
	eventsList = None

	(x, y, z) = (1.0, 1.0, 0.0)
	height = 1.0
	width = W_CHART

	def __init__(self, bpm, x, y, *events):
		GLObject.__init__(self, x, y, 0.0)

		self.bpm = bpm
		self.eventsList = SortedList(events)
		self.width = W_CHART
		self.height = SPD_CHART / BEATS_PER_SECOND(bpm)


if __name__ == "__main__":
	import random
	sorted = SortedList()

	unsorted = [random.randint(0, 10) for x in range(20)]

	map(sorted.add, unsorted)

	print("unsorted: %s\nsorted: %s" % (unsorted, sorted.items))
