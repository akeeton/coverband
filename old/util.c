/*************************************************************************
 * util.c
 *
 * Last Modified:
 * 2 March 2009
 * by Andrew Keeton
 *
 * Purpose: Provide various utility functions and macros that don't
 * belong anywhere else.
 ************************************************************************/

#include "autoinc.h"

/* freeAll - free every pointer passed. */
void freeAll(size_t num, ...) {
	size_t i;	
	va_list ap;
	void **ptrptr = NULL;

	va_start(ap, num);

	for(i = 0; i < num; i++) {
		ptrptr = va_arg(ap, void **);
		free(*ptrptr);
		*ptrptr = NULL;
	}

	va_end(ap);
}

static inline void *GET(sorted_array_t *sa, size_t index) {
	return (void *)((char *)sa->dataList + sa->elemSize * index);
}

/* saFindIndex - return the index of the item (or where the item should go)
 * using binary search.  If a match was found, indicate through the bool found. */
static size_t saFindIndex(sorted_array_t *sa, const void *data, bool *found) {
	size_t low, high, mid;
	enum COMPARE cmp;

	if (sa->num == 0) {
		if (found) *found = false;
		return 0;
	}

	low = 0;
	high = sa->num - 1;

	// First see if the item should be appended to the end of the list since
	// this is a common operation.
	cmp = sa->cmp(data, GET(sa, high));
	if (cmp == GREATER_THAN) {
		if (found) *found = false;
		return sa->num;
	}

	// Also check that the item doesn't belong at the beginning of the list.
	cmp = sa->cmp(data, GET(sa, low));
	if (cmp == LESS_THAN) {
		if (found) *found = false;
		return low;
	}

	while (low <= high) {
		mid = low + ((high - low) / 2);

		cmp = sa->cmp(GET(sa, mid), data);
		if (cmp == GREATER_THAN) {
			high = mid - 1;

			if (high < low) {
				if (found) *found = false;
				return mid;
			}

		} else if (cmp == LESS_THAN) {
			low = mid + 1;

			if (low > high) {
				if (found) *found = false;
				return mid + 1;
			}
		} else {
			if (found) *found = true;
			return mid;
		}
	}

	// If we get here, then we haven't found the item but this is where
	// we should insert it if we intend to.
	if (found) *found = false;
	return mid;
}

/* saInsert - insert an item into the list at a specific index. */
static int saInsert(sorted_array_t *sa, const void *data, size_t index) {
	// Reallocate if necessary.
	if (sa->num == sa->capacity) {
		sa->capacity *= 2;
		sa->dataList = (void *)realloc(sa->dataList,
				sa->capacity * sa->elemSize);

		if (!sa->dataList) PANIC(SYS, "realloc", 
				"Unable to reallocate memory for sorted data list");
	}

	// Move the elements up by one.
	memmove(GET(sa, index + 1), GET(sa, index), sa->elemSize * (sa->num - index));

	// Copy the data into the list.
	memcpy(GET(sa, index), data, sa->elemSize);

	sa->num++;

	return 0;
panic_SYS:
	return ERR;
}

static void saRemoveIndex(sorted_array_t *sa, size_t index) {
	if (index < sa->num - 1)
		// Shift everything down by one.
		memmove(GET(sa, index), GET(sa, index + 1),
				sa->elemSize * (sa->num - index - 1));

	sa->num--;

	return;
}

/* saInit -	base: pointer to the first element in the array
 * 			num: number of elements in the array
 * 			elemSize: size of each element in the array
 * 			cmp: comparator function that returns LESS_THAN, EQUAL, or GREATER_THAN
 *
 * saInit copies the elements of the array and sorts them.  If a NULL base pointer
 * is passed, then no array is copied and sorted.
 */
int saInit(sorted_array_t *sa, const void *base, size_t num, size_t elemSize,
		enum COMPARE (*cmp)(const void *d1, const void *d2)) {
	if (!sa) PANIC(APP, "saInit", "Null sorted array pointer");
	if (!cmp) PANIC(APP, "saInit", "Null comparison function pointer" );

	if (!base) num = 0;

	sa->elemSize = elemSize;
	sa->capacity = (num > SA_MIN_CAPACITY) ? num : SA_MIN_CAPACITY;
	sa->num = num;
	sa->cmp = cmp;

	sa->dataList = NULL;
	sa->dataList = (void *)malloc(sa->capacity * sa->elemSize);
	if (!sa->dataList)
		PANIC(SYS, "malloc", "Unable to allocate memory for sorted data list");

	// Copy and sort the array if it exists.
	if (base) {
		memcpy(sa->dataList, base, num * elemSize);
		qsort(sa->dataList, num, elemSize, cmp);
	}

	sa->initialized = true;

	return 0;

panic_SYS:
panic_APP:
	freeAll(1, &sa->dataList);
	return ERR;
}

/* saDestory - free user data if given a destructor function and free internals.
 * If the sorted array was not initialized, don't do anything. */
int saDestroy(sorted_array_t *sa, void (*dtor)(const void *data)) {
	size_t i = 0;
	if (!sa) PANIC(APP, "saInit", "Null sorted array pointer");
	if (!sa->initialized) return 1;

	// If the user supplied a destructor function pointer, then use it
	// to clean up all of the elements in the list.
	if (dtor)
		for (i = 0; i < sa->num; i++)
			dtor(GET(sa, i));

	freeAll(1, &sa->dataList);

	return 0;
panic_APP:
	return ERR;
}


/* saAdd - add the item in sorted order to the list. */
int saAdd(sorted_array_t *sa, const void *data) {
	size_t index = 0;

	if (!sa) PANIC(APP, "saAdd", "Null sorted array pointer");
	if (!sa->initialized)
		PANIC(APP, "saAdd", "Trying to add data to unitialized sorted array");
	if (!data) PANIC(APP, "saAdd", "Null data pointer");

	index = saFindIndex(sa, data, NULL);

	if (saInsert(sa, data, index) < 0)
		PANIC(APP, "saInsert", "Unable to insert data into sorted data list");

	return 0;
	
panic_APP:
	return ERR;
}

/* saRemove - remove an item that matches from the list and return it via removed. */
int saRemove(sorted_array_t *sa, const void *data) {
	size_t index = 0;
	bool found = false;

	if (!sa) PANIC(APP, "saRemove", "Null sorted array pointer");
	if (!sa->initialized) return 1;

	if (!data) PANIC(APP, "saRemove", "Null data pointer");

	index = saFindIndex(sa, data, &found);

	if (found) saRemoveIndex(sa, index);
	else return 1;

	return 0;

panic_APP:
	return ERR;
}
