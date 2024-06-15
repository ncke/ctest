#!/usr/bin/env python3

compiler = "clang"
test_products_dir = "ctest_temp"
generated_main = "cmainc.c"

from os import walk, getcwd
import subprocess
from sys import exit

test_count = 0
file_count = 0

ctest_h = [
  '// DO NOT EDIT (THIS CODE IS AUTOMATICALLY GENERATED)',
  '',
  '#ifndef CTEST_H',
  '#define CTEST_H',
  '',
  '#define CTEST_DEF(name) void name(int* ctest_exec_result)',
  '#define CTEST_FAIL *ctest_exec_result = -1',
  '#define CTEST_ABORT return',
  '#define CTEST_EXPECT_EQUAL(x,y) if ((x) != (y)) { CTEST_FAIL; }',
  '#define CTEST_EXPECT_NOT_EQUAL(x,y) if ((x) == (y)) { CTEST_FAIL; }',
  '#define CTEST_EXPECT_ZERO(x) if ((x) != 0) { CTEST_FAIL; }',
  '#define CTEST_EXPECT_NONZERO(x) if ((x) == 0) { CTEST_FAIL; }',
  '#define CTEST_EXPECT_TRUE(x) CTEST_EXPECT_NONZERO(x);',
  '#define CTEST_EXPECT_FALSE(x) CTEST_EXPECT_ZERO(x);',
  '',
  '#endif'
]

headers = [
  '// DO NOT EDIT (THIS CODE IS AUTOMATICALLY GENERATED)',
  '',
  '#define CTEST_GREEN "\\033[32m"',
  '#define CTEST_RED "\\033[31m"',
  '#define CTEST_RESET "\\033[0m"',
  '',
  '#include <stdio.h>',
  '#include "ctest.h"'
]

mainc = [
  '',
  'int main() {',
  '',
  'int ctest_exec_count = 0;',
  'int ctest_fail_count = 0;',
  ''
]

def run_command(command, capture_output=True, exit_upon_error=True):
  try:
    result = subprocess.run(
      command, 
      capture_output=capture_output, 
      text=True, 
      check=True)
    return result.stdout
  
  except subprocess.CalledProcessError as e:
    if exit_upon_error == False:
      return e.stderr
    
    print(f'error: {e}\n{e.stderr}\n')
    print('\033[31mtest process failed\033[0m')
    exit(1)

def traverse_files(path):
  for (dirpath, dirnames, filenames) in walk(path):
    for filename in filenames:
      if filename[-2:] == '.c' and filename != generated_main:
        find_tests_in_file(dirpath, filename)
    for dirname in dirnames:
      traverse_files(dirpath + '/' + dirname)

def find_tests_in_file(dir_path, filename):
  test_found = False
  
  file_path = dir_path + '/' + filename
  with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:

      if line.find('CTEST_DEF') < 0:
        continue

      open_idx = line.find('(')
      close_idx = line.find(')')
      if open_idx < 0 or close_idx < 0 or open_idx >= close_idx:
        print('test syntax error in line: ', line)
        print('\033[31mtest process failed\033[0m\n')
        exit(1)
      
      test_name = line[open_idx+1:close_idx]

      if not test_found:
        test_found = True
        add_header(file_path)

      add_test(file_path, test_name)

def add_header(file_path):
  global file_count
  file_count += 1

  print('assembling tests from: ', file_path)

  headers.append(f'#include "{file_path}"')
  mainc.append(f'// TESTS FROM: {file_path}')
  mainc.append(f'')
  mainc.append(f'printf(CTEST_RESET "{file_path}:\\n");')

def add_test(file_path, test_name):
  global test_count
  test_count += 1

  mainc.append( '{')
  mainc.append(f'  printf(CTEST_RESET "{test_name}");')
  mainc.append(f'  int result = 0; {test_name}(&result);')
  mainc.append( '  ctest_exec_count += 1;')
  mainc.append( '  if (result < 0) {')
  mainc.append( '    ctest_fail_count += 1;')
  mainc.append(f'    printf("\\r" CTEST_RED "fail: {test_name}\\n");')
  mainc.append( '  } else {')
  mainc.append(f'    printf("\\r" CTEST_GREEN "pass: {test_name}\\n");')
  mainc.append( '  }')
  mainc.append( '}')
  mainc.append( '')

def add_result_code():
  mainc.append('if (ctest_fail_count == 0)')
  mainc.append('  printf(CTEST_GREEN);')
  mainc.append('else')
  mainc.append('  printf(CTEST_RED);')
  mainc.append('printf("executed %d tests with %d failures\\n", ctest_exec_count, ctest_fail_count);')
  mainc.append('if (ctest_fail_count == 0)')
  mainc.append('  printf("all tests passed\\n");')
  mainc.append('else')
  mainc.append('  printf("tests failed\\n");')
  mainc.append('printf(CTEST_RESET);')
  mainc.append('')
  mainc.append('return ctest_fail_count == 0 ? 0 : 1;')
  mainc.append('}')

def write_test_driver():
  run_command(['mkdir', '-p', f'{test_products_dir}'])
  
  with open(f'./{test_products_dir}/{generated_main}', 'w') as file:
    for line in headers:
      file.write(line + '\n')
    for line in mainc:
      file.write(line + '\n')

def write_ctest_header_file():
  with open('./ctest.h', 'w') as file:
    for line in ctest_h:
      file.write(line + '\n')

def compile_test_driver():
  run_command([
    f'{compiler}', 
    '-I./', f'./{test_products_dir}/{generated_main}', 
    '-o', f'./{test_products_dir}/ctest_driver'
    ])

def run_test_driver():
  result = run_command(
    f'./{test_products_dir}/ctest_driver', 
    capture_output=False, 
    exit_upon_error=False)

def main():
  # Print the test environment.
  print('\033[32mstarting tests\033[0m')
  print(f'compiler: {compiler}')
  print(f'test_products_dir: {test_products_dir}')
  print(f'generated_main: {generated_main}')

  # Write ctest.h
  print('writing ctest.h header file')
  write_ctest_header_file()

  # Traverse from current working directory to find tests.
  print('finding tests')
  cwd = getcwd()
  print('traversing from: ', cwd)
  traverse_files(cwd)
  print('found ', test_count, ' tests in ', file_count, 'files')

  # Add code to the test driver to show the overall result.
  add_result_code()

  # Write the test driver.
  write_test_driver()
  print('test driver code generated')

  # Compile.
  print('compiling test driver')
  compile_test_driver()

  # And run.
  print('running test driver')
  run_test_driver()

if __name__ == "__main__":
  main()
