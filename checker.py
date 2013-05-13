#!/usr/bin/env python
from os import walk, X_OK, access
from os.path import basename, splitext, isdir, realpath, join
import datetime
import sys
import subprocess
import argparse
import create_table


class Checker:
    def __init__(self, path):
        if not isdir(path):
            sys.exit(1)
        self.path = realpath(path)
        self.jobs = self.getExecutableFiles(self.path)

    def getExecutableFiles(self, path):
        files = []
        for dirname, dirnames, filenames in walk(path):
            for filename in filenames:
                filename_path = join(dirname, filename)
                if access(filename_path, X_OK):
                    files.append(filename_path)
        return files

    def run(self):
        for job in self.jobs:
            now = datetime.datetime.now()
            process = subprocess.Popen(job, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            output = process.communicate()
            retcode = process.poll()

            # Create database checker_log.sqlite if it doesn't exist
            db = create_table.CreateTable('checker_log.sqlite')
            # Create job table if it doesn't exist
            db.make(basename(splitext(job)[0]),
                    ' (datetime text, exit_code integer, value text)')
            # Insert values into table
            db.insert_values(basename(splitext(job)[0]),
                             "('"+str(now)+"',"+str(retcode)+",'"+output[0]+"')")

if __name__ == '__main__':
    # Add CLI parsing.
    parser = argparse.ArgumentParser(
        description="A script that runs all the jobs in the given directory"
                    " and keeps track of responses in an sqlite database.")
    parser.add_argument('path', metavar='jobs-directory', type=str, nargs=1,
                        help='Path to the directory where executable jobs are.')
    args = parser.parse_args()

    # Initialize and run the checker.
    check = Checker(args.path[0])
    check.run()
