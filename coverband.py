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

	beats = []
	for x in range(10):
		beat = DrumsBeat(120 + 120 * x // 5,
				Note("red", 0.0),
				Note("yellow", 0.0),
				Note("orange", 1.0 / 2.0),
				Note("yellow", 1.0 / 2.0))
		beats.append(beat)

	drumChart = Chart(*beats)

	while True:
		drawChart(drumChart)

		pygame.display.flip()

		handleEvents(pygame.event.get())

	pygame.quit()

if __name__ == "__main__":
	main()
