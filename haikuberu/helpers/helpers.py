"""
    dogetipbot is a bot that lets you tip dogecoins on the internets
    Copyright (C) 2014-2017 Wow Such Business, Inc. and other contributors
    Portions of this software were derived from ALTcointip by Dmitriy Vi - https://github.com/vindimy/altcointip

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from iron_mq import *
from sqlalchemy import *
import json
import os
import sys
import logging
import re
import time
from decimal import *
import yaml





def parse_to_mysql(message):
    '''takes a msg, grabs the service and command type, and produces the correct mysql insert'''

    if message is None or message == '':
        logging.warning('helpers::parse_to_mysql: No message passed or message is none')
        return None

    if message['service'] is None or '':
        logging.warning('helpers::parse_to_mysql: No service type sent')
        return None

    if message['type'] is None or '':
        logging.warning('helpers::parse_to_mysql: No type sent')
        return None

    logging.info('*****************WE GOT A TIP*****************')
    if message['type'] == 'tip':
        logging.info('*****************TIP FROM REDDIT*****************')
        if message['service'] == 'reddit':

            #get user ids
            to_user = get_user_id('reddit', message['to_user'])
            logging.debug('> helpers::parse_to_mysql() TIP: TO USER ID: %s', to_user)

            from_user = get_user_id('reddit', message['from_user'])
            logging.debug('> helpers::parse_to_mysql() TIP: FROM USER ID: %s', from_user)
