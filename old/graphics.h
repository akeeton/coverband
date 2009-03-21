/********************************
 * graphics.h
 *
 * Last Modified:
 * 2 March 2009
 * by Andrew Keeton
********************************/

#ifndef __GRAPHICS_H__
#define __GRAPHICS_H__

#include "autoinc.h"

#define W_LINE 0.03f
#define W_CHART	66.0f * W_LINE
#define DRUMS_ORANGE_HEIGHT	2 * W_LINE

#define SPD_CHART 30.0f	// units per second

int initScreen(SDL_Surface **screen);
void drawChart(chart_t *p_chart);
void resizeGL(size_t width, size_t height);

int glFromChart(chart_t *p_chart);
int glNotesFromChartDrums(chart_t *p_chart);
int glNotesFromChartGuitar(chart_t *p_chart);

// Bass and guitar are the same for now.
#define glNotesFromChartBass glNotesFromChartGuitar
int glNotesFromChartBass(chart_t *p_chart);

int glSkeletonFromChart(chart_t *p_chart, size_t numLanes);

#endif	// __GRAPHICS_H__
