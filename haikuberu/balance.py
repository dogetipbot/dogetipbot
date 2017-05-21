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
import subprocess
from sqlalchemy import *
from helpers import misc, coin
import time
import os
import sys
import yaml
import re
from decimal import *

class Balance(object):

    conf = None
    db = None
    coin = None

    def parse_config(self):
        conf = {}
        try:
            prefix = './conf/'
            for i in ['coins', 'db', 'exchanges', 'fiat', 'logs', 'misc', 'queue', 'service']:
                conf[i] = yaml.load(open(prefix + i + '.yml'))
        except yaml.YAMLError as e:
            print e
            
        self.conf = misc.DotDict(conf)

        return self



    def connect_db(self):
        conn = None
        dsn = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8" % (
        self.conf.db[os.environ.get('HK_ENV', 'test')].user, self.conf.db[os.environ.get('HK_ENV', 'test')].password, self.conf.db[os.environ.get('HK_ENV', 'test')].host, self.conf.db[os.environ.get('HK_ENV', 'test')].port,
        self.conf.db[os.environ.get('HK_ENV', 'test')].dbname)
        dbobj = create_engine(dsn, pool_size=5, max_overflow=0, pool_recycle=30)
        try:
            conn = dbobj.connect()
        except Exception as e:
            print e
        
        self.db = conn
        
        return self



    def connect_dogecoind(self):
        self.coin = coin.HaikuberuCoin(self.conf.coins['dog'])
        
        return self


    
    def save_balance(self):
        cmd = self.coin.getinfo()
        self.db.execute("INSERT INTO wallet_balance SET amount = %s", (cmd['balance']))



    def main(self):
        self.parse_config()
        self.connect_db()
        self.connect_dogecoind()
        

        
        while (True):
            self.save_balance()
            print "Inserted balance"
            time.sleep(3600)


balance = Balance()
balance.main()


