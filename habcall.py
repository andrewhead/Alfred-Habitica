#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import ConfigParser
import os.path
import slumber
import argparse
from requests.auth import AuthBase


logging.basicConfig(level=logging.INFO, format="%(message)s")
config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.expanduser('~'), '.habitica.cfg'))
user_id = config.get('auth', 'user_id')
api_token = config.get('auth', 'api_token')


class HabiticaAuth(AuthBase):

    def __init__(self, user_id, api_token):
        self.user_id = user_id
        self.api_token = api_token

    def __call__(self, r):
        r.headers['x-api-user'] = self.user_id
        r.headers['x-api-key'] = self.api_token
        return r


def report_habit(habit_name, up):
    api = slumber.API('https://habitica.com/api/v2', auth=HabiticaAuth(user_id, api_token))
    direction = "up" if up else "down"
    api.user.tasks(habit_name)(direction).post()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Log habit activity.")
    parser.add_argument('habit', help="The name of the habit.")
    parser.add_argument('--up', action='store_true', help="If this is a positive habit")
    args = parser.parse_args()
    report_habit(args.habit, args.up)
