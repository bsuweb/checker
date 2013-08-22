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
            db.make(current, ' (datetime TEXT, exit_code INTEGER, value TEXT, fails INTEGER)')
            out = out[0].splitlines()
            if ret > 0:
                # Something went wrong with the current job.
                # value is information to be saved in the database.
                # message is the information to be sent in the email.
                value = out[0]
                message = out[1]
                # Get the number of fails for the current job, and increment
                try:
                    cur_fails = db.query("SELECT fails FROM "+current)[-1][0] + 1
                    print cur_fails
                except IndexError:
                    cur_fails = 1
                    print "INDEX ERROR : " + str(cur_fails)
                # Add new entry to the current job table containing the time,
                # exit code, value, and current number of fails. 
                db.insert_values(current, "('"+str(now)+"',"+str(ret)+",'"+value+"',"+str(cur_fails)+")")
                # Check to see if anyone needs to be notified of the failure.
                users = db.query("SELECT email, checks FROM users")
                for user in users:
                    email = user[0]
                    jobs = user[1]
                    for x in glob.glob(jobs):
                        if job in abspath(join(getcwd(), x)):
                            max_fails = db.query("SELECT fails FROM users WHERE email ="+"'"+email+"'")[0][0]
                            cur_notify = db.query("SELECT cur_notify FROM users WHERE email ="+"'"+email+"'")[0][0]
                            max_notify = db.query("SELECT notify FROM users WHERE email ="+"'"+email+"'")[0][0]
                            print "MAXFAILS: "+str(max_fails)
                            print "CURNOT: "+str(cur_notify)
                            print "MAXNOT: "+str(max_notify)
                            if cur_fails >= max_fails and cur_notify <= max_notify:
                                # Send Message
                                # mail = contact.Email(email, message)
                                # mail.send()
                                print "Current Fails: " + str(cur_fails) + " Max Fails: " + str(max_fails)
                                # Update number of notifications user has been sent
                                db.update('UPDATE users SET cur_notify = cur_notify + 1 WHERE email ='+'"'+email+'"')
                                print "Current Notifications: " + str(cur_notify) + " Max Notifications: " + str(max_notify)
            # Job ran successfully.
            else:
                print "No Errors"
                db.insert_values(current, "('"+str(now)+"',"+str(ret)+",'"+out[0]+"',"+str(0)+")")

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
