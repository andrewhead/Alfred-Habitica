#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import ConfigParser
import slumber
import argparse
import codecs
from requests.auth import AuthBase
import xml.etree.ElementTree as et


logging.basicConfig(level=logging.INFO, format="%(message)s")
CONFIG_FILENAME = 'alfred_habitica.cfg'
TASKS_FILENAME = 'tasks.txt'


class HabiticaAuth(AuthBase):

    def __init__(self, user_id, api_token):
        self.user_id = user_id
        self.api_token = api_token

    def __call__(self, r):
        r.headers['x-api-user'] = self.user_id
        r.headers['x-api-key'] = self.api_token
        return r


# Read in API configuration from local configuration file and initialize global API
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILENAME)
user_id = config.get('auth', 'user_id')
api_token = config.get('auth', 'api_token')
api = slumber.API('https://habitica.com/api/v2', auth=HabiticaAuth(user_id, api_token))


def report_habit(args):
    ''' Report good or bad behavior for a habit. '''
    direction = "up" if args.up else "down"
    api.user.tasks(args.habit)(direction).post()


def refresh_tasks(args):
    ''' Fetch the list of tasks the user has from the API and store them in a local cache. '''
    tasks = api.user.tasks.get()
    with codecs.open(TASKS_FILENAME, 'w', encoding='utf8') as tasks_file:
        for task in tasks:
            tasks_file.write(task['text'] + '\n')


def autocomplete(args):
    ''' Return XML autocomplete items matching a query, for use with Alfred. '''

    # Read tasks from local file
    with codecs.open('tasks.txt', encoding='utf8') as tasks_file:
        task_list = [l.strip() for l in tasks_file.readlines()]

    # Create an autcomplete 'item' for each task matched
    items = et.Element('items')
    for task in task_list:
        if args.query.lower() in task.lower():
            item = et.SubElement(items, 'item', autocomplete=task, arg=task)
            title = et.SubElement(item, 'title')
            title.text = task
            subtitle = et.SubElement(item, 'subtitle')
            subtitle.text = "Upvote this task."
            icon = et.SubElement(item, 'icon')
            icon.text = args.task_type + '.png'

    # Print out the XML
    print et.tostring(items)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Log habit activity.")
    subparsers = parser.add_subparsers(help="sub-commands for interfacing with Habitica")

    report_subparser = subparsers.add_parser('report', help="Report habit behavior")
    report_subparser.add_argument('habit', help="The name of the habit.")
    report_subparser.set_defaults(func=report_habit)
    report_subparser.add_argument(
        '--up',
        action='store_true',
        help="If this is a positive habit (default is false)."
    )

    refresh_subparser = subparsers.add_parser(
        'refresh',
        help="Refresh local list of autocomplete suggestions for tasks."
    )
    refresh_subparser.set_defaults(func=refresh_tasks)

    autocomplete_subparser = subparsers.add_parser(
        'autocomplete',
        help="Get a list of tasks matching the query",
    )
    autocomplete_subparser.set_defaults(func=autocomplete)
    autocomplete_subparser.add_argument(
        'query',
        help="The query for which to suggest autocomplete action."
    )
    autocomplete_subparser.add_argument(
        '--task-type',
        default="good",
        help="The type of task for which to autocomplete tasks (default: %(default)s)",
    )

    # Parser arguments and call the function for the sub-command
    args = parser.parse_args()
    args.func(args)
