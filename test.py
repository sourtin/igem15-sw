#!/usr/bin/env python
if __name__ == '__main__':
    import os
    import sys
    import glob
    import traceback
    import subprocess

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)   

    if len(sys.argv) > 1:
        test = sys.argv[1]

    else:
        while True:
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

    subprocess.call([sys.executable, "-im", "var.tests.%s" % test])

