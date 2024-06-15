#include "ctest.h"

CTEST_DEF(a_failing_test) {
  int t = 2 + 2;
  CTEST_EXPECT_EQUAL(t, 5);
}

CTEST_DEF(another_failing_test) {
  int t = 2 + 2;
  CTEST_EXPECT_NOT_EQUAL(t, 4);
}

CTEST_DEF(yet_another_failing_test) {
  int t = 4;
  if (t < 0)
  	CTEST_ABORT;

  CTEST_FAIL;
}