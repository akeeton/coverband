import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

width = 640
height = 480

pygame.init()

pygame.display.set_mode((width, height), pygame.OPENGL|pygame.DOUBLEBUF)

glClearColor(1.0, 1.0, 1.0, 1.0)
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
#gluOrtho2D(0, width, 0, height)
aspect = width/height
gluPerspective(75.0, aspect, 1.0, 200.0)
glMatrixMode(GL_MODELVIEW)

while True:
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	pygame.display.flip()
