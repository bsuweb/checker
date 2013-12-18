#!/usr/bin/env python
import argparse
import yaml
import sys
import subprocess
import sqlite3
# import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from ast import literal_eval
from time import clock
from os import walk, X_OK, access, getcwd
from os.path import basename, splitext, isdir, isfile, realpath, relpath, abspath, join, commonprefix

class Email:
    def __init__(self, emails, message):
        self.emails = emails
        self.message = message
        self.subject = "Subject"
        self.sender = "bsuchecker@..."

    def send(self):
        msg = MIMEText(self.message)
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ','.join(self.emails)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(USER, PASSWORD)
        s.sendmail(self.sender, self.emails, msg.as_string())
        s.close()


class Checker:

    def __init__(self, path, config_file='config.yaml'):
        if not isdir(path):
            sys.exit(1)
        file = open(config_file)
        config = yaml.safe_load(file)
        file.close()
        self.setConfigValues(config)
        self.path = realpath(path)
        self.jobs = self.getExecutableFiles(self.path)

    def setConfigValues(self, config):
        # Test config
        self.threshold = config["threshold"]
        self.max_alerts = config["max_alerts"]
        self.keep_logs = config["keep_logs"]
        self.log_db_path = config["log_db_path"]
        self.users = config["users"]

    def getExecutableFiles(self, path):
        files = []
        for dirname, dirnames, filenames in walk(path):
            for filename in filenames:
                filename_path = join(dirname, filename)
                if access(filename_path, X_OK):
                    files.append(filename_path)
        return files

    def createDatabase(self):
        conn = sqlite3.connect(self.log_db_path)
        conn.close()

    def updateDatabase(self, job, values):
        conn = sqlite3.connect(self.log_db_path)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS ' + job + ' (datetime text, exit_code integer, value text, alert integer, runtime integer)')
        for item in values:
            c.execute('INSERT INTO ' + job + ' VALUES (?, ?, ?, ?, ?)', item)
        conn.commit()
        conn.close()

    def getRows(self, job, num):
        conn = sqlite3.connect(self.log_db_path)
        c = conn.cursor()
        c.execute('SELECT alert FROM ' + job + ' ASC limit ' + str(num))
        vals = c.fetchall()
        conn.commit()
        conn.close()
        return vals

    def run(self):
        # Create DB if it does not exist
        if not isfile(self.log_db_path):
            self.createDatabase()

        for job in self.jobs:
            start = clock()
            cur_job = (splitext(relpath(job))[0]).replace('/', '_')
            cur_time = datetime.now()
            process = subprocess.Popen(job, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=True)

            out = process.communicate()[0]
            exit_code = process.wait()
            try:
                json_dict = literal_eval(out)
                try:
                    # JSON
                    json_dict['data-type']
                    val = json_dict

                except TypeError:
                    # BOOLEAN
                    val = literal_eval(out)

            except SyntaxError:
                # NOT JSON OR BOOLEAN
                val = out

            if isinstance(val, dict):
                # JSON DICT SUCCESS
                if exit_code == 0 and val['alert'] == 0:
                    rename_var = val

                # JSON DICT FAIL
                elif exit_code == 0 and val['alert'] == 1:
                    rename_var = val

            elif isinstance(val, bool):
                # BOOLEAN SUCCESS
                if val == True:
                    rename_var = {"data-type": "INTEGER", "value": 1, "alert": 0}
                # BOOLEAN FAIL
                else:
                    rename_var = {"data-type": "INTEGER", "value": 0, "alert": 1}
            else:
                # TEXT RETURN
                rename_var = {"data-type": "TEXT", "value": "Python Error", "alert": 1}

            elapsed = (clock() - start)
            self.updateDatabase(cur_job, [(cur_time, exit_code, rename_var["value"], rename_var["alert"], elapsed)])

    def alerts(self):
        # For each job, get the last x rows from it's table
        # if the number of rows where alert == true is from the fail threshold
        # through the fail threshold + the max number of alerts, add this job to
        # the jobs that will send a notification
        latestJobVals = []
        for job in self.jobs:
            print job
            cur_job = (splitext(relpath(job))[0]).replace('/', '_')
            num = self.threshold + self.max_alerts
            latestJobVals = self.getRows(cur_job, num)
            for i in reversed(range(len(latestJobVals))):
                if latestJobVals[i][0] == 1:
                    # job failed, alert
                    continue
                else:
                    continue
                print i
                print latestJobVals[i][0]
            # for item in reversed(latestJobVals):
            #     if item[0] == 1:
            #         # alert
            #         print job
            #         print(latestJobVals)
            #     else:
            #         # no alert
            #         break

    # def sendNotifications():
    #     continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A script that runs all the jobs in the given directory"
                    " and keeps track of responses in an sqlite database.")
    parser.add_argument('path', metavar='jobs-directory', type=str, nargs=1,
                        help='Path to the directory where jobs are located.')
    parser.add_argument('-c', '--config')
    args = parser.parse_args()

    # Initialize and run the checker
    if args.config is not None:
        check = Checker(args.path[0], args.config)
    else:
        check = Checker(args.path[0])

    check.run()
    check.alerts()