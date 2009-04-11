from __future__ import division

import time

import pygame

from graphics import *
from globals import *

class Unimplemented(Exception):
	"""
	Exception for abstract methods that must be implemented.
	"""
	def __init__(self, message = ''):
		baseMessage = 'Behavior not implemented'
		self.message = baseMessage + (': ' + message if message != '' else '')

	def __str__(self):
		return self.message

class Time():
	"""
	Manage time.
	"""
	T0 = 0

	def __init__(self):
		self.T0 = int(1000.0 * time.clock())
		print("Time T0 initialized to %s" % (self.T0))

	def ticks(self):
		"""
		@return: Number of ticks since T0.
		@rtype: milliseconds
		"""
		return int(1000.0 * time.clock()) - self.T0


class Repr:
	"""
	Supply a standard __repr__ method for all subclasses.
	"""
	def __repr__(self):
		return ("<Instance of %s, address %s:\n%s>" %
				(self.__class__.__name__,
					id(self),
					self.attrnames()))
	def __str__(self):
		return "<Instance of %s, address %s>" % (self.__class__.__name__, id(self))

	def attrnames(self):
		result = ""
		for attr in self.__dict__.keys():
			if attr.startswith("__"):
				result = result + "\tname %s = <built-in>\n" % attr
			else:
				result = result + "\tname %s = %s\n" % (attr, self.__dict__[attr])

		return result

class SortedList(Repr):
	"""
	Deprecated?
	"""
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
	"""
	Deprecated!
	The main base class for all game events.

	@param tick: Time of the event relative to the beginning of the beat or song.
	@type tick: integer in milliseconds
	"""
	def update(self, tick):
		"""
		Abstract method.
		@raise Unimplemented:
		"""
		raise Unimplemented()

	def getDurTicks(self):
		"""
		Abstract method.
		@raise Unimplemented:
		"""
		raise Unimplemented()

	tick = 0

	def __init__(self, tick = 0):
		self.tick = tick

	def __cmp__(self, other):
		tickcmp = cmp(self.tick, other.tick)
		if tickcmp == 0:
			return cmp(id(self), id(other))

