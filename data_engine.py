from __future__ import division

import pygame
from OpenGL.GL import *

from graphics import *

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

class GameEvent(Repr):
	"""
	The main base class for all game events.

	@param tick: Absolute time of the event.
	@type tick: integer in milliseconds
	"""
	tick = 0

	def __init__(self, tick = 0):
		self.tick = tick

	def __cmp__(self, other):
		tickcmp = cmp(self.tick, other.tick)
		if tickcmp == 0:
			return cmp(id(x), id(y))

class GLObject(Repr):
	# The point (x, y, z) defines the center of the object.
	(x, y, z) = (0.0, 0.0, 0.0)
	dlNum = 0

	def __init__(self, x = 0.0, y = 0.0, z = 0.0,
			glCreationFunc = QUAD_RECT_PRISM, *funcArgs):
		"""
		@param glCreationFunc: This function will be used to "draw" something
			to an OpenGL display list.
		@type glCreationFunc: A function that draws OpenGL objects
		@param *funcArgs: The arguments to glCreationFunc
		"""
		if pygame.display.get_init() == False:
			raise pygame.error("Display must be initialized before using Opengl")

		self.x = x
		self.y = y
		self.z = z

		self.createGLDisplayList(glCreationFunc, *funcArgs)
	
	def __del__(self):
		if self.dlNum != 0:
			glDeleteLists(self.dlNum, 1)
	
	def createGLDisplayList(self, glCreationFunc, *funcArgs):
		self.dlNum = glGenLists(1)

		glNewList(self.dlNum, GL_COMPILE)
		glCreationFunc(self.x, self.y, self.z, *funcArgs)
		glEndList
	
	def draw(self):
		glCallList(self.dlNum)

class Note(Repr, GameEvent):
	(xlen, ylen, zlen) = (0.0, 0.0, 0.0)
	glNote = None

	def __init__(self, tick = 0, x = 0.0, y = 0.0, z = 0.0,
			xlen = 0.0, ylen = 0.0, zlen = 0.0):
		GameEvent.__init__(self, tick)

		self.xlen = xlen
		self.ylen = ylen
		self.zlen = zlen

		self.glNote = GLObject(x, y, z, QUAD_RECT_PRISM, xlen, ylen, zlen)
		print(self)

	def draw(self):
		self.glNote.draw()
