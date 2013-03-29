#!/usr/bin/env python
import os
import sys
import subprocess
import getopt


class Chdir:
    def __init__(self, newPath):
        self.savedPath = os.getcwd()
        os.chdir(newPath)


class Checker:
    def __init__(self, path):
        self.path = path

    def get_jobs(self):
        Chdir(self.path)
        jobs = []
        for dirname, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                i = os.path.join(dirname, filename)
                if i != "./__init__.py":
                    jobs.append(self.path + i[2:])
        self.run_jobs(jobs)

    def run_jobs(self, jobs):
        for job in jobs:
            subprocess.call(job)


if __name__ == '__main__':
    opts, path = getopt.getopt(sys.argv[1], "h")
    for opt, arg in opts:
        if opt == '-h':
            print './main.py /full/path/to/jobs'
            sys.exit()
    check = Checker(path)
    check.get_jobs()
