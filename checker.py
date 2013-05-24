#!/usr/bin/env python
from os import walk, X_OK, access, getcwd
from os.path import basename, splitext, isdir, realpath, abspath, join, commonprefix
import datetime
import sys
import subprocess
import argparse
import data
import glob
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
            out = out[0].splitlines()
            if ret > 0:
                # Something went wrong with the current job.
                # value is information to be saved in the database.
                # message is the information to be sent in the email.
                value = out[0]
                message = out[1]
                db.insert_values(current,
                                 "('"+str(now)+"',"+str(ret)+",'"+value+"')")
                # Check to see if anyone needs to be notified of the failure.
                users = db.query("SELECT email, checks FROM users")
                # For each pair of email/checks in the users table
                for jobs in users:
                    #jobs[0] => emails
                    #jobs[1] => checks
                    checks = jobs[1].split(',')
                    # For each job listed in the checks column
                    for i in checks:
                        test = glob.glob(i)
                        # Get the full path of each check, and compare it to
                        # the full path of the current job
                        for x in test:
                            temp = abspath(join(getcwd(), x))
                            # If they match
                            if job in temp:
                                print 'yes'
                                # Update current number of fails
                                db.update('UPDATE users SET cur_fails = cur_fails + 1 WHERE email = '+'"'+jobs[0]+'"')
                                # See if the number of current fails has broken the fails threshold
                                cur_fails = db.query("SELECT cur_fails FROM users")
                                fails = db.query("SELECT fails FROM users")
                                if cur_fails == fails:
                                    # Check if message threshold has been broken
                                    cur_notif = db.query("SELECT cur_notify FROM users")
                                    notif = db.query("SELECT notify FROM users")
                                    if cur_notif < notif:
                                        # Send message
                                        mail = contact.Email(jobs[0], message)
                                        print "EMAIL SENT"
                                        # mail.send()
                                        db.update('UPDATE users SET cur_notify = cur_notify + 1 WHERE email ='+'"'+jobs[0]+'"')
                            else:
                                print 'no'
            # Job ran successfully.
            else:
                db.insert_values(current,
                                 "('"+str(now)+"',"+str(ret)+",'"+out[0]+"')")

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
