/*******************************************
 * data_engine.c
 *
 * Last Modified:
 * 3 March 2009
 * by Andrew Keeton
 *
 * Purpose: Core functions for handling data.
********************************************/

#include "autoinc.h"


enum COMPARE compEvents(const void *d1, const void *d2) {
	const event_t *e1 = (const event_t *)d1;
	const event_t *e2 = (const event_t *)d2;

	if (e1->tick < e2->tick) return LESS_THAN;
	else if (e1->tick > e2->tick) return GREATER_THAN;
	else {
		if (e1->cmd < e2->cmd) return LESS_THAN;
		else if (e1->cmd > e2->cmd) return GREATER_THAN;
		else {
			if (e1->param1 < e2->param1) return LESS_THAN;
			else if (e1->param1 > e2->param1) return GREATER_THAN;
			else {
				if (e1->param2 < e2->param2) return LESS_THAN;
				else if (e1->param2 > e2->param2) return GREATER_THAN;
				else return EQUAL;
			}
		}
	}
}

#define BUF_SIZE 64
/* chartFromFile - open a binary chart file and read its contents
 * into struct form.  Allocate memory for the chart structure. */
int chartFromFile(const char *pathname, chart_t *p_chart) {
	size_t i = 0, dt = 0, tick = 0;
	char lineBuf[BUF_SIZE];
	FILE *fp = NULL;
	event_t event = {0};

	// Initialize all of the sorted arrays.
	p_chart->allEvents.initialized = false;
	if (saInit(&p_chart->allEvents, NULL, 0, sizeof(event_t), compEvents) < 0)
		PANIC(APP, "saInit", "Unable to initialize sorted array of events");

	for (i = 0; i < NUM_COMMANDS; i++) {
		p_chart->events[i].initialized = false;
		if (saInit(&p_chart->events[i], NULL, 0,
					sizeof(event_t), compEvents) < 0)
			PANIC(APP, "saInit", "Unable to initialize sorted array of events");
	}

	fp = fopen(pathname, "r");
	if (!fp) PANIC(SYS, "fopen", "Unable to open file for reading");

	// Read in header data.
	if (fgets(lineBuf, BUF_SIZE, fp) == NULL)
		PANIC(SYS, "fgets", "Unable to header read string");

	if (sscanf(lineBuf, "%d %d %hu %hu\n", (int *)(&p_chart->instrument),
				(int *)(&p_chart->difficulty),
				&p_chart->bpm, &p_chart->duration) < 4)
		PANIC(SYS, "sscanf", "Unable to match all header items");

	// Add events to the sorted arrays.
	while (fgets(lineBuf, BUF_SIZE, fp)) {
		if (sscanf(lineBuf, "%u %u %u %u\n", &dt, &event.cmd,
					&event.param1, &event.param2) < 4)
			PANIC(SYS, "sscanf", "Unable to match all event items");

		tick += dt;
		event.tick = tick;

		addEvent(p_chart, &event);
	}

	if (ferror(fp)) PANIC(SYS, "fgets", "Unable to read event string");

	if (fclose(fp) < 0) PANIC(SYS, "fclose", "Unable to close file");
	fp = NULL;

	// Create an OpenGL representation of the chart.
	// IMPORTANT: The SDL/OpenGL system must have been initialized already
	// since glFromChart makes OpenGL calls.
	if (glFromChart(p_chart) < 0)
		PANIC(APP, "glFromChart", "Unable to create OpenGL chart");

	return 0;

panic_SYS:
panic_APP:
	saDestroy(&p_chart->allEvents, NULL);

	for (i = 0; i < NUM_COMMANDS; i++)
		saDestroy(&p_chart->events[i], NULL);

	if (fp) (void)fclose(fp);

	return ERR;
}

/* fileFromChart - write chart data (header and events) to file. */
int fileFromChart(const char *pathname, chart_t *p_chart) {
	size_t i = 0, numEvents = 0, dt = 0, prevTick = 0;
	event_t *eventsList = NULL;			// For convenience.
	FILE *fp = NULL;

	if (!p_chart) PANIC(APP, "fileFromChart", "Null chart pointer");

	eventsList = (event_t *)(p_chart->events->dataList);
	numEvents = p_chart->events->num;

	// Open the chart file for writing.
	fp = fopen(pathname, "wb");
	if (!fp) PANIC(SYS, "fopen", "Unable to open file for writing");

	// Write the header data (non-binary) to the file.
	if (fprintf(fp, "%d %d %hu %hu\n",
				p_chart->instrument, p_chart->difficulty,
				p_chart->bpm, p_chart->duration) < 0)
		PANIC(SYS, "fprintf", "Unable to write chart header data to file");

	prevTick = 0;
	// Write the event data to file.
	for (i = 0; i < numEvents; i++) {
		dt = eventsList[i].tick - prevTick;
		prevTick = eventsList[i].tick;

		if (fprintf(fp, "%u %u %u %u\n", dt, eventsList[i].cmd,
				eventsList[i].param1, eventsList[i].param2) < 4)
			PANIC(SYS, "fprintf", "Unable to write chart event data to file");
	}

	// Cleanup
	if (fclose(fp) < 0) PANIC(SYS, "fclose", "Unable to close file");
	fp = NULL;

	return 0;
	
panic_APP:
panic_SYS:
	if (fp) (void)fclose(fp);

	return SYS;
}

int addEvent(chart_t *p_chart, event_t *event) {
	if (!p_chart) PANIC(APP, "addEvent", "Null chart pointer");
	if (!event) PANIC(APP, "addEvent", "Null event pointer");

	if (saAdd(&p_chart->allEvents, event) < 0)
		PANIC(APP, "saAdd", "Unable to add event to sorted list of all events");
	if (saAdd(&p_chart->events[event->cmd], event) < 0)
		PANIC(APP, "saAdd", "Unable to add event to sorted list of events");

	return 0;

panic_APP:
	return ERR;
}

int removeEvent(chart_t *p_chart, event_t *event) {
	int ret = 0;

	if (!p_chart) PANIC(APP, "addEvent", "Null chart pointer");
	if (!event) PANIC(APP, "addEvent", "Null event pointer");

	ret = saRemove(&p_chart->allEvents, event);

	if (ret < 0)
		PANIC(APP, "saRemove", "Unable to remove event from list of all events");
	if (ret > 0) return ret;

	ret = saRemove(&p_chart->events[event->cmd], event);

	if (ret < 0)
		PANIC(APP, "saRemove", "Unable to remove event from list of events");
	if (ret > 0) return ret;

	return 0;

panic_APP:
	return ERR;
}

int destroyChart(chart_t *p_chart) {
	size_t i = 0;

	if (!p_chart) PANIC(APP, "destroyChart", "Null chart pointer");

	if (saDestroy(&p_chart->allEvents, NULL) < 0)
		PANIC(APP, "saDestroy", "Unable to destroy events list");

	for (i = 0; i < NUM_COMMANDS; i++) {
		if (saDestroy(&p_chart->events[i], NULL) < 0)
			PANIC(APP, "saDestroy", "Unable to destroy events list");
	}

	return 0;

panic_APP:
	return ERR;
}
