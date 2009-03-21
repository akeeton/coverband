/*************************************************************************
 * util.h
 *
 * Last Modified:
 * 28 February 2009
 * by Andrew Keeton
 ************************************************************************/

#ifndef __UTIL_H__
#define __UTIL_H__

#include "autoinc.h"

extern int errno;

// DANGER: Macro voodoo ahead.
#define JOIN_AGAIN(x, y) x #y
#define JOIN(x, y) JOIN_AGAIN(x, y)

// Panic error conditions.
#define	ERR	-1
#define SYS	-2
#define	SDL	-3
#define OGL	-4
#define	APP	-5

#define PANIC(lvl, func, msg) { 							\
	switch(lvl) {											\
		case SYS:											\
			fprintf(stderr, "Error at %s (%s): %s: %s\n",	\
					JOIN(__FILE__, :__LINE__),				\
					func, msg, strerror(errno));			\
			break;											\
		case SDL:											\
			fprintf(stderr, "Error at %s (%s): %s: %s\n",	\
					JOIN(__FILE__, :__LINE__),				\
					func, msg, SDL_GetError());				\
			break;											\
		case OGL:											\
			fprintf(stderr, "Error at %s (%s): %s: OpenGL error #%d\n",	\
					JOIN(__FILE__, :__LINE__),				\
					func, msg, glGetError());				\
			break;											\
		case APP:											\
			fprintf(stderr, "Error at %s (%s): %s\n",		\
					JOIN(__FILE__, :__LINE__), func, msg);	\
			break;											\
		default:											\
			fprintf(stderr, "Error at %s (%s): %s\n",		\
					JOIN(__FILE__, :__LINE__), func, msg);	\
			break;											\
	}														\
	goto panic_ ## lvl;										\
}

enum COMPARE {
	EQUAL = 0,
	GREATER_THAN = 1,
	LESS_THAN = -1
};

#define SA_MIN_CAPACITY 16	// Allocate at least 64 elements worth of capacity.

typedef struct {
	bool initialized;
	size_t elemSize;
	size_t capacity;	// Internal capacity in elements.
	size_t num;			// Number of elements.

	void *dataList;		// Array of elements.

	enum COMPARE (*cmp)(const void *d1, const void *d2);
} sorted_array_t;

void freeAll(size_t num, ...);

int saInit(sorted_array_t *sa, const void *base, size_t num, size_t elemSize,
		enum COMPARE (*cmp)(const void *d1, const void *d2));
int saDestroy(sorted_array_t *sa, void (*dtor)(const void *data));
int saAdd(sorted_array_t *sa, const void *data);
int saRemove(sorted_array_t *sa, const void *data);

#endif // __UTIL_H__
