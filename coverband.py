import sys
import copy

import pygame
from OpenGL.GL import *

from data_engine import *
from graphics import initScreen, drawChart

def handleEvents(events):
	for event in events:
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			sys.exit(0)

def main():
	pygame.display.init()
	initScreen()

	beat = DrumsBeat(120, Note("red", 1.0 / 4.0), Note("green", 1.0 / 2.0),
			Note("orange", 3.0 / 4.0))
	beats = [beat]

	"""
	for x in range(1):
		beats.append(copy.deepcopy(beat))
	"""
	drumChart = Chart(*beats)

	T0 = pygame.time.get_ticks()

	while True:
		drawChart(drumChart)

		pygame.display.flip()

		handleEvents(pygame.event.get())

	pygame.quit()

if __name__ == "__main__":
	main()
