import sys
import os

import pygame
from OpenGL.GL import *

from data_engine import Note
from graphics import initScreen, drawGLObjects

def handleEvents(events):
	for event in events:
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			sys.exit(0)

def main():
	pygame.display.init()
	initScreen()

	note = Note(1000, 0.0, 0.0, -20.0, 5.0, 5.0, 5.0)

	zpos = 80.0
	while True:
		print("zpos = %s" % (zpos))

		glColor(1.0, 1.0, 1.0)
		drawGLObjects(note)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glMatrixMode(GL_MODELVIEW)

		glBegin(GL_TRIANGLES)
		glVertex(0.0, 3.0, zpos)
		glVertex(-3.0, -3.0, zpos)
		glVertex(3.0, -3.0, zpos)
		glEnd

		pygame.display.flip()

		handleEvents(pygame.event.get())

		zpos -= 0.5


	pygame.quit()


if __name__ == "__main__":
	main()
