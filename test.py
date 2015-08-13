#!/usr/bin/env python
"""CLI helper file for running tests;
      Searches through and displays the list of
      available tests or runs the test specified
      in $1 (use as `./test.py TEST`, or just run
      `./test.py` and choose from the listed options"""

if __name__ == '__main__':
    import os
    import sys
    import glob
    import traceback
    import subprocess

    # cd to script director
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)   

    # run the cli-specified test
    if len(sys.argv) > 1:
        test = sys.argv[1]

    # prompt the user for a test
    else:
        # until a valid test had been chosen
        while True:
            # search for available tests
            ext = ".py"
            root = "var/tests/"
            tests = [test[len(root):-len(ext)].replace(".", " ").replace("/", ".")
                        for tests in [glob.glob(root + wild + ext) for wild in ["*", "**/*"]]
                            for test in tests]
            tests = [test for test in tests if ' ' not in test]

            print("Choose a test, or q to exit:")
            for i in range(len(tests)):
                print(" %2d) %s" % (i, tests[i]))
            choice = input("$ ").strip()
            print()

            if choice.lower() == 'q':
                print("goodbye.")
                os._exit(0)
            else:
                try:
                    test = tests[int(choice)]
                    break
                except:
                    continue

    # run the test in interactive mode (-i)
    # also need to run the test as a module (-m)
    # so it has access to the rest of the library
    subprocess.call([sys.executable, "-im", "var.tests.%s" % test])

