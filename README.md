# Checker

This script executes all the executable files in a directory and stores their return values in a respective table in an automatically-generated and maintained SQLite database. The checker could be run every minute to keep a tab on what web services are up or anything else that you might like to check often.

The checker is agnostic about the contents of the checking scripts themselves. It simply expects them to be executable (and won't attempt to run them if not), and that they use exit codes meaningfully (non zero for an error), and return either a boolean (0 or 1) or a JSON object with three properties: `data-type`, `value`, `alert`.

## Running the checker

Here's an example of running the tests checks included in the repository

	./checker.py tests



## Alerts

If any of the scripts fail (by returning a non-zero exit code), or return a `0`, or return a JSON object where the `alert` property is set to `1`, then the checker will attempt to send out alerts. Email addresses of those to be alerted are stored each on a separate line in a file named `contacts.txt` found in the directory containing the checks. If contact should only receive alerts about certain jobs, enter a space-separated list of the job(s) they should be alerted about.