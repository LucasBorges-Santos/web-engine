import datetime
import sys
import os
import pathlib
sys.path.insert(0, os.path.join(pathlib.Path().resolve(), pathlib.Path('../../../')))
from source.web_multithread import WebMultithread
import copy

commands = [
    {"get": {"url": "$html_path"}},
    {"print": {"value": "{text(%/html/body/table/tbody/tr[3]/td)} - {text(%/html/body/table/tbody/tr[2]/td)}"}},
    {"print": {"value": "test"}},
    {"print": {"value": "(\d\{6\})"}},
    {"for_each": {
        "elements": "%/html/body/table/tbody/tr",
        "action_commands": [
            {"print": {"value": "{text(this)}"}},
        ]
    }},
    {"download_action": {
        "action_commands": [
            {"click": {"element": "#download_test"}}
        ],
        "file_name": "$file_name",
        "wait_time": "10",
        }
    },
    {"sleep":{"timesec": 5}},
]

contents = [
    {   
        'download_path': r".\download",
        'content_variables':{
            '$teste': '1',
            '$file_name': 'test_file_renamed_1',
            '$html_path': os.path.join(os.getcwd(), 'test_index.html')
        },
        'error_log_name': 'logs.log',
        'commands': copy.deepcopy(commands),
        'show_webdriver': True,
    },
    {   
        'download_path': r".\download",
        'content_variables':{
            '$teste': '2',
            '$file_name': 'test_file_renamed_2',
            '$html_path': os.path.join(os.getcwd(), 'test_index.html')
        },
        'error_log_name': 'logs.log',
        'commands': copy.deepcopy(commands),
        'show_webdriver': True,
    }
]

web_automation = WebMultithread(contents)
web_automation.execute_all_contents()
