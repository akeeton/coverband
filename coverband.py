import sys

import pygame
from OpenGL.GL import *

from data_engine import *
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

	note = Note("red", 1.0 / 4.0)
	beat = DrumsBeat(120, note)

	print(note)
	print(beat)

	while True:
		drawGLObjects(beat)

		pygame.display.flip()

		handleEvents(pygame.event.get())

	pygame.quit()

if __name__ == "__main__":
	main()
