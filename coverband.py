import sys
import copy

import pygame
from OpenGL.GL import *

from data_engine import *
from graphics import initScreen, drawChart

paused = False

def handleEvents(events):
	for event in events:
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
			global paused
			paused = not paused
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
			drumChart.tryHit(Color('red'))

def main():
	pygame.display.init()
	initScreen()

	beats = []
	for x in range(10):
		beat1 = DrumsBeat(120,
				Note("red", 0.0),
				Note("yellow", 0.0),
				Note("orange", 0.0),
				Note("yellow", 1.0 / 2.0))
		beat2 = DrumsBeat(120,
				Note("orange", 0.0),
				Note("yellow", 0.0),
				Note("yellow", 1.0 / 2.0))

		beats.append(beat1)
		beats.append(beat2)

	global drumChart
	drumChart = Chart(*beats)

	while True:
		global paused
		if not paused:
			drawChart(drumChart)

		pygame.display.flip()

		handleEvents(pygame.event.get())

	pygame.quit()

if __name__ == "__main__":
	main()
