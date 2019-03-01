# -*- coding: utf-8 -*-
import sqlite3


class InstancedDatabase(object):
    """ Instanced database handler class. """

    def __init__(self, databasefile):
        self._connection = sqlite3.connect(databasefile, check_same_thread=False)
        self._cursor = self._connection.cursor()

    def execute(self, sqlquery, queryargs=None):
        """ Execute a sql query on the instanced database. """
        if queryargs:
            self._cursor.execute(sqlquery, queryargs)
        else:
            self._cursor.execute(sqlquery)

        return self._cursor

    def commit(self):
        """ Commit any changes of the instanced database. """
        self._connection.commit()

    def close(self):
        """ Close the instanced database connection. """
        self._connection.close()
        return

    def __del__(self):
        """ Close the instanced database connection on destroy. """
        self._connection.close()