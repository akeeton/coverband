import sys
import os

import pygame
from OpenGL.GL import *

from data_engine import Note
from graphics import initScreen, drawGL

def handleEvents(events):
	for event in events:
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			sys.exit(0)

def main():
	pygame.init()
	initScreen()

	note = Note(1000, 0.0, 0.0, -20.0, 5.0, 5.0, 5.0)

	while True:
		handleEvents(pygame.event.get())

		drawGL(note)

		glColor(1.0, 1.0, 1.0)

		pygame.display.flip()


	pygame.quit()


if __name__ == "__main__":
	main()
