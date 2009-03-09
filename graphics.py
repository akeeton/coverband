from __future__ import division

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

def resizeGL(width, height):
	if height == 0: height = 1

	glViewport(0, 0, width, height)
	aspect = width/height

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

	gluPerspective(75.0, aspect, 1.0, 200.0)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def initGL():
	#glPolygonMode(GL_FRONT, GL_LINE)
	glShadeModel(GL_SMOOTH)
	glClearColor(0.0, 0.0, 0.0, 1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def drawGLObjects(*drawables):
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)

	for drawable in drawables:
		drawable.draw()
	
def initScreen():
	if not pygame.display.mode_ok((640, 480), pygame.OPENGL):
		raise pygame.error("Could not set opengl")
	elif not pygame.display.mode_ok((640, 480), pygame.DOUBLEBUF):
		raise pygame.error("Could not set opengl")
	elif not pygame.display.mode_ok((640, 480), pygame.HWSURFACE):
		raise pygame.error("Could not set opengl")

	screen = pygame.display.set_mode((640, 480),
			pygame.OPENGL | pygame.DOUBLEBUF)
	pygame.display.set_caption("Cover Band")

	initGL()
	resizeGL(screen.get_width(), screen.get_height())

def QUAD_RECT_PRISM(x, y, z, xlen, ylen, zlen):
	"""
	A function that draws a rectangular prism with center at the point (x, y, z)
	using quad surfaces.
	"""

	glPushMatrix()
	glTranslate(x, y, z)
	glTranslate(-xlen / 2.0, -ylen / 2.0, zlen / 2.0)

	glBegin(GL_QUADS)

	# Front face
	glVertex(0.0, 0.0, 0.0)		# Bottom left
	glVertex(xlen, 0.0, 0.0)	# Bottom right
	glVertex(xlen, ylen, 0.0)	# Top right
	glVertex(0.0, ylen, 0.0)	# Top left

	# Top face
	glVertex(0.0, ylen, 0.0)	# Bottom left
	glVertex(xlen, ylen, 0.0)	# Bottom right
	glVertex(xlen, ylen, -zlen)	# Top right
	glVertex(0.0, ylen, -zlen)	# Top left

	# Back face
	glVertex(xlen, 0.0, -zlen)	# Bottom left
	glVertex(0.0, 0.0, -zlen)	# Bottom right
	glVertex(0.0, ylen, -zlen)	# Top right
	glVertex(xlen, ylen, -zlen)	# Top left

	# Bottom face
	glVertex(0.0, 0.0, -zlen)	# Bottom left
	glVertex(xlen, 0.0, -zlen)	# Bottom right
	glVertex(xlen, 0.0, 0.0)	# Top right
	glVertex(0.0, 0.0, 0.0)		# Top left

	# Right face
	glVertex(xlen, 0.0, 0.0)	# Bottom left
	glVertex(xlen, 0.0, -zlen)	# Bottom right
	glVertex(xlen, ylen, -zlen)	# Top right
	glVertex(xlen, ylen, 0.0)	# Top left

	# Left face
	glVertex(0.0, 0.0, -zlen)	# Bottom left
	glVertex(0.0, 0.0, 0.0)		# Bottom right
	glVertex(0.0, ylen, 0.0)	# Top right
	glVertex(0.0, ylen, -zlen)	# Top left

	glEnd()

	glPopMatrix()
