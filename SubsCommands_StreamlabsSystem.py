#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Allow subs to create commands."""

# Import Libraries
import os
import sys
import sqlite3
import re
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

# [Required] Script Information
ScriptName = "Subs Commands"
Website = "https://twitch.tv/eitch"
Description = "Allow subs to create commands."
Creator = "Eitch"
Version = "0.5.0"

# Define Global Variables
DatabaseFile = os.path.join(os.path.dirname(__file__), "SubsCommands.db")


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

# [Required] Initialize Data (Only called on load)
# ------------------------------------------------


def Init():
    """ [Required] Initialize Data (Only called on load) """

    global db
    db = InstancedDatabase(DatabaseFile)

    # Create db file if not exists
    db.execute("CREATE TABLE IF NOT EXISTS `commands` ("
               "`id` INTEGER PRIMARY KEY,"
               "`name` TEXT UNIQUE,"
               "`timestamp` INTEGER,"
               "`count` INTEGER,"
               "`creator` TEXT,"
               "`text` TEXT)"
               )

    db.commit()
    return

def Execute(data):
    """ [Required] Execute Data / Process messages """

    if data.IsChatMessage() and re.search(r"^!", data.Message):
        user = data.User
        request = data.GetParam(0).lower()
        request = re.sub(r'[^a-z0-9]', '', request)

        if data.GetParamCount() > 1:
            command = re.sub(r'^!', '', data.GetParam(1)).lower()
            command = re.sub(r'[^a-z0-9]', '', command)

        # command creation
        if request == "add" and (Parent.HasPermission(user, "Subscriber", "") or Parent.HasPermission(user, "Moderator", "")):
            # not enough parameters
            if data.GetParamCount() < 3:
                Parent.SendStreamMessage("Use: !add !comando <mensagem>")
                return

            msg = data.Message
            msg = msg.split(" ")
            msg = msg[2:]
            msg = " ".join(msg)
            msg = msg[:500]

            sql_row = db.execute("SELECT creator FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is None:
                # add new command
                new_entry = (command, time.time(), 0, user, msg)
                db.execute("INSERT INTO `commands`(`name`, `timestamp`, `count`, `creator`, `text`) VALUES (?,?,?,?,?)", new_entry)
                db.commit()
                Parent.SendStreamMessage("Comando !%s adicionado." % command)
                return
            else:
                # command already exists
                Parent.SendStreamMessage("Comando !%s ja existe. Criado por %s." % (command, sql_row[0]))
                return

        elif request == "edit" and (Parent.HasPermission(user, "Subscriber", "") or Parent.HasPermission(user, "Moderator", "")):
            # not enough parameters
            if data.GetParamCount() < 3:
                Parent.SendStreamMessage("Use: !edit !comando <mensagem>")
                return

            msg = data.Message
            msg = msg.split(" ")
            msg = msg[2:]
            msg = " ".join(msg)
            msg = msg[:500]

            sql_row = db.execute("SELECT id,creator FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                # edit command
                if (sql_row[1] == user) or (Parent.HasPermission(user, "Moderator", "")):
                    db.execute("UPDATE `commands` SET `text` = ? WHERE `id` = ?", (msg, sql_row[0]))
                    db.commit()
                    Parent.SendStreamMessage("Comando !%s editado." % command)
                    return
                else:
                    Parent.SendStreamMessage("Você não pode editar !%s." % command)
                    return
            else:
                # command doesn't exist
                Parent.SendStreamMessage("Comando !%s não existe." % command)
                return

        # command stat
        elif request == "stat" and Parent.HasPermission(user, "Everyone", ""):
            # not enough parameters
            if data.GetParamCount() < 2:
                Parent.SendStreamMessage("Use: !stat !comando")
                return

            sql_row = db.execute("SELECT creator,count FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                Parent.SendStreamMessage("Comando !%s criado por %s, usado %s vezes." % (command, sql_row[0], sql_row[1]))
                return
            else:
                Parent.SendStreamMessage("Comando !%s não existe." % command)
                return

        # command del
        elif request == "del" and Parent.HasPermission(user, "Caster", "Caster"):
            # not enough parameters
            if data.GetParamCount() < 2:
                Parent.SendStreamMessage("Use: !del !comando")
                return

            sql_row = db.execute("SELECT id FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                db.execute("DELETE FROM `commands` WHERE `id` = ?", (sql_row[0],))
                db.commit()
                Parent.SendStreamMessage("Comando !%s removido." % command)
                return
            else:
                Parent.SendStreamMessage("Comando !%s não existe." % command)
                return

        # display commands
        else:
            command  = re.sub(r'^!', '', request)
            sql_row = db.execute("SELECT id,count,text FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                # command is on cooldown, doing nothing
                if Parent.IsOnCooldown(ScriptName, "!" + command):
                    return

                Parent.AddCooldown(ScriptName, "!" + command, 10)

                # increment counter
                count = int(sql_row[1]) + 1
                db.execute("UPDATE `commands` SET `count` = ? WHERE `id` = ?", (count, sql_row[0]))
                db.commit()

                # reply
                reply = sql_row[2]
                reply = re.sub(r"\$\(count\)", str(count), reply)
                reply = re.sub(r"\$\(user\)", str(user), reply)
                Parent.SendStreamMessage(reply)
                return

    return


def Tick():
    """ [Required] Tick method (Gets called during every iteration even when there is no incoming data) """
    return


def Unload():
    """ [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff) """
    db.close()
    return


def ScriptToggled(state):
    """ [Optional] ScriptToggled (Notifies you when a user disables your script or enables it) """
    return
