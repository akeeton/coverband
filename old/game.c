/********************************
 * game.c
 *
 * Last Modified:
 * 2 March 2009
 * by Andrew Keeton
********************************/

#include "autoinc.h"

#ifndef __UNIT_TEST__
int main(int argc, char *argv[]) {
	bool done;
	Uint8 *keys;
	chart_t chart;
	SDL_Surface *screen;

	if (SDL_Init(SDL_INIT_VIDEO) < 0)
		PANIC(SDL, "SDL_Init", "Unable to initialize SDL video");

	if (initScreen(&screen) < 0)
		PANIC(APP, "initScreen", "Unable to intialize screen");

	// Test reading from a file.
	if (chartFromFile("drumsin.chart", &chart) < 0)
		PANIC(APP, "chartFromFile", "Unable to read chart from file");

	// Test writing back to a file.
	if (fileFromChart("drumsout.chart", &chart) < 0)
		PANIC(APP, "fileFromChart", "Unable to write chart to file");

	/* Main game loop */
	done = false;
	while (!done) {
		SDL_Event event;

		while (SDL_PollEvent(&event)) {
			switch(event.type) {
				case SDL_VIDEORESIZE:
					screen = SDL_SetVideoMode(event.resize.w, event.resize.h, 0,
							SDL_OPENGL|SDL_RESIZABLE);
					if (!screen) PANIC(SDL, "SDL_SetVideoMode",
							"Unable to set new video mode");

					resizeGL((size_t)screen->w, (size_t)screen->h);
					break;

				case SDL_QUIT:
					done = true;
					break;
			}
		}
		keys = SDL_GetKeyState(NULL);

		if (keys[SDLK_ESCAPE]) done = true;

		drawChart(&chart);
		SDL_GL_SwapBuffers();
	}

	destroyChart(&chart);
	SDL_Quit();

	return 0;

panic_SDL:
panic_APP:
	destroyChart(&chart);
	SDL_Quit();

	return ERR;
}
#endif 	// __UNIT_TEST__
