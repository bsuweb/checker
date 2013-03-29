#!/usr/bin/env python
import os
import sys
import subprocess
import getopt


class Checker:

    def __init__(self, path):
        if not os.path.isdir(path):
            sys.exit(1);
        self.path = os.path.realpath(path)
        self.jobs = self.getExecutableFiles(self.path)

    def getExecutableFiles(self,path):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filename_path = os.path.join(dirname, filename)
                if os.access(filename_path,os.X_OK):
                    files.append(filename_path)
        return files;

    def run(self):
        for job in self.jobs:
            subprocess.call(job)


if __name__ == '__main__':
    opts, path = getopt.getopt(sys.argv[1], "h")
    for opt, arg in opts:
        if opt == '-h':
            print './main.py /full/path/to/jobs'
            sys.exit()
    check = Checker(path)
    check.run()
