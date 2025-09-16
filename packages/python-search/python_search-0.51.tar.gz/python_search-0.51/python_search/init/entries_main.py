#!/usr/bin/env python3

import datetime
import os

from python_search.configuration.configuration import PythonSearchConfiguration
from python_search.official_entries.entries import OfficialEntries

"""
This is a initial version of python_search _entries to give you a sense of what is possible.
Feel free to delete all the _entries here. You will want to versionate your _entries
"""

entries = {
    # NEW_ENTRIES_HERE
    "python search open search ui": {
        "cmd": "python_search_search run",
        "xfce_shortcut": "<Control>space",
        "mac_shortcuts": ["⌥Space"],
    },
    "register new entry ui": {
        # cmd scripts will be executed in a terminal in the background
        "cmd": "python_search register_new from_clipboard",
        "xfce_shortcut": "<Control>r",
        "mac_shortcuts": ["⌥R"],
    },
    # cli cmds will additional open a new terminal window and execute the  command
    "edit current project _entries source code": {
        "cli_cmd": "python_search edit_main",
    },
    # snippets copy  the content of the snippet to the clipboard when executed
    "date current today now copy": {
        "snippet": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    },
    # file will open the file with the standard file handler for the file type in the system
    "edit current selected project _configuration of python search": {
        # you can have multiple projects in paralel with python search
        "file": f"{os.environ['HOME']}/.config/python_search/current_project",
    },
    "get python help function on object": {
        # pythons search is shipped with a multiplataform UI
        # that collects_input to questions and returns the string answered
        "cli_cmd": 'python3 -c "help($(collect_input giveTheObjectName))" '
    },
    # example with shortcuts
    "gmail application": {
        "url": "https://mail.google.com/",
        "mac_shortcuts": ["⌥M"],
        "xfce_shortcut": "<Super>m",
    },
    # _entries are python code, you can import them from other python scripts
    # or you can generate them dynamically like in the example below
    # here we are generating different _entries for different environments (production, testing, development)
    "help python search manual": {"cli_cmd": "python_search --help"},
    **{
        f"get pods for {env}": {"cli_cmd": f"kubectl --context {env} get pods"}
        for env in ["production", "testing", "development"]
    },
}


config = PythonSearchConfiguration(entries=entries, entries_groups=[OfficialEntries])
