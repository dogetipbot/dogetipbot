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
from helpers import user, db, logger, misc, action, exchange, coin
from iron_mq import *
from iron_cache import *
from sqlalchemy import *
from email.mime.text import MIMEText
from math import trunc
import json
import os
import sys
import logging
import re
import time
from decimal import *
import yaml
import traceback
import smtplib
import random
import requests


# logzlogzlogz
logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger('haikuberu')


class Haikuberu(object):
    '''
    Bro its the Haikuberu Obj
    '''

    conf = None
    db = None
    cache = None
    queue = None
    ironmq_in = None
    ironmq_out = None
    coins = {}
    exchanges = {}
    runtime = {'ev': {}, 'regex': []}


    def init_logging(self):
        """
        Initialize logging handlers
        """

        handlers = {}
        levels = ['warning', 'info', 'debug']
        lg = logging.getLogger('haikuberu')

        # Get handlers
        handlers = {}
        for l in levels:
            if self.conf.logs.levels[l].enabled:
                handlers[l] = logging.FileHandler(self.conf.logs.levels[l].filename, mode='a' if self.conf.logs.levels[l].append else 'w')
                handlers[l].setFormatter(logging.Formatter(self.conf.logs.levels[l].format))

        # Set handlers
        for l in levels:
            if handlers.has_key(l):
                level = logging.WARNING if l == 'warning' else (logging.INFO if l == 'info' else logging.DEBUG)
                handlers[l].addFilter(logger.LevelFilter(level))
                lg.addHandler(handlers[l])

        # Set default levels
        lg.setLevel(logging.DEBUG)
        lg.info('Haikuberu::init_logging(): -------------------- logging initialized --------------------')
        return True



    def parse_config(self):
        """
        Returns a Python object with Haikuberu configuration
        """
        lg.debug('Haikuberu::parse_config(): parsing config files...')

        conf = {}
        try:
            prefix = './conf/'
            for i in ['coins', 'db', 'exchanges', 'fiat', 'logs', 'misc', 'queue', 'service']:
                lg.debug("Haikuberu::parse_config(): reading %s%s.yml", prefix, i)
                conf[i] = yaml.load(open(prefix + i + '.yml'))
        except yaml.YAMLError as e:
            lg.error("Haikuberu::parse_config(): error reading config file: %s", e)
            if hasattr(e, 'problem_mark'):
                lg.error("Haikuberu::parse_config(): error position: (line %s, column %s)", e.problem_mark.line + 1,
                         e.problem_mark.column + 1)
            sys.exit(1)

        lg.info('Haikuberu::parse_config(): config files has been parsed')
        return misc.DotDict(conf)



    def connect_db(self):
        """
        Returns a database connection object
        """
        lg.debug('Haikuberu::connect_db(): connecting to database...')

        dsn = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8" % (
        self.conf.db[os.environ.get('HK_ENV', 'test')].user, self.conf.db[os.environ.get('HK_ENV', 'test')].password, self.conf.db[os.environ.get('HK_ENV', 'test')].host, self.conf.db[os.environ.get('HK_ENV', 'test')].port,
        self.conf.db[os.environ.get('HK_ENV', 'test')].dbname)
        dbobj = create_engine(dsn)

        try:
            conn = dbobj.connect()
        except Exception as e:
            lg.error("CointipBot::connect_db(): error connecting to database: %s", e)
            sys.exit(1)

        lg.info("CointipBot::connect_db(): connected to database %s as %s", self.conf.db[os.environ.get('HK_ENV', 'test')].dbname, self.conf.db[os.environ.get('HK_ENV', 'test')].user)
        return conn



    def connect_ironmq(self):
        """
        Returns an IronMQ connection object
        """
        lg.debug('Haikuberu::connect_ironmq(): connecting to queue...')
        
        # Connection info
        conn = IronMQ(
            project_id = self.conf.queue[os.environ.get('HK_ENV', 'test')].project,
            token = self.conf.queue[os.environ.get('HK_ENV', 'test')].token,
            host = self.conf.queue[os.environ.get('HK_ENV', 'test')].host
        )
        
        # Connect to in and out queue
        self.ironmq_in = conn.queue(self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_in)
        
        print self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_out.reddit
        self.ironmq_out = dict()
        self.ironmq_out['reddit'] = conn.queue(self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_out.reddit)
        self.ironmq_out['twitch'] = conn.queue(self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_out.twitch)
        self.ironmq_out['twitter'] = conn.queue(self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_out.twitter)
        #self.ironmq_out['disqus'] = conn.queue(self.conf.queue[os.environ.get('HK_ENV', 'test')].queue_out.disqus)
        
        # Done
        return True



    def check_addresses(self):
        lg.debug('> dogetipbot::check_addresses() %s')
        results = None
        results = self.db.execute("SELECT address_id, username, username.user_id FROM address JOIN username ON username.user_id = address.user_id WHERE address IS NULL AND wallet_name IS NULL GROUP BY address_id")
        for mysqlrow in results:

            # Insert address
            wallet_name = mysqlrow['username'] + ':' + str(mysqlrow['user_id'])
            
            # Generate address
            new_address = self.coins['dog'].getnewaddr(_user=wallet_name)
            
            # Update address record
            self.db.execute("UPDATE address SET address = %s, wallet_name = %s WHERE address_id = %s AND address IS NULL", (new_address, wallet_name, mysqlrow['address_id']))
            
            # Debug
            lg.debug('> dogetipbot::check_addresses() UPDATED address ID %s', mysqlrow['address_id'])
        lg.debug('dogetipbot::check_addresses() done %s', results.rowcount)
        self.db.invalidate()
        return self



    def check_deposits(self):
        self.db.invalidate()
        lg.debug('> dogetipbot::check_deposits()')
        sql = "SELECT * FROM unprocessed ORDER BY created_time ASC LIMIT 10000"
        for mysqlrow in self.db.execute(sql):
            lg.debug('Checking txid: %s', mysqlrow['txid'])
            txinfo = self.coins['dog'].conn.gettransaction(mysqlrow['txid'])
            if txinfo['confirmations'] >= 6:
                if (txinfo['details'][0]['category'] == 'receive') or (txinfo['details'][0]['category'] == 'generate'):
                    mytime = txinfo['timereceived']
                    myconfirmations = txinfo['confirmations']
                    myamount = None
                    myaccount = None
                    myaddress = None
                    myint = 1
                    for detail in txinfo['details']:
                        for k, v in detail.iteritems():
                            if k == "amount":
                                myamount = v
                            if k == "account":
                                myaccount = v
                            if k == "address":
                                myaddress = v
                        lg.debug('SUCCESS : found a deposit of %s to %s with %s confirmations',myamount,myaccount,myconfirmations)

                        # Notify from dogecoind will send the same txid multiple times, do not deposit more than once per txid
                        check_txid = self.get_row("SELECT action_id FROM action WHERE type = 'deposit' AND to_addr = '"+myaddress+"' AND txid = '" + mysqlrow['txid'] + "' LIMIT 1 ")
                        if(myaccount != None and check_txid == None):
                            
                            # Retarded wallet name logic
                            user_wallet = self.get_row("SELECT username.username, service.service_name, service.service_id FROM address JOIN username ON username.user_id = address.user_id JOIN service ON service.service_id = username.service_id WHERE address.address = '" + myaddress + "' LIMIT 1")
                            if user_wallet == None:
                                user_wallet = self.get_row("SELECT username.username, service.service_name, service.service_id FROM address JOIN username ON username.user_id = address.user_id_alias JOIN service ON service.service_id = username.service_id WHERE address.address = '" + myaddress + "' LIMIT 1") 
                            
                            if user_wallet != None:

                                mymsgid = mysqlrow['txid'] + "-" + str(myint)
                                sql3 = "INSERT INTO action (service_id, type, state, timestamp, from_user, to_addr, coin_val, coin, txid) values (%s, %s, %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s)"
                                self.db.execute(sql3, (user_wallet['service_id'], 'deposit','completed',txinfo['blocktime'], user_wallet['username'], myaddress, myamount, 'dog', mysqlrow['txid']))
                                myint = myint + 1
                                
                                deposit_user = user.HkUser(username = user_wallet['username'], service = user_wallet['service_name'], haikuberu=self) 
                                deposit_user.add_coin(coin='dog', amount=myamount)
                                sql2 = "DELETE FROM unprocessed WHERE txid = '%s'" % (mysqlrow['txid'])
                                self.db.execute(sql2)
                                
                                action = self.get_row("SELECT * FROM action WHERE txid = '" + mysqlrow['txid'] + "' LIMIT 1 ")
    
                                # Base notification data
                                data = {
                                    'type'          : 'deposit',
                                    'service'       : user_wallet['service_name'],
                                    'command'       : action['type'],
                                    'u_from'        : deposit_user.username,
                                    'addr_from'     : deposit_user.get_addr('dog'),
                                    'config1'       : action['config1'],
                                    'config2'       : action['config2'],
                                    'config3'       : action['config3'],
                                    'config4'       : action['config4'],
                                    'config5'       : action['config5'],
                                    'config6'       : action['config6'],
                                    'config7'       : action['config7'],
                                    'config8'       : action['config8'],
                                    'config9'       : action['config9'],
                                    'config10'      : action['config10'],
                                    'associated'    : deposit_user.get_usernames(),
                                    'total_doge_sent'       : str(deposit_user.total_sent()),
                                    'total_doge_received'   : str(deposit_user.total_received()),
                                    'balance'               : str(deposit_user.get_balance('dog')),
                                    'coinval'               : str(myamount)
                                }
                                self.push_messasge_out(json.dumps(data))
                            else:
                                lg.warning('WARNING: could not find this user info -- look into this shit: %s', mysqlrow['txid'])
                        else:
                            lg.warning('WARNING: txid is odd -- look into this shit: %s', mysqlrow['txid'])
                            sql2 = "DELETE FROM unprocessed WHERE txid = '%s'" % (mysqlrow['txid'])
                            self.db.execute(sql2)
                elif txinfo['details'][0]['category'] == 'send':
                    sql2 = "SELECT * FROM action where txid ='%s'" % (mysqlrow['txid'])
                    myrow = self.db.execute(sql2).fetchone()
                    if myrow == None:
                        lg.debug('WITHDRAWAL CRASH MOST LIKELY: WTF is %s', (mysqlrow['txid']))
                    else:
                        #found transaction
                        txfee = Decimal(abs(txinfo['details'][0]['fee']))

                        myuser  = myrow['from_user']
                        lg.debug('SUCCESS : found a withdrawal from %s of %s with a fee of %s with %s confirmations',myuser, abs(txinfo['details'][0]['amount']),txfee,txinfo['confirmations'])
                        #create CtbUser object for withdraw user and dogetipbot
                        #b=ctb_user.CtbUser(service = 'reddit', name=self.conf.reddit.auth.user.lower(), ctb=self)
                        #b.sub_coin(coin='dog',amount=txfee)
                        sql2 = "UPDATE action set state = 'completed', txfee='%s' WHERE txid = '%s'" % (txfee, mysqlrow['txid'])
                        self.db.execute(sql2)
                        sql2 = "DELETE FROM unprocessed WHERE txid = '%s'" % (mysqlrow['txid'])
                        self.db.execute(sql2)
                else:
                    lg.debug('Found something else what the fuck. Ignoring.');
                    sql2 = "DELETE FROM unprocessed WHERE txid = '%s'" % (mysqlrow['txid'])
                    self.db.execute(sql2)
            else:
                lg.debug('Not enough confirmations yet on txid %s. Only %s out of 6',txinfo['txid'], txinfo['confirmations'])
        lg.debug('> dogetipbot::check_deposits() DONE')



    def accept_pending_tips(self):
        """
        Accept any pending tips for newly registered users
        """
        sql = "SELECT username.username, service.service_name FROM action JOIN username ON username.username = action.to_user JOIN service ON service.service_id = username.service_id WHERE action.service_id = username.service_id AND type = 'givetip' AND state = 'pending' "
        for row in self.db.execute(sql):
            print row
            # Send an accept for this user to claim all pending tips
            request = dict()
            request['body'] = json.dumps({
                "service": row['service_name'],
                "u_from": row['username'],
                "created_utc": time.time(),
                "type": "accept"
            })
            message_obj = action.HkAction(self, request).do()

        # Done
        return True



    def expire_pending_tips(self):
        """
        Decline any pending tips that have reached expiration time limit
        """

        # Calculate timestamp
        seconds = int(self.conf.misc.times.expire_pending_hours * 3600)
        created_before = time.mktime(time.gmtime()) - seconds

        # Get expired actions and decline them
        for a in action.get_actions(command='givetip', state='pending', timestamp= '< DATE_SUB(NOW(), INTERVAL ' + str(self.conf.misc.times.expire_pending_hours) + ' HOUR)', haikuberu=self):
            lg.debug("expire_pending_tips(): well, we're here. now let's expire")
            a.expire()

        # Done
        return True



    def refresh_ev(self):
        """
        Refresh coin/fiat exchange values using self.exchanges
        """

        # Return if rate has been checked in the past hour
        seconds = int(1 * 900)
        if hasattr(self.conf.exchanges, 'last_refresh') and self.conf.exchanges.last_refresh + seconds > int(
                time.mktime(time.gmtime())):
            lg.debug("< Haikuberu::refresh_ev(): DONE (skipping)")
            return

        # For each enabled coin...
        for c in vars(self.conf.coins):
            if self.conf.coins[c].enabled:

                # Get BTC/coin exchange rate
                values = []
                result = 0.0

                if not self.conf.coins[c].unit == 'btc':
                    # For each exchange that supports this coin...
                    for e in self.exchanges:
                        if self.exchanges[e].supports_pair(_name1=self.conf.coins[c].unit, _name2='btc'):
                            # Get ticker value from exchange
                            value = self.exchanges[e].get_ticker_value(_name1=self.conf.coins[c].unit, _name2='btc')
                            if value and float(value) > 0.0:
                                values.append(float(value))

                    # Result is average of all responses
                    if len(values) > 0:
                        result = sum(values) / float(len(values))

                else:
                    # BTC/BTC rate is always 1
                    result = 1.0

                # Assign result to self.runtime['ev']
                if not self.runtime['ev'].has_key(c):
                    self.runtime['ev'][c] = {}
                self.runtime['ev'][c]['btc'] = result

        # For each enabled fiat...
        for f in vars(self.conf.fiat):
            if self.conf.fiat[f].enabled:

                # Get fiat/BTC exchange rate
                values = []
                result = 0.0

                # For each exchange that supports this fiat...
                for e in self.exchanges:
                    if self.exchanges[e].supports_pair(_name1='btc', _name2=self.conf.fiat[f].unit):
                        # Get ticker value from exchange
                        value = self.exchanges[e].get_ticker_value(_name1='btc', _name2=self.conf.fiat[f].unit)
                        if value and float(value) > 0.0:
                            values.append(float(value))

                # Result is average of all responses
                if len(values) > 0:
                    result = sum(values) / float(len(values))

                # Assign result to self.runtime['ev']
                if not self.runtime['ev'].has_key('btc'):
                    self.runtime['ev']['btc'] = {}
                self.runtime['ev']['btc'][f] = result

        lg.debug("Haikuberu::refresh_ev(): %s", self.runtime['ev'])

        # If the value is good, save to db for emergencies
        if self.coin_value('dog', 'usd') > 0:
            # Convert the fiat data to JSON and insert
            sqlcmd = "INSERT INTO fiat (fiat_data) VALUES (%s)"
            sqlinsert = self.db.execute(sqlcmd, json.dumps(self.runtime['ev']))
            lg.debug("Saving fiat to DB: %s", json.dumps(self.runtime['ev']))
        else:
            # Fiat conversion is returning 0, load last good value from DB
            fiat_data = self.get_field("SELECT fiat_data FROM fiat ORDER BY fiat_id DESC LIMIT 1")
            self.runtime['ev'] = json.loads(fiat_data)
            lg.debug("Fiat value is bad, loading from DB: %s", fiat_data)

        # Update last_refresh
        self.conf.exchanges.last_refresh = int(time.mktime(time.gmtime()))
        
        return self



    def coin_value(self, _coin, _fiat):
        """
        Quick method to return _fiat value of _coin
        """
        try:
            value = self.runtime['ev'][_coin]['btc'] * self.runtime['ev']['btc'][_fiat]
        except KeyError as e:
            lg.warning("Haikuberu::coin_value(%s, %s): KeyError", _coin, _fiat)
            value = 0.0
        return Decimal(Decimal(trunc(value * 100000000)) / 100000000)



    def push_messasge_in(self, message):
        if self.ironmq_in:
            return self.ironmq_in.post(message)
        else:
            raise Exception('Haikuberu::push_message_in() ')



    def push_messasge_out(self, message):
        if self.ironmq_out:
            tmp = json.loads(message)
            print "posting message to queue " + tmp.get('service')
            return self.ironmq_out[tmp.get('service')].post(message)
        else:
            raise Exception('Haikuberu::push_message_out() ')



    def delete_messasge(self, message_id, res_id):
        if self.ironmq_in:
            return self.ironmq_in.delete(message_id, res_id)
        else:
            raise Exception('Haikuberu::delete_messasge() ')



    def get_messasges(self):
        if self.ironmq_in:
            return self.ironmq_in.reserve(max=self.conf.queue.scan.batch_limit, timeout=1000)
        else:
            raise Exception('Haikuberu::get_messasges() ')



    def process_queue(self):
        '''process items in the queue'''
        lg.info("Haikuberu::process_queue()...")
        try:
            # Fetch the queue
            lg.debug("Getting all messages in the queue")
            msgs = self.get_messasges()

            lg.debug("Total Messages should be %s", len(msgs))

            for message in msgs['messages']:
                mysqlexec = self.db.execute(text("INSERT INTO message SET message = :msg"), msg = json.dumps(message))
                message_obj = action.HkAction(self, message).do()
        except Exception as e:
            lg.error('Haikuberu::process_queue(): %s', e)
            raise
        lg.debug("< Haikuberu::process_queue() DONE")
        return True



    def get_field(self, sql):
        mysqlexec = self.db.execute(sql).fetchone()
        
        if mysqlexec is None:
            return ''
        else:
            for row in mysqlexec:
                return row



    def get_row(self, sql):
        mysqlexec = self.db.execute(sql).fetchone()
        
        if mysqlexec is None:
            return None
        else:
            return mysqlexec



    def self_checks(self):
        # Reddit check
        b = user.HkUser(self, 'reddit', self.conf.service.reddit.username)
        if not b.is_registered():
            b.register()
        
        # Twitch check
        b = user.HkUser(self, 'twitch', self.conf.service.twitch.username)
        if not b.is_registered():
            b.register()

        # Twitter check
        b = user.HkUser(self, 'twitter', self.conf.service.twitter.username)
        if not b.is_registered():
            b.register()

        # Disqus check
        #b = user.HkUser(self, 'disqus', self.conf.service.disqus.username)
        #if not b.is_registered():
        #    b.register()


    def __init__(self, self_checks=False, init_coins=False, init_exchanges=True, init_db=True, init_logging=True, init_cache=True):
        """
        Constructor. Parses configuration file and initializes bot.
        """
        lg.info("Haikuberu::__init__()...")

        # Configuration
        self.conf = self.parse_config()

        # Logging
        if init_logging:
            self.init_logging()

        # Database
        if init_db:
            self.db = self.connect_db()

        # Coins
        if init_coins or 1 == 1:
            for c in vars(self.conf.coins):
                if self.conf.coins[c].enabled:
                    self.coins[c] = coin.HaikuberuCoin(_conf=self.conf.coins[c])
            if not len(self.coins) > 0:
                lg.error("Haikuberu::__init__(): Error: please enable at least one type of coin")
                sys.exit(1)

        # Exchanges
        if init_exchanges:
            for e in vars(self.conf.exchanges):
                if self.conf.exchanges[e].enabled:
                    self.exchanges[e] = exchange.HkExchange(_conf=self.conf.exchanges[e])
            if not len(self.exchanges) > 0:
                lg.warning("Haikuberu::__init__(): Warning: no exchanges are enabled")

        # Self-checks
        self.self_checks()

        # Connect to IronMQ (self.inronmq_in, self.ironmq_out)
        self.connect_ironmq()
        
        # Debug
        lg.info("< Haikuberu::__init__(): DONE, batch-limit = %s, sleep-seconds = %s", self.conf.queue.scan.batch_limit, self.conf.misc.times.sleep_seconds)


    def __str__(self):
        """
        Return string representation of self
        """
        me = "<Haikuberu: sleepsec=%s, batchlim=%s, ev=%s"
        me = me % (self.conf.misc.times.sleep_seconds, self.conf.queue.scan.batch_limit, self.runtime['ev'])
        return me



    def main(self):
        """
        Main loop
        """
        while (True):
            try:
                # Debug
                lg.debug("Haikuberu::main(): beginning main() iteration")
                
                # Refresh exchange rate values
                self.refresh_ev()
    
                #self.process_queue()
                self.process_queue()

                # Fill in addresses from website created users
                self.check_addresses()

                #self.check_deposits()
                self.check_deposits() 

                # Check pending tips
                self.accept_pending_tips()
                   
                # Expire pending tips
                self.expire_pending_tips()

                # Sleep
                lg.debug("Haikuberu::main(): sleeping for %s seconds...", self.conf.misc.times.sleep_seconds)
                time.sleep(self.conf.misc.times.sleep_seconds)
    
            except Exception as e:
                lg.error("CointipBot::main(): exception: %s", e)
                lg.warning("CointipBot::main(): traceback: %s", e)
                tb = traceback.format_exc()
                lg.error("CointipBot::main(): traceback: %s", tb)
                lg.warning("CointipBot::main(): traceback: %s", tb)
                
                # Send a notification, if enabled
                if self.conf.misc.notify.enabled:
                    self.notify(_msg=tb)
                sys.exit(1)



    def notify(self, _msg = None):
        """
        Send _msg to configured destination
        """

        # Construct MIME message
        msg = MIMEText(_msg)
        msg['Subject'] = self.conf.misc.notify.subject
        msg['From'] = self.conf.misc.notify.addr_from
        msg['To'] = self.conf.misc.notify.addr_to

        # Send MIME message
        server = smtplib.SMTP(self.conf.misc.notify.smtp_host)
        if self.conf.misc.notify.smtp_tls:
            server.starttls()
        server.login(self.conf.misc.notify.smtp_username, self.conf.misc.notify.smtp_password)
        server.sendmail(self.conf.misc.notify.addr_from, self.conf.misc.notify.addr_to, msg.as_string())
        server.quit()