class GLObject(Repr):
	"""
	Provide functionality for creating and drawing objects in OpenGL.

	@ivar displayList: Represents a series of OpenGL calls.
	@type displayList: integer
	@ivar glCreationFunc: Function used to make OpenGL calls.
	@type glCreationFunc: function
	@ivar created: True iff createGLDisplayList() was called.
	@type created: bool
	"""
	displayList = 0
	glCreationFunc = None
	created = False

	def __init__(self, glCreationFunc):
		"""
		@param glCreationFunc: This function will be used to "draw" something
			to an OpenGL display list.
		@type glCreationFunc: function
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
		"""
		Calls glCreationFunc() and stores the result as an OpenGL display list.
		@param funcArgs: Arguments to glCreationFunc()
		"""
		glNewList(self.displayList, GL_COMPILE)
		self.glCreationFunc(*funcArgs)
		glEndList()

		self.created = True
	
	def draw(self):
		"""
		Draw the GLObject.
		"""
		if not self.created:
			raise Exception("Must call createGLDisplayList before calling draw")

		glCallList(self.displayList)

class Note(Repr, GLObject):
	"""
	Base class that represents a single note.  The enclosing L{Beat}
	should set L{tick} and should call L{createGLDisplayList}
	to set L{coords} and L{dimensions}.

	@ivar color: The color of the note.
	@type color: L{Color}
	@ivar position: A fraction representing where on the chart to place the note.
	@type position: float clamped to the range [0.0, 1.0]
	@ivar hit: True iff the note has been hit.
	@type hit: bool
	@ivar miss: True iff the note was missed.
	@type miss: bool
	@ivar sustain: Duration of sustain
	@type sustain: milliseconds
	@ivar coords: XYZ coordinates relative to the enclosing beat.  Set by calling
		createGLDisplayList.
	@type coords: tuple of floats
	@ivar dimensions: Dimensions of the note.  Set by calling createGLDisplayList.
	@type dimensions: tuple of floats
	@ivar tick: Absolute time that the note occurs.  Must be set by the enclosing
		beat.
	@type tick: milliseconds
	@ivar sustainLen: Length of sustain line
	@type sustainLen: units
	"""

	color = Color('red')
	position = 0.0
	hit = False
	miss = False
	sustain = 0

	# Set after __init__
	coords = (0.0, 0.0, 0.0)
	dimensions = (0.0, 0.0, 0.0)
	tick = 0
	sustainLen = 0.0

	def __init__(self, colorDesc, position, sustain=0):
		"""
		@param colorDesc: Description of the color of the note.
		@type colorDesc: string
		@param position: L{position}
		@param sustain: L{sustain}
		@type sustain: milliseconds
		"""
		GLObject.__init__(self, GL_NOTE)

		self.color = Color(colorDesc)

		if position < 0.0:
			position = 0.0
		elif position > 1.0:
			position = 1.0

		self.position = position
		self.hit = False
		self.miss = False
		self.sustain = sustain
	
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
	
	def createGLDisplayList(self, *funcArgs):
		"""
		Create an OpenGL display list of a note at the given coordinates
		with the given dimensions using L{glCreationFunc}().

		@param coords: L{coords}
		@param dimensions: L{dimensions}
		@param sustainLen: L{sustainLen}
		@param funcArgs: Arguments passed to L{glCreationFunc}.
		"""

		GLObject.createGLDisplayList(self, self.coords, self.dimensions,
				self.sustainLen, *funcArgs)

	def draw(self):
		if not self.hit:
			GLObject.draw(self)

	def setCoords(self, coords):
		self.coords = coords

	def setDimensions(self, dimensions):
		self.dimensions = dimensions

	def setHit(self):
		self.hit = True

	def setMiss(self):
		"""
		Set L{miss} = True and change the appearance of the note.
		"""
		self.createGLDisplayList(Color('miss', alpha = 0.8)) 
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

	def getSustain(self):
		return self.sustain

def BEATS_PER_SECOND(bpm):
	return bpm / 60.0

def MILLISECONDS_PER_BEAT(bpm):
	return 60000 // bpm

class Beat(Repr, GLObject):
	"""
	Container for L{Note} objects.

	@ivar bpm: Beats per minute.
	@type bpm: positive integer
	@ivar notes: Notes local to this beat.
	@type notes: list
	@ivar durTicks: Duration of this beat in milliseconds.
	@type durTicks: milliseconds
	@ivar width: Width of the whole beat.
	@type width: units
	@ivar height: Height (length) of the whole beat.
	@type height: units
	@ivar wLane: Width of each lane.
	@type wLane: units

	@ivar tick: Absolute time that this beat begins.
	@type tick: milliseconds
	"""

	bpm = 0
	notes = None
	durTicks = 0
	width = 0.0
	height = 0.0
	wLane = 0.0

	# Set after construction.
	tick = 0

	def __init__(self, bpm, *notes):
		"""
		Initialize this beat as well as finalize the initialization of
		each L{Note} passed in.

		@param bpm: L{bpm}
		@param notes: L{Note} objects to go into this beat.
		"""
		GLObject.__init__(self, GL_BEAT)

		numLanes = self.numLanes()

		self.bpm = bpm
		self.durTicks = MILLISECONDS_PER_BEAT(bpm)
		# TODO: SortedList needed?
		self.notes = list(notes)	# SortedList(*notes)
		self.width = W_CHART
		self.height = SPD_CHART / BEATS_PER_SECOND(bpm)
		self.wLane = (W_CHART - (numLanes + 1) * W_LINE) / numLanes

		for note in self.notes:	
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
			note.setCoords((xNote, yNote, zNote))
			note.setDimensions((wNote, hNote, hNote))

	def draw(self):
		"""
		Draw the beat and the notes in it.
		"""
		GLObject.draw(self)
		for note in self.notes:
			note.draw()
	
	def createGLDisplayList(self, *funcArgs):
		GLObject.createGLDisplayList(self, self.width, self.height, self.wLane,
				self.numLanes(), *funcArgs)

		for note in self.notes:
			note.createGLDisplayList(note.getColor())

	def update(self, tick, yOffset):
		glPushMatrix()
		glTranslate(0.0, -SPD_CHART * tick / 1000.0 + yOffset, 0.0)
		self.draw()
		glPopMatrix()

	def setTick(self, tick):
		"""
		Set the tick for this beat and the tick for each note in this beat.

		@param tick: L{tick}
		"""
		self.tick = tick
		for note in self.notes:
			note.setTick(self.tick + note.getPosition() * self.durTicks)

	def getTick(self):
		return self.tick

	def getDurTicks(self):
		return self.durTicks

	def getHeight(self):
		return self.height

	def getNotes(self):
		return self.notes

	def numLanes(self):
		"""
		Abstract method.
		@raise Unimplemented:
		"""
		raise Unimplemented()

	def noteLane(self, color):
		"""
		Abstract method.
		Return the lane that the note goes in.  Lane 0 is the whole chart.

		@raise Unimplemented:
		"""
		raise Unimplemented()


class DrumsBeat(Repr, Beat):
	def __init__(self, bpm, *notes):
		Beat.__init__(self, bpm, *notes)

	def numLanes(self):
		return 4

	def noteLane(self, color):
		return { "red": 1, "yellow": 2,
				"blue": 3, "green": 4,
				"orange": 0 }[str(color)]

class GuitarBeat(Repr, Beat):
	def __init__(self, bpm, *notes):
		Beat.__init__(self, bpm, *notes)

	def numLanes(self):
		return 5

	def noteLane(self, color):
		return { 'green': 1, 'red': 2,
				'yellow': 3, 'blue': 4,
				'orange': 5 }[str(color)]

class Instrument(Repr):
	"""
	Base class that represents how different Instruments behave and sound.

	@cvar identifier: A string identifying the instrument, for example "drums"
	@type identifier: string
	
	@cvar keyMap: A mapping from an input to notes.
	@type keyMap: dictionary
	"""

	identifier = ""
	keyMap = {}
	whiffSounds = [None]

	def canHitNote(self, note, *keys):
		"""
		Return true if the note can be hit with this sequence of keys.
		"""
		raise Unimplemented()

	def keyToNote(self, key):
		return keyMap[key]

	def getKeys(self):
		return keyMap.keys

class Chart(Repr):
	"""
	@type instrument: L{Instrument}
	"""
	beats = []
	currentBeatIndex = 0
	ticksRemaining = 0
	lastTick = 0
	instrument = None

	time = None

	def __init__(self, instrument, *beats):
		self.beats = list(beats)
		self.currentBeatIndex = 0
		self.ticksRemaining = self.beats[self.currentBeatIndex].getDurTicks()
		self.lastTick = 0
		self.instrument = instrument

		self.time = Time()

		sustainNotes = []
		tick = self.time.ticks()
		for beat in self.beats:
			beat.setTick(tick)
			tick += beat.getDurTicks()

			# Purge the old sustain notes that have been completed.
			sustainNotes = filter(lambda (note, sustainLeft): sustainLeft > 0,
					sustainNotes)
			# Add all of the sustain notes in this beat with their sustains.
			sustainNotes += [(note, note.getSustain()) for note in beat.getNotes()
					if note.getSustain() > 0]

			def updateSustain((note, sustainLeft)):
				if sustainLeft > beat.getDurTicks():
					sustain = beat.getDurTicks()
					sustainLeft -= beat.getDurTicks()
				else:
					sustain = sustainLeft
					sustainLeft = 0

				note.sustainLen += (beat.getHeight() * sustain) / beat.getDurTicks()
				return (note, sustainLeft)

			# Update the amount of sustain remaining for each note.
			sustainNotes = map(updateSustain, sustainNotes)

		# Create the draw lists outside of the previous loop since not all of the
		# information is correct within the loop.
		for beat in self.beats:
			beat.createGLDisplayList()

	def getNotesInFocus(self):
		"""
		Return notes from the current, previous, and next beats.
		"""
		# Check the current and next beat for notes.
		index = self.currentBeatIndex
		beats = [self.beats[index]]
		if index > 0:
			beats.insert(0, self.beats[index - 1])
		if index + 1 < len(self.beats):
			beats.append(self.beats[index + 1])

		# Combine the notes from each beat into one list of notes.
		notes = reduce(lambda acc, beat: acc + beat.getNotes(), beats, [])
		return notes

	def update(self):
		tick = self.time.ticks()

		# Check for missed notes.
		notes = self.getNotesInFocus()
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
		GL_QUAD_RECT_PRISM((0, 0, 0), (W_CHART, W_LINE, W_LINE), Color('yellow'))

		# Update (draw) all of the beats.
		for beat in self.beats:
			beat.update(tick, yOffset)
			yOffset += beat.getHeight()
	
	def handleInput(self, *keys):
		tick = self.time.ticks()

		notes = self.getNotesInFocus()
		for note in notes:
			if (not note.getMiss() and not note.getHit()
					and abs(note.getTick() - tick) < HIT_THRESHOLD):
				if self.instrument.canHitNote(note, *keys):
					note.setHit()
					return

class Drums(Instrument):
	identifier = "drums"
	keyMap = {pygame.K_a: 'red', pygame.K_s: 'yellow', pygame.K_d: 'blue',
			pygame.K_f: 'green', pygame.K_SPACE: 'orange'}

	def __init__(self):
		pass

	def canHitNote(self, note, *keys):
		for key in keys:
			if str(note.getColor()) == self.keyMap[key]:
				return True

		return False

class DrumsChart(Chart, Drums):
	def __init__(self, *beats):
		Chart.__init__(self, *beats)
		Drums.__init__(self)

if __name__ == "__main__":
	import random
	sortedList = SortedList()

	unsortedList = [random.randint(0, 10) for x in range(20)]

	map(sortedList.add, unsortedList)

	print("unsorted: %s\nsorted: %s" % (unsortedList, sortedList.items))
