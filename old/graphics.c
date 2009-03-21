/************************************************************************
 * graphics.c
 *
 * Last Modified:
 * 2 March 2009
 * by Andrew Keeton
 * 
 * Purpose: Provide functions for creating and drawing OpenGL graphics.
 *
 * Includes code adapted from NeHe's OpenGL tutorials at nehe.gamedev.net
************************************************************************/

#include "autoinc.h"

/* RECT_PRISM - create quads that define a rectangular prism with
 * the point (x, y, z) the closest, lower-left corner. */
static inline void RECT_PRISM(GLfloat x, GLfloat y, GLfloat z,
		GLfloat xlen, GLfloat ylen, GLfloat zlen) {

	glBegin(GL_QUADS);

	/* Front face */
	glVertex3f(x, y, z);						/* Bottom left */
	glVertex3f(x + xlen, y, z);					/* Bottom right */
	glVertex3f(x + xlen, y + ylen, z);			/* Top right */	
	glVertex3f(x, y + ylen, z);					/* Top left */

	/* Top face */
	glVertex3f(x, y + ylen, z);					/* Bottom left */
	glVertex3f(x + xlen, y + ylen, z);			/* Bottom right */
	glVertex3f(x + xlen, y + ylen, z + zlen);	/* Top right */
	glVertex3f(x, y + ylen, z + zlen);			/* Top left */

	/* Back face */	
	glVertex3f(x + xlen, y, z + zlen);			/* Bottom left */
	glVertex3f(x, y, z + zlen);					/* Bottom right */
	glVertex3f(x, y + ylen, z + zlen);			/* Top right */
	glVertex3f(x + xlen, y + ylen, z + zlen);	/* Top left */

	/* Bottom face */
	glVertex3f(x, y, z + zlen);					/* Bottom left */
	glVertex3f(x + xlen, y, z + zlen);			/* Bottom right */
	glVertex3f(x + xlen, y, z);					/* Top right */
	glVertex3f(x, y, z);						/* Top left */

	/* Left face */
	glVertex3f(x, y, z + zlen);					/* Bottom left */
	glVertex3f(x, y, z);						/* Bottom right */
	glVertex3f(x, y + ylen, z);					/* Top right */
	glVertex3f(x, y + ylen, z + zlen);			/* Top left */

	/* Right face */
	glVertex3f(x + xlen, y, z);					/* Bottom left */
	glVertex3f(x + xlen, y, z + zlen);			/* Bottom right */
	glVertex3f(x + xlen, y + ylen, z + zlen);	/* Top right */
	glVertex3f(x + xlen, y + ylen, z);			/* Top left */

	glEnd();
}

/* RECT_PRISM_CENTER - construct an OpenGL rectangular prism with center
 * at the point (x, y, z). */
static inline void RECT_PRISM_CENTER(GLfloat x, GLfloat y, GLfloat z,
		GLfloat xlen, GLfloat ylen, GLfloat zlen) {
	glPushMatrix();
	glTranslatef(-xlen / 2.0f, -ylen / 2.0f, -zlen / 2.0f);

	RECT_PRISM(x, y, z, xlen, ylen, zlen);

	glPopMatrix();
}

/* BPS - Beats per second */
static inline double BPS(unsigned short bpm) { return (double)bpm / 60.0f; }
static inline size_t MILLISECONDS_PER_BEAT(unsigned short bpm) { 
	return (size_t)(60000.0f / (double)bpm);
}

static inline double HEIGHT_PER_BEAT(unsigned short bpm) { 
	// (speed in units/second) / (beats/second)
	return SPD_CHART / BPS(bpm);
}

/* BEATS_PER_SONG - returns a rounded-up number of beats in a song. */
static inline size_t BEATS_PER_SONG(chart_t *p_chart) {
	// beats/second * time in seconds
	return (size_t)(BPS(p_chart->bpm) * (double)p_chart->duration) + 1;
}

/* general OpenGL initialization function */
static void initGL() {
    /* Enable smooth shading */
    glShadeModel(GL_SMOOTH);

	//glPolygonMode(GL_FRONT, GL_LINE);
    /* Set the background black */
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f);

    /* Depth buffer setup */
    glClearDepth(1.0f);

	glEnable(GL_CULL_FACE);

    /* Enables Depth Testing */
    glEnable(GL_DEPTH_TEST);

    /* The Type Of Depth Test To Do */
    glDepthFunc(GL_LEQUAL);

    /* Really Nice Perspective Calculations */
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
	glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST);

}

/* initScreen - initialize SDL and GL for drawing to the screen and
 * passback a pointer to an SDL screen. */
