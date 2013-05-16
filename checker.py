#!/usr/bin/env python
from os import walk, X_OK, access
from os.path import basename, splitext, isdir, realpath, join
import datetime
import sys
import subprocess
import argparse
import data
import json
import contact


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
            current = basename(splitext(job)[0])
            now = datetime.datetime.now()
            process = subprocess.Popen(job, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            out = process.communicate()
            ret = process.poll()

            # Create database checker_log.sqlite if it doesn't exist
            db = data.Data('checker_log.sqlite')
            db.make(current, ' (datetime text, exit_code integer, value text)')

            try:
                out = json.loads(str(out[0]))
            except ValueError:
                out = out[0]
            else:
                out = out["value"]
            finally:
                db.insert_values(current,
                                 "('"+str(now)+"',"+str(ret)+",'"+out+"')")

            if ret == 1:
                # Something went wrong with the current job. Send email.
                message = "There is something wrong with " + current
                emails = db.query('users', 'jobs', current)
                # mail = contact.Email(EMAILLIST, message, SUBJECT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A script that runs all the jobs in the given directory"
                    " and keeps track of responses in an sqlite database.")
    parser.add_argument('path', metavar='jobs-directory', type=str, nargs=1,
                        help='Path to the directory where executable jobs are.')
    args = parser.parse_args()

    # Initialize and run the checker.
    check = Checker(args.path[0])
    check.run()
