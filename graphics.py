from __future__ import division

import time
import math

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from globals import *

class Color:
	"""
	Easily switch between string and RGBA representations of colors.
	@cvar colors: table of colors with common identifiers
	@type colors: dict
	@ivar color: RGBA value for this color
	@type color: 4-tuple of values in the range [0.0, 1.0]

	"""
	colors = {
				"red": (1.0, 0.0, 0.0),
				"yellow": (1.0, 1.0, 0.0),
				"blue": (0.0, 0.0, 1.0),
				"green": (0.0, 1.0, 0.0),
				"orange": (1.0, 0.5, 0.0),

				"white": (1.0, 1.0, 1.0),
				"gray": (0.5, 0.5, 0.5),

				"miss": (1.0, 0.5, 0.5),
			}

	color = (0.0, 0.0, 0.0, 0.0)
	description = ""

	def __init__(self, description, alpha = 1.0, rgba = None):
		self.color = rgba if rgba else Color.colors[description] + (alpha,)
		self.description = description

	def __repr__(self):
		return "%s %s" % (self.description, self.color)
	
	def __str__(self):
		return self.description

	def __cmp__(self, other):
		return cmp(self.color, other.color)

	def rgba(self):
		return self.color

def resizeGL(width, height):
	"""
	Readjust the OpenGL perspective to scale to the window.
	@param width: width of window
	@type width: pixels
	@param height: height of window
	@type height: pixels
	"""
	if height == 0: height = 1

	glViewport(0, 0, width, height)
	aspect = width/height

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

	gluPerspective(75.0, aspect, 1.0, 200.0)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def normalize((x, y, z)):
	"""
	Normalize a vector to have length one.
	@param (x, y, z): vector to be normalized
	@type (x, y, z): 3D vector
	"""
	len = math.sqrt(x*x + y*y + z*z)
	return (x/len, y/len, z/len)

def initGL():
	"""
	Setup OpenGL-specific settings.
	"""
	#glPolygonMode(GL_FRONT, GL_LINE)
	glShadeModel(GL_SMOOTH)
	glClearColor(0.0, 0.0, 0.0, 1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)

	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	glEnable(GL_LIGHTING)

	ambientLight = (0.5, 0.5, 0.5, 1.0)
	glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambientLight)

	diffuseLight = (0.5, 0.5, 0.5, 1.0)
	specular = (1.0, 1.0, 1.0, 1.0)
	#lightPos = (0.0, 100.0, -40.0)
	#spotDir = normalize((0.0, -1.0, 0.0))
	glLight(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
	glLight(GL_LIGHT0, GL_SPECULAR, specular)
	#glLight(GL_LIGHT0, GL_POSITION, lightPos)
	#glLight(GL_LIGHT0, GL_SPOT_DIRECTION, spotDir)

	# Cut-off angle is 60 degrees.
	#glLight(GL_LIGHT0, GL_SPOT_CUTOFF, 60.0)

	glEnable(GL_LIGHT0)

	glEnable(GL_COLOR_MATERIAL)
	glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

	specref = (1.0, 1.0, 1.0, 1.0)
	glMaterial(GL_FRONT, GL_SPECULAR, specref)
	glMaterial(GL_FRONT, GL_SHININESS, 128)

	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def initScreen():
	"""
	Initialize the screen for pygame and OpenGL settings.
	"""
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

def drawChart(chart):
	"""
	Clear the scene, adjust the axes, and draw the chart.
	@param chart: A chart of notes to be drawn.
	@type chart: L{Chart}
	"""
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)

	glLoadIdentity()
	glTranslate(-W_CHART / 2.0, 20.0, -150.0)
	glRotate(-40.0, 1.0, 0.0, 0.0)

	chart.update()
	

def GL_BEAT(width, height, wLane, numLanes):
	"""
	Draw the lines that define a chart for one beat using OpenGL calls.
	"""
	white = Color('white')
	gray = Color('gray')

	# Draw the vertical lines that define the lanes.
	xLine = 0.0
	for i in range(numLanes + 1):
		GL_QUAD_RECT_PRISM((xLine, 0.0 + W_LINE / 2.0, 0.0),
			(W_LINE, height, W_LINE), white) 
		xLine += wLane + W_LINE

	# Draw the full-beat horizontal line.
	GL_QUAD_RECT_PRISM((0.0, 0.0, 0.0),
			(width, W_LINE, W_LINE), white)

	# Draw the half-beat horizontal line.
	GL_QUAD_RECT_PRISM((0.0, height / 2.0 - W_LINE / 2.0, 0.0),
			(width, W_LINE, W_LINE), gray)

def GL_QUAD_RECT_PRISM((x, y, z), (xlen, ylen, zlen), color = Color('white')):
	"""
	Make GL calls to create a rectangular prism with lower-left corner at
	the point (x, y, z).
	@type color: L{Color}
	"""
	glPushMatrix()
	glTranslate(x, y, z)
	# Uncomment for center at (x, y, z)
	# glTranslate(-xlen / 2.0, -ylen / 2.0, zlen / 2.0)

	glColor(*(color.rgba()))

	glBegin(GL_QUADS)

	# Front face
	glNormal(0.0, 0.0, 1.0)
	glVertex(0.0, 0.0, 0.0)		# Bottom left
	glVertex(xlen, 0.0, 0.0)	# Bottom right
	glVertex(xlen, ylen, 0.0)	# Top right
	glVertex(0.0, ylen, 0.0)	# Top left

	# Top face
	glNormal(0.0, 1.0, 0.0)
	glVertex(0.0, ylen, 0.0)	# Bottom left
	glVertex(xlen, ylen, 0.0)	# Bottom right
	glVertex(xlen, ylen, -zlen)	# Top right
	glVertex(0.0, ylen, -zlen)	# Top left

	# Back face
	glNormal(0.0, 0.0, -1.0)
	glVertex(xlen, 0.0, -zlen)	# Bottom left
	glVertex(0.0, 0.0, -zlen)	# Bottom right
	glVertex(0.0, ylen, -zlen)	# Top right
	glVertex(xlen, ylen, -zlen)	# Top left

	# Bottom face
	glNormal(0.0, -1.0, 0.0)
	glVertex(0.0, 0.0, -zlen)	# Bottom left
	glVertex(xlen, 0.0, -zlen)	# Bottom right
	glVertex(xlen, 0.0, 0.0)	# Top right
	glVertex(0.0, 0.0, 0.0)		# Top left

	# Right face
	glNormal(1.0, 0.0, 0.0)
	glVertex(xlen, 0.0, 0.0)	# Bottom left
	glVertex(xlen, 0.0, -zlen)	# Bottom right
	glVertex(xlen, ylen, -zlen)	# Top right
	glVertex(xlen, ylen, 0.0)	# Top left

	# Left face
	glNormal(-1.0, 0.0, 0.0)
	glVertex(0.0, 0.0, -zlen)	# Bottom left
	glVertex(0.0, 0.0, 0.0)		# Bottom right
	glVertex(0.0, ylen, 0.0)	# Top right
	glVertex(0.0, ylen, -zlen)	# Top left

	glEnd()

	glPopMatrix()
