# Checker

This script executes all the executable files in a directory and stores their return values in a respective table in an automatically-generated and maintained SQLite database. The checker could be run every minute to keep a tab on what web services are up or anything else that you might like to check often.

The checker is agnostic about the contents of the checking scripts themselves. It simply expects them to be executable (and won't attempt to run them if not), and that they use exit codes meaningfully (non zero for an error), and return either a boolean (0 or 1) or a JSON object with three properties: `data-type`, `value`, `alert`.

## Running the checker

Here's an example of running the tests checks included in the repository

	./checker.py tests

## Alerts

If any of the scripts fail (by returning a non-zero exit code), or return a `0`, or return a JSON object where the `alert` property is set to `1`, then the checker will attempt to send out alerts. Email addresses of those to be alerted are stored each on a separate line in a file named `contacts.txt` found in the directory containing the checks. If contact should only receive alerts about certain jobs, enter a space-separated list of the job(s) they should be alerted about.

## Details

Database is created(checker_log.sqlite) when the first job is ran, if it doesn't exist already.

Users, their emails, and the jobs they should be alerted about are also stored in this database in the users table.
Because of this, you should create the database, and this table prior to running. The users table looks like:

	`users (user TEXT, email TEXT, jobs TEXT);`

Whenever a job is run, the checker creates/accesses a table with the same name as the current job (job.rb => job).
	
	`job_name (datetime TEXT, exit_code TEXT, value TEXT);`
	
The value field holds whatever information a job is supposed to return.

When a job runs, it returns information to the checker using STDOUT (print in python, puts in ruby for example).

If a job fails, it should return an exit code of 1. This tells the checker something went wrong with the job, and that the appropriate users should be contacted.
