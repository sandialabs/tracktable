# Python Legacy Test Cases

There are a lot of test cases to move over from old-style tests (which CMake will pass or fail based on the return value from `main()`) and PyTest format.

For the time being, all of the PyTest test cases are in `tests/Python/pytest/tests`.  Everything outside that tree is an old-style test.

Here's how to move a test over:

1. Choose a file of old-style test cases.
2. Copy it to `tests/Python/pytest/tests/<dir_name>`.  Create that directory if necessary.
3. Modify all the tests in the file to operate on assertions instead of counting errors.
4. Make liberal use of fixtures.  If you create fixtures that would be useful to other tests, put them in `conftest.py`.
5. Remove `main()` and the `if __name__ == "__main__"` boilerplate.
6. Remove the test from `CMakeLists.txt` in the directory where you first found it.
7. Re-run the build to get `pytest-cmake` to pick up the new test.
8. Make sure all the tests in the file you just created passes.
9. `git add` the new file of tests and `git rm` the old file, then commit both at the same time.
10. If this was the last test in the old directory, `git rm CMakeLists.txt` to turn the lights off on your way out.

Once we're done moving all the old-style tests, we'll reorganize the directory tree and all that will be left is PyTest.