int initScreen(SDL_Surface **screen) {
	/*
	if (SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8) < 0)
		PANIC(SDL, "SDL_GL_SetAttribute");
	if (SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8) < 0)
		PANIC(SDL, "SDL_GL_SetAttribute");
	if (SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8) < 0)
		PANIC(SDL, "SDL_GL_SetAttribute");
	if (SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24) < 0)
		PANIC(SDL, "SDL_GL_SetAttribute");
	if (SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1) < 0)
		PANIC(SDL, "SDL_GL_SetAttribute");
		*/

	*screen = SDL_SetVideoMode(800, 600, 0, SDL_OPENGL|SDL_RESIZABLE);
	if (!*screen) PANIC(SDL, "SDL_SetVideoMode",
			"Unable to initialize 800x600 video mode");

	SDL_WM_SetCaption("Cover Band", "coverband");

	initGL();

	resizeGL((size_t)(*screen)->w, (size_t)(*screen)->h);

	return 0;

panic_SDL:
	return SDL;
}

static Uint32 T0 = 0;
static double Scroll = 0;

void drawChart(chart_t *p_chart) {
	size_t i = 0;
	Uint32 t;

	// Update the screen at 30fps.
	t = SDL_GetTicks();
	if (t - T0 >= (1000.0f / 30.0f)) {
		T0 = t;
		Scroll += SPD_CHART / 30.0f;
	}

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glLoadIdentity();

	glTranslatef(-W_CHART / 2.0f, -W_CHART * 0.5f, -10.0f * W_CHART);
	glRotatef(-85.0f, 1.0f, 0.0f, 0.0f);
	glTranslatef(0.0f, (GLfloat)-Scroll, 0.0f);

	glCallList(p_chart->glChart.dlSkel);
	for (i = 0; i < p_chart->events[CMD_NOTE].num; i++)
		glCallList(p_chart->glChart.dlNotes + i);

}

/* resizeGL - new window size or exposure */
void resizeGL(size_t width, size_t height) {
	double h = (double)height / (double)width;

	glViewport(0, 0, (GLint)width, (GLint)height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glFrustum(-1.0, 1.0, -h, h, 10.0, 80.0);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	glTranslatef(0.0, 0.0, -40.0);
}

/* glFromChart - create an OpenGL representation of the chart and store it in
 * p_chart->glChart */
int glFromChart(chart_t *p_chart) {
	p_chart->glChart.dlSkel = 0;
	p_chart->glChart.dlNotes = 0;

	if (glSkeletonFromChart(p_chart, NUM_LANES[p_chart->instrument]) < 0)
		PANIC(APP, "glSkeletonFromChart", "Unable to create skeleton chart");

	switch(p_chart->instrument) {
		case MASTER:
			break;
		case GUITAR:
			return glNotesFromChartGuitar(p_chart);
			break;
		case BASS:
			return glNotesFromChartBass(p_chart);
			break;
		case DRUMS:
			return glNotesFromChartDrums(p_chart);
			break;
		default:
			break;
	}

	return 0;

panic_APP:
	// TODO: "Free" OpenGL display lists?
	return ERR;
}


/* !!!!!!!!!! README !!!!!!!!!!
 *
 * These macros are very important!  They begin and end the main construction loop
 * for iterating through the song chart while taking into account the effects
 * of BPM changes -- since the chart scrolls at a constant speed the spacing
 * of the chart changes with the BPM.
 */
#define BEGIN_CHART_PER_BEAT_LOOP {	\
	double heightPerBeat = 0, yOffset = 0;	\
	unsigned short bpm = p_chart->bpm;	\
	size_t tick = 0, lastTick = (size_t)p_chart->duration * 1000;	\
	size_t bpmIndex = 0, millisecondsPerBeat = 0;	\
	event_t *bpmList = (event_t *)p_chart->events[CMD_BPM].dataList;	\
	size_t bpmListLen = p_chart->events[CMD_BPM].num;	\
	\
	/* Main construction loop.  We have to loop through all BPM changes	\
	 * since they affect the height of the chart and placement of notes. */	\
	while (tick < lastTick) {	\
		millisecondsPerBeat = MILLISECONDS_PER_BEAT(bpm);	\
		heightPerBeat = HEIGHT_PER_BEAT(bpm);	\
	\
		/* Increment one beat at a time.  If there are no more BPM changes	\
		 * then continue on this current BPM until the end of the song. */	\
		while (bpmIndex == bpmListLen || tick < bpmList[bpmIndex].tick) {

#define END_CHART_PER_BEAT_LOOP	\
			yOffset += heightPerBeat;	\
			tick += millisecondsPerBeat;	\
	\
			/* Don't run past the end of the song! */	\
			if (tick >= lastTick)	\
				break;	\
		}	\
	\
		if (bpmIndex >= bpmListLen) break;	\
	\
		bpm = (unsigned short)bpmList[bpmIndex].param1;	\
		bpmIndex++;	\
	}	\
}

