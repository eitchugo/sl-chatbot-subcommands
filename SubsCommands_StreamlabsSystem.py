#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Allow subs to create commands."""

# system libraries
import os
import sys
import re
import time

# application libraries
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from database import InstancedDatabase  # noqa: E402
from settings import MySettings  # noqa: E402
from localization import MyLocale  # noqa: E402

# [Required] Script Information
ScriptName = 'Subs Commands'
Website = 'https://twitch.tv/eitch'
Description = 'Allow subs to create commands.'
Creator = 'Eitch'
Version = '0.6.2'

# Define Global Variables
database_file = os.path.join(os.path.dirname(__file__), 'SubsCommands.db')
config_file = os.path.join(os.path.dirname(__file__), 'settings.json')
locale_dir = os.path.join(os.path.dirname(__file__), 'locale')


def Init():
    """ [Required] Initialize Data (Only called on load) """

    # database initialization
    global db
    db = InstancedDatabase(database_file)

    # Create db file if not exists
    db.execute('CREATE TABLE IF NOT EXISTS `commands` ('
               '`id` INTEGER PRIMARY KEY,'
               '`name` TEXT UNIQUE,'
               '`timestamp` INTEGER,'
               '`count` INTEGER,'
               '`creator` TEXT,'
               '`text` TEXT)'
               )

    db.commit()

    # settings initialization
    global settings
    settings = MySettings(config_file)
    settings.save()

    # locale initialization
    global locale
    locale = MyLocale(os.path.join(locale_dir, settings.locale) + '.json')

    return


def Execute(data):
    """ [Required] Execute Data / Process messages """

    prefix = settings.prefix
    cooldown = settings.cooldown
    command = None

    if data.IsChatMessage() and re.search(r"^%s" % prefix, data.Message) and not data.IsWhisper():
        user = data.User
        request = data.GetParam(0).lower()
        request = re.sub(r'[^a-z0-9]', '', request)

        if data.GetParamCount() > 1:
            command = re.sub(r"^%s" % prefix, '', data.GetParam(1)).lower()
            command = re.sub(r'[^a-z0-9]', '', command)

        # command creation
        if request == 'add' and (Parent.HasPermission(user, 'Subscriber', '')
                                 or Parent.HasPermission(user, 'Moderator', '')):
            # not enough parameters
            if data.GetParamCount() < 3:
                Parent.SendStreamMessage(locale.add_help % prefix)
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
                db.execute("INSERT INTO `commands`(`name`, `timestamp`, `count`, `creator`, `text`) VALUES (?,?,?,?,?)",
                           new_entry)
                db.commit()
                Parent.SendStreamMessage(locale.add_done % (prefix, command))
                return
            else:
                # command already exists
                Parent.SendStreamMessage(locale.add_exists % (prefix, command, sql_row[0]))
                return

        elif request == "edit" and (Parent.HasPermission(user, "Subscriber", "") or
                                    Parent.HasPermission(user, "Moderator", "")):
            # not enough parameters
            if data.GetParamCount() < 3:
                Parent.SendStreamMessage(locale.edit_help % prefix)
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
                    Parent.SendStreamMessage(locale.edit_done % (prefix, command))
                    return
                else:
                    Parent.SendStreamMessage(locale.edit_denied % (prefix, command))
                    return
            else:
                # command doesn't exist
                Parent.SendStreamMessage(locale.notfound % (prefix, command))
                return

        # command stat
        elif request == "stat" and Parent.HasPermission(user, "Everyone", ""):
            # not enough parameters
            if data.GetParamCount() < 2:
                Parent.SendStreamMessage(locale.stat_help % prefix)
                return

            sql_row = db.execute("SELECT creator,count FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                Parent.SendStreamMessage(locale.stat_done % (prefix, command, sql_row[0], sql_row[1]))
                return
            else:
                Parent.SendStreamMessage(locale.notfound % (prefix, command))
                return

        # command del
        elif request == "del" and Parent.HasPermission(user, "Caster", "Caster"):
            # not enough parameters
            if data.GetParamCount() < 2:
                Parent.SendStreamMessage(locale.del_help % prefix)
                return

            sql_row = db.execute("SELECT id FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                db.execute("DELETE FROM `commands` WHERE `id` = ?", (sql_row[0],))
                db.commit()
                Parent.SendStreamMessage(locale.del_done % (prefix, command))
                return
            else:
                Parent.SendStreamMessage(locale.notfound % (prefix, command))
                return

        # display commands
        else:
            command = re.sub(r"^%s" % prefix, '', request)
            # if exists, generate touser reply variable
            if data.GetParamCount() > 1:
                touser = data.GetParam(1)
            else:
                touser = user

            sql_row = db.execute("SELECT id,count,text FROM `commands` WHERE `name` = ?", (command,)).fetchone()
            if sql_row is not None:
                # command is on cooldown, doing nothing
                if Parent.IsOnCooldown(ScriptName, prefix + command):
                    return

                Parent.AddCooldown(ScriptName, prefix + command, cooldown)

                # increment counter
                count = int(sql_row[1]) + 1
                db.execute("UPDATE `commands` SET `count` = ? WHERE `id` = ?", (count, sql_row[0]))
                db.commit()

                # reply
                reply = sql_row[2]
                reply = re.sub(r"\$\(count\)", str(count), reply)
                reply = re.sub(r"\$\(user\)", str(user), reply)
                reply = re.sub(r"\$\(touser\)", str(touser), reply)
                Parent.SendStreamMessage(reply)
                return

    return


def Tick():
    """ [Required] Tick method (Gets called during every iteration even when there is no incoming data) """
    return


def ReloadSettings(json_data):
    """ [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI) """
    settings.reload(json_data)
    settings.save()
    locale.reload(os.path.join(locale_dir, settings.locale) + '.json')
    return


def Unload():
    """ [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff) """
    db.close()
    return


def ScriptToggled(state):
    """ [Optional] ScriptToggled (Notifies you when a user disables your script or enables it) """
    return
