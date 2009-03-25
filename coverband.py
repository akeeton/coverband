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
			drumChart.tryHit(Time.ticks(), "red")

def main():
	pygame.display.init()
	initScreen()
	Time.initT0()

	beats = []
	for x in range(20):
		beat = DrumsBeat(120,
				Note("red", 0.0),
				Note("yellow", 0.0),
				Note("orange", 1.0 / 2.0),
				Note("yellow", 1.0 / 2.0))
		beats.append(beat)

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
