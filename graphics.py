from __future__ import division

import pygame
from OpenGL.GL import *

def resizeGL(width, height):
	h = height / width
	 
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glFrustum(-1.0, 1.0, -h, h, 10.0, 80.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0.0, 0.0, -40.0)

def initGL():
	glShadeModel(GL_FLAT)
	glPolygonMode(GL_FRONT, GL_LINE)
	glClearColor(0.5, 0.5, 0.0, 0.0)
	glClearDepth(1.0)
	#glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)
	#glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	#glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def initScreen():
	pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
	screen = pygame.display.set_mode((640, 480),
			pygame.OPENGL | pygame.DOUBLEBUF)
	pygame.display.set_caption("Cover Band")

	initGL()
	resizeGL(screen.get_width(), screen.get_height())

def drawGLObjects(*drawables):
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glTranslatef(0.0, 0.0, -40.0)

	for drawable in drawables:
		drawable.draw()
	

def QUAD_RECT_PRISM(x, y, z, xlen, ylen, zlen):
	"""
	A function that draws a rectangular prism with center at the point (x, y, z)
	using quad surfaces.
	"""
	glBegin(GL_QUADS)

	glPushMatrix()
	glTranslate(x / 2.0, y / 2.0, z / 2.0)

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
