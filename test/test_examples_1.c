#include "ctest.h"

CTEST_DEF(test_something) {
  int t = 2 + 2;
  CTEST_EXPECT_EQUAL(t, 4);
}

CTEST_DEF(test_something_else) {
  int t = 0;
  CTEST_EXPECT_ZERO(t);
}

CTEST_DEF(yet_another_test) {
  int t = -1;
  if (t < 0)
  	CTEST_ABORT;

  CTEST_FAIL;
}
