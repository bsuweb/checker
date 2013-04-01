#!/usr/bin/env python
import os
import sys
import subprocess
import argparse


class Checker:
    def __init__(self, path):
        if not os.path.isdir(path):
            sys.exit(1)
        self.path = os.path.realpath(path)
        self.jobs = self.getExecutableFiles(self.path)

    def getExecutableFiles(self, path):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filename_path = os.path.join(dirname, filename)
                if os.access(filename_path, os.X_OK):
                    files.append(filename_path)
        return files

    def run(self):
        for job in self.jobs:
            subprocess.call(job)


if __name__ == '__main__':
    # Add CLI parsing.
    parser = argparse.ArgumentParser(
        description="""A script that runs all the jobs in the given directory
                    and keeps track of responses in an sqlite database.""")
    parser.add_argument('path', metavar='jobs-directory', type=str, nargs=1,
                        help='Path to the directory where executable jobs are.')
    args = parser.parse_args()

    # Initialize and run the checker.
    check = Checker(args.path[0])
    check.run()
