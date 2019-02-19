# StreamLabs Chatbot Script - Subs Commands

Script for Streamlabs Chatbot to allow users to create/edit their own commands.

# Installation and use

On Streamlabs Chatbot interface, go to `Scripts` and on the top right icons,
click on the `Import` button and chose the zip file containing this
repository. This will install the script itself.

Since it does not contain configuration, it will be working right out of
the box.

To add commands, simply type in your chat:

```
!add command text
```

The `add` command can only be used by subscribers, moderators and caster.

After adding the command, anyone can invoke it just by typing in your chat:

```
!command
```

To edit a command:

```
!edit command new text
```

The `edit` command can only be used by the command creator, the moderators or
the caster.

To delete a command:

```
!del command
```

The `del` command can only be used by the caster.

To view stats about a command:

```
!stat command
```

This will show who created the command and how many times it was used.

# Variables

The following variables can be used on the commands' texts. The script will 
replace the variable with their corresponding replacement:

| Variable |              Replacement             |
|:--------:|:------------------------------------:|
| $(count) | How many times the command was used. |
| $(user)  | Which used just used the command.    |

# Database

The script uses SQLite python library to create a local database file containing
all the commands and stats associated with them. The database file location
is the same as the script itself. For example:

* C:\Users\<USER>\AppData\Roaming\Streamlabs\Streamlabs Chatbot\Services\Scripts\SubsCommands

Where `<USER>` is your local user. All databases used by this script will have
the `.db` extension.

**REMEMBER**: Backup your database files periodically. If you have any loss or
corruption on the file, you won't lose anything!

# Change Log

## 0.5.0

* Initial public release
* Raw functionality to add/edit/remove commands without configuration

# Author

* Hugo Cisneiros (Eitch)
* Website: https://twitch.tv/eitch