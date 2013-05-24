import sqlite3
import argparse


class Data:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()

    def commit(self, sql):
        self.c.execute(sql)
        self.conn.commit()

    def make(self, table, values):
        sql = 'CREATE TABLE if not exists ' + table + values
        self.commit(sql)

# Dont Need
# Replace with one function that takes string of sql and runs it
    def insert_values(self, table, values):
        sql = 'INSERT INTO ' + table + ' VALUES ' + values
        self.commit(sql)

    def update(self, sql):
        self.commit(sql)

    def query(self, sql):
        self.c.execute(sql)
        return self.c.fetchall()

    def query_like(self, table, column, value):
        self.c.execute('SELECT * FROM ' + table + ' WHERE ' + column + ' like ?', ['%'+value+'%'])
        return self.c.fetchall()
# Dont Need

    def __del__(self):
        self.c.close()
        self.conn.close()

# May be unnecessary.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Creates the checker database if it does not exist."
                    "Creates the given tables.")
    parser.add_argument('db', type=str, nargs=1,
                        help="Name of the database being created/used.")
    parser.add_argument('tblname', type=str, nargs=1,
                        help="The name of the table to be created.")
    parser.add_argument('values', type=str, nargs=1,
                        help="The columns for the given table.")
    args = parser.parse_args()
    db = Data(args.db[0])
    db.make(args.tblname[0], args.values[0])