int glNotesFromChartDrums(chart_t *p_chart) {
	size_t numLanes = NUM_LANES[DRUMS];
	double wLane = (W_CHART - (numLanes + 1) * W_LINE) / (double)numLanes;
	double xOffset = 0, yOffsetNote = 0;
	double xlenNote = 0, ylenNote = 0, zlenNote = 0;
	size_t noteIndex = 0, numNotes = p_chart->events[CMD_NOTE].num;
	size_t note = 0;
	event_t *notesList = (event_t *)p_chart->events[CMD_NOTE].dataList;

	p_chart->glChart.dlNotes = glGenLists(numNotes);
	if (!p_chart->glChart.dlNotes)
		PANIC(OGL, "glGenLists", "Unable to generate GL list");


BEGIN_CHART_PER_BEAT_LOOP
			while (noteIndex < numNotes) {
				// Wait for the next beat (BPM could change).
				if (notesList[noteIndex].tick > tick + millisecondsPerBeat)
					break;

				note = notesList[noteIndex].param1;
				yOffsetNote = SPD_CHART
					* (double)notesList[noteIndex].tick / 1000.0f;

				xlenNote = wLane;
				ylenNote = wLane / 2.0f;
				zlenNote = wLane / 4.0f;

				xOffset = W_LINE + wLane / 2.0f;

				glNewList(p_chart->glChart.dlNotes + noteIndex, GL_COMPILE);

				if (note & DRUMS_RED) {
					xOffset += 0;
					glColor3f(1.0f, 0.0f, 0.0f);
				} else if (note & DRUMS_YELLOW){
					xOffset += (wLane + W_LINE);
					glColor3f(1.0f, 1.0f, 0.0f);
				} else if (note & DRUMS_BLUE){
					xOffset += 2 * (wLane + W_LINE);
					glColor3f(0.0f, 0.0f, 1.0f);
				} else if (note & DRUMS_GREEN){
					xOffset += 3 * (wLane + W_LINE);
					glColor3f(0.0f, 1.0f, 0.0f);
				} else if (note & DRUMS_ORANGE) {
					xlenNote = W_CHART;
					ylenNote = DRUMS_ORANGE_HEIGHT;
					zlenNote = DRUMS_ORANGE_HEIGHT;
					
					xOffset = W_CHART / 2.0f;
					glColor3f(1.0f, 0.5f, 0.0f);
				}

				RECT_PRISM_CENTER(xOffset, yOffset + yOffsetNote,
						zlenNote / 2.0f, xlenNote, ylenNote, zlenNote);

				glEndList();

				noteIndex++;
			}
END_CHART_PER_BEAT_LOOP

	return 0;

panic_OGL:
panic_APP:
	return APP;
}

int glNotesFromChartGuitar(chart_t *p_chart) {
	return 0;
}


/* glSkeletonFromChart - construct a display list of the horizontal and vertical
 * lines that make up the chart body and store in p_chart->glChart. */
int glSkeletonFromChart(chart_t *p_chart, size_t numLanes) {
	double wLane = (W_CHART - (numLanes + 1) * W_LINE) / (double)numLanes;
	double xOffset = 0; 
	size_t i = 0;

	// Reserve a unique "name" for this display list.
	p_chart->glChart.dlSkel = glGenLists(1);

	if (!p_chart->glChart.dlSkel)
		PANIC(OGL, "glGenLists", "Unable to generate GL list");

	glNewList(p_chart->glChart.dlSkel, GL_COMPILE);

// IMPORTANT MACRO
BEGIN_CHART_PER_BEAT_LOOP

			// Create the vertical small lines that define the lanes.
			xOffset = 0;
			glColor3f(0.5f, 0.5f, 0.5f);
			for(i = 0; i <= numLanes; i++) {
				RECT_PRISM(xOffset, yOffset, 0.0f,
						W_LINE, (GLfloat)heightPerBeat, W_LINE);

				xOffset += wLane + W_LINE;
			}

			// Create the horizontal beat lines.
			glColor3f(1.0f, 1.0f, 1.0f);
			RECT_PRISM(0.0f, (GLfloat)yOffset, 0.0f,
					W_CHART, W_LINE, W_LINE);
				
			// And create the lighter half-beat lines.
			glColor3f(0.5f, 0.5f, 0.5f);
			RECT_PRISM(0.0f, (GLfloat)(yOffset + heightPerBeat / 2.0f), 0.0f,
					W_CHART, W_LINE, W_LINE);

// IMPORTANT MACRO
END_CHART_PER_BEAT_LOOP

	glEndList();

	return 0;

panic_OGL:
	return OGL;
}
