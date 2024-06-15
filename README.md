# ctest
A simple test driver for C code.

*ctest* is a super-simple framework for testing C code. It consists of a single executable python script: *ctest.py*.

**TL;DR** Make a `test` directory, copy `ctest.py` into it and run it to create `ctest.h`. Add tests in `.c` files within the `test` directory and `#include "ctest.h"` (see the examples). Run `ctest.py` each time you want to execute the test suite. 

## What it does:

- The first thing that *ctest* does is to write a `ctest.h` header file to the current working directory. This header has some macros that you can use to define test cases, make common test assertions, and so on.
- The current working directory is then traversed recursively to find all `.c` files. It's expected that the *ctest* command will be run in some kind of test directory. Each file is scanned for test definitions and, when found, *ctest* generates test driver code (in C) for those tests.
- The automatically generated test driver code is then compiled and executed.

Note:
*ctest* creates a test products directory in the current working directory. This directory is used to store automatically generated code and the compiled executable. These files are considered ephemeral so the test products directory (`ctest_temp` by default) can be added to `.gitignore`. 

⚠️  As mentioned, *ctest* is reading from and writing to your file system so you should read the script before you run it.

## Writing test cases.

Each test case is enclosed in a `CTEST_DEF` block. A file can contain multiple test cases.

```C
#include "ctest.h"

CTEST_DEF(some_test_name) {
  // Test code here.
}
```

The name of the test is translated into a C function, so it must obey the rules for C function names. Additionally, the name must be globally unique among all test case names in all files. The file name and test name are printed when each test is executed along with the test outcome.

## Test case assertions, etc.

All tests pass by default, so `some_test_name` shown above will pass.

This test will fail:

```C
#include "ctest.h"

CTEST_DEF(failing_test) {
  // This assertion will fail.
  int t = 2 + 2;
  CTEST_EXPECT_EQUAL(t, 5);

  // Code after the failure will continue to be executed.
  // This assertion will pass, but outcome is already fail.
  CTEST_EXPECT_NOT_EQUAL(t, 0);
}
```
Further test examples can be found in `test_examples_1.c` and `test_examples_2.c`.

### Test control flow.
- `CTEST_ABORT;`: A test will continue to execute code after any failing assertions. You can explicitly exit the test case by calling `CTEST_ABORT;`. This does not fail the test, it merely provides an early exit if desired.
- `CTEST_FAIL;`: Marks the test as failed (test execution continues).

### Assertions: 
`CTEST_EXPECT_EQUAL`, `CTEST_EXPECT_NOT_EQUAL`, `CTEST_EXPECT_ZERO`, `CTEST_EXPECT_NONZERO`, `CTEST_EXPECT_TRUE`, `CTEST_EXPECT_FALSE`.

## Test environment.
The compiler name (default is `clang`), the name of the test products directory, and the name of the automatically generated test driver are hard-coded into the first lines of `ctest.py` and can be edited there if necessary.

## `ctest.h` header.
The `ctest.h` header file is automatically generated each time that `ctest` runs. Here's a copy for reference.
```C
// DO NOT EDIT (THIS CODE IS AUTOMATICALLY GENERATED)

#ifndef CTEST_H
#define CTEST_H

#define CTEST_DEF(name) void name(int* result)
#define CTEST_FAIL *result = -1
#define CTEST_ABORT return
#define CTEST_EXPECT_EQUAL(x,y) if ((x) != (y)) { CTEST_FAIL; }
#define CTEST_EXPECT_NOT_EQUAL(x,y) if ((x) == (y)) { CTEST_FAIL; }
#define CTEST_EXPECT_ZERO(x) if ((x) != 0) { CTEST_FAIL; }
#define CTEST_EXPECT_NONZERO(x) if ((x) == 0) { CTEST_FAIL; }
#define CTEST_EXPECT_TRUE(x) CTEST_EXPECT_NONZERO(x);
#define CTEST_EXPECT_FALSE(x) CTEST_EXPECT_ZERO(x);

#endif
```
