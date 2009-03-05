from __future__ import division

import pygame
from OpenGL.GL import *

class Repr:
	"""
	Supply a standard __repr__ string for all subclasses
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
	def __init__(self, tick):
		self.tick = tick		# In milliseconds

	def __cmp__(self, other):
		tickcmp = cmp(self.tick, other.tick)
		if tickcmp == 0:
			return cmp(id(x), id(y))

class GLObject(Repr):
	def __init__(self, x, y, z, dlNum):
		# The point (x, y, z) defines the center of the object.
		self.x = x
		self.y = y
		self.z = z
		self.displayListNum = dlNum
	
	def __del__(self):
		glDeleteLists(self.dlNum, 1)
	
	def draw(self):
		glCallList(displayListNum)

	def QUADS_RECT_PRISM(self, xlen, ylen, zlen):
		glBegin(GL_QUADS)

		glPushMatrix()
		glTranslate(self.x / 2.0, self.y / 2.0, self.z / 2.0)

		# Front face
		glVertex(0.0, 0.0, 0.0)		# Bottom left
		glVertex(xlen, 0.0, 0.0)	# Bottom right
		glVertex(xlen, ylen, 0.0)	# Top right
		glVertex(0.0, ylen, 0.0)	# Top left

		# Top face
		glVertex(0.0, ylen, 0.0)	# Bottom left
		glVertex(xlen, ylen, 0.0)	# Bottom right
		glVertex(xlen, ylen, zlen)	# Top right
		glVertex(0.0, ylen, zlen)	# Top left

		# Back face
		glVertex(xlen, 0.0, zlen)	# Bottom left
		glVertex(0.0, 0.0, zlen)	# Bottom right
		glVertex(0.0, ylen, zlen)	# Top right
		glVertex(xlen, ylen, zlen)	# Top left

		# Bottom face
		glVertex(0.0, 0.0, zlen)	# Bottom left
		glVertex(xlen, 0.0, zlen)	# Bottom right
		glVertex(xlen, 0.0, 0.0)	# Top right
		glVertex(0.0, 0.0, 0.0)		# Top left

		# Right face
		glVertex(xlen, 0.0, 0.0)	# Bottom left
		glVertex(xlen, 0.0, zlen)	# Bottom right
		glVertex(xlen, ylen, zlen)	# Top right
		glVertex(xlen, ylen, 0.0)	# Top left

		# Left face
		glVertex(0.0, 0.0, zlen)	# Bottom left
		glVertex(0.0, 0.0, 0.0)		# Bottom right
		glVertex(0.0, ylen, 0.0)	# Top right
		glVertex(0.0, ylen, zlen)	# Top left

		glPopMatrix()

		glEnd()

class Note(Repr, GameEvent, GLObject):
	def __init(self, tick = 0, x = 0.0, y = 0.0, z = 0.0,
			xlen = 0.0, ylen = 0.0, zlen = 0.0):
		GameEvent.__init__(tick)

		self.xlen = xlen
		self.ylen = ylen
		self.zlen = zlen

		dlNum = createGLNote(self, x, y, z)
		GLObject.__init__(x, y, z, dlNum)

	
	def createGLDisplayList(self, x, y, z):
		dlNum = glGenLists(1)
		glNewList(dlNum, GL_COMPILE)

		self.QUADS_RECT_PRISM(self.xlen, self.ylen, self.zlen)

		glEndList()

		return dlNum
