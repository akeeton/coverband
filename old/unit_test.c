#include "autoinc.h"

#ifdef __UNIT_TEST__

#define NNUMS	100

enum COMPARE compInts(const void *d1, const void *d2) {
	int num1, num2;

	num1 = *(const int *)d1;
	num2 = *(const int *)d2;

	if (num1 > num2) return GREATER_THAN;
	else if (num1 < num2) return LESS_THAN;
	else return EQUAL;
}

int main(int argc, char *argv[]) {
	int nums[NNUMS];
	size_t i = 0, j = 0;
	sorted_array_t saInts;

	srand(10);

	for (i = 0; i < NNUMS; i++) {
		nums[i] = rand() % 10;
		printf("%d ", nums[i]);
	}
	printf("\n");

	saInit(&saInts, nums, NNUMS, sizeof(int), &compInts);

	assert(saInts.num == NNUMS);

	for (i = 0; i < saInts.num; i++)
		printf("%d ", *((int *)saInts.dataList + i));
	printf("\n");

	for (i = 0; i < NNUMS; i++) {
		saRemove(&saInts, nums + i);
		for (j = 0; j < saInts.num; j++)
			printf("%d ", *((int *)saInts.dataList + j));

		printf("\n");
	}

	assert(saInts.num == 0);

	for (i = 0; i < NNUMS; i++) {
		nums[i] = rand() % 10;
		printf("%d ", nums[i]);
	}
	printf("\n");

	for (i = 0; i < NNUMS; i++) {
		saAdd(&saInts, nums + i);
	}

	assert(saInts.num == NNUMS);

	for (i = 0; i < saInts.num; i++)
		printf("%d ", *((int *)saInts.dataList + i));
	printf("\n");

	saDestroy(&saInts, NULL);

	return 0;
}

#endif	// __UNIT_TEST__
