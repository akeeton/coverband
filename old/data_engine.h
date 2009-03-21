/********************************
 * data_engine.h
 *
 * Last Modified:
 * 2 March 2009
 * by Andrew Keeton
********************************/
#ifndef __DATA_ENGINE_H__
#define __DATA_ENGINE_H__

#include "autoinc.h"

enum INSTRUMENT {
	MASTER = 0,	// Not technically an instrument but it goes in the field.
	GUITAR,
	BASS,
	DRUMS,
	VOCALS,
	NUM_INSTRUMENTS
};

static size_t NUM_LANES[] = {0, 5, 5, 4, 0};

enum DIFFICULTY {
	BEGINNER = 0,
	EASY,
	MEDIUM,
	HARD,
	EXPERT,
	NUM_DIFFICULTIES
};

enum COMMAND {
	CMD_NOTE = 0,		// Single note.  Drums should use separate single notes for
						// simulataneous notes.
	CMD_CHORD,			// Drums don't use chords.
	CMD_BEGIN,
	CMD_END,
	CMD_BPM,		// Change BPM.
	NUM_COMMANDS
};

enum BASS_NOTES {
	BASS_GREEN	= 0x1,
	BASS_RED	= 0x2,
	BASS_YELLOW	= 0x4,
	BASS_BLUE	= 0x8,
	BASS_ORANGE	= 0x10,
	NUM_BASS_NOTES	= 5
};

enum GUITAR_NOTES {
	GUITAR_GREEN	= 0x1,
	GUITAR_RED		= 0x2,
	GUITAR_YELLOW	= 0x4,
	GUITAR_BLUE		= 0x8,
	GUITAR_ORANGE	= 0x10,
	NUM_GUITAR_NOTES	= 5
};

enum DRUMS_NOTES {
	DRUMS_RED		= 0x1,
	DRUMS_YELLOW	= 0x2,
	DRUMS_BLUE		= 0x4,
	DRUMS_GREEN		= 0x8,
	DRUMS_ORANGE	= 0x10,
	NUM_DRUMS_NOTES	= 5
};

enum NOTE_MODIFIERS {
	HOPO = 0,
	NUM_NOTE_MODIFIERS
};

/* struct event_t - events are notes, BPM changes,
 * animations, fills, etc that occur within the course
 * of a song.  The master chart contains global events - 
 * animations, etc.
 */
typedef struct {
	size_t tick;		// Total elapsed time in milliseconds.
	size_t cmd;
	size_t param1;	// In the case of notes, 1-bit flags.
	size_t param2;
} event_t;

typedef struct {
	GLuint dlSkel;	// The board display list (horizontal and vertial lines).
	GLuint dlNotes;	// Sequential display lists for notes.
					// notes + i gives the ith note display list.
} glchart_t;

/* chart_t - a list of events and a graphical representation of a note chart. */
typedef struct {
	// Included in file I/O.
	enum INSTRUMENT instrument;
	enum DIFFICULTY difficulty;
	unsigned short bpm;			// Starting BPM
	unsigned short duration;	// Duration of the song in seconds.

	// Not included in file I/O.
	sorted_array_t allEvents;	// Single sorted array containing all events.
	sorted_array_t events[NUM_COMMANDS];	// Array of event-specific sorted arrays.
	glchart_t glChart;
} chart_t;

typedef struct {
	char title[64];
	char artist[64];

	// TODO: Replace with a concrete implementation of song track data.
	void *track[NUM_INSTRUMENTS];		// Song track for each instrument.
	chart_t charts[NUM_INSTRUMENTS];	// Note chart for each instrument.
} song_t;

typedef struct {
	int add_some_options;
} options_t;

typedef struct {
	song_t *songs;						// List of songs

	options_t options;					// Various options for this session.
} session_t;

int chartFromFile(const char *pathname, chart_t *p_chart);
int fileFromChart(const char *pathname, chart_t *p_chart);
int addEvent(chart_t *p_chart, event_t *event);
int removeEvent(chart_t *p_chart, event_t *event);
int destroyChart(chart_t *p_chart);

#endif	// __DATA_ENGINE_H__
