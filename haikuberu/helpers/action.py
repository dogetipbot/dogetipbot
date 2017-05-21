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
from os import urandom
from decimal import *
from math import trunc
import json, os, sys, logging, re, time, yaml, db, misc, datetime, user, hkservice, addressvalidate



lg = logging.getLogger('haikuberu')



class HkAction(object):
    '''
    Action class for haikuberu
    '''
    is_pending = False
    action_id = None
    service = None
    command = None
    state = None
    txid = None

    u_from = None
    u_to = None
    addr_to = None

    coin = None
    fiat = None
    coinval = None
    fiatval = None
    verify = None

    subreddit = None
    channel = None

    msg = {}
    haikuberu = None
    keyword = None
    action_id = None

    deleted_msg_id = None
    deleted_created_utc = None
    
    notification = []

    def __init__(self, haikuberu=None, msg=None, deleted_msg_id = None, deleted_created_utc=None):

        # Debug
        lg.debug("> HkAction::__init__() BEGIN INIT")

        # Make sure message and haikuberu object were passed
        if not bool(msg):
            raise Exception("HkAction::__init__: Message not set, this should never happen")

        if not bool(haikuberu):
            raise Exception("HkAction::__init__: Haikuberu obj not set, this should never happen")
        self.msg = json.loads(msg['body'])
        self.haikuberu = haikuberu

        # Queue ID
        self.queue_id = msg['id'] if 'id' in msg else ''
        self.queue_res_id = msg['reservation_id'] if 'reservation_id' in msg else ''


        # Error
        self.error = ''
        self.state = ''

        # Config variables
        self.config1 = None
        self.config2 = None
        self.config3 = None
        self.config4 = None
        self.config5 = None
        self.config6 = None
        self.config7 = None
        self.config8 = None
        self.config9 = None
        self.config10 = None
        
        # Action ID
        self.action_id = self.msg.get("action_id", None)
        
        # Command / type
        self.service = self.msg['service']
        self.service_id = hkservice.HkService(self.haikuberu).get_from_name(self.service)
        self.command = self.msg['type']
        self.u_from = self.msg['u_from']

        # Currency
        self.coin = 'dog'
        self.fiat = self.msg.get("fiat", None)
        self.coinval = self.msg.get('coin_val', None)
        self.fiatval = self.msg.get("fiatval", None)
        self.fiat = self.msg.get("fiat", None)

        # Reddit specific
        self.msg_id = self.msg.get("msgid", None)
        self.created_utc = self.msg.get("created_utc", None)
        self.verify = self.msg.get("verify", None)
        self.subreddit = self.msg.get('subreddit', None)
        self.fullname = self.msg.get('fullname', None)

        # Twitch specific
        self.channel = self.msg.get("channel", None)

        # Twitter specific
        self.tweet_id = self.msg.get("tweet_id", None)

        # Disqus specific
        self.post_id = self.msg.get("post_id", None)
        self.thread_id = self.msg.get("thread_id", None)

        # Set configuration field values
        if self.service == 'reddit':
            self.config1 = self.msg_id
            self.config2 = self.fullname
            self.config3 = self.subreddit
            self.config4 = self.msg.get("msg_link", None)
            self.config5 = self.msg.get("verify", None)
        elif self.service == 'twitch':
            self.config1 = self.channel
        elif self.service == 'twitter':
            self.config1 = self.tweet_id
        elif self.service == 'disqus':
            self.config1 = self.post_id
            self.config2 = self.thread_id

        # Address
        self.addr_to = self.msg.get("addr_to", None)
        self.u_to = self.msg.get('u_to', None)
        self.u_to_service = self.msg.get('u_to_service', None)

        # To and from user objects
        self.u_to = user.HkUser(haikuberu, self.service, self.u_to) if bool(self.u_to) else None
        self.u_from = user.HkUser(haikuberu, self.service, self.u_from)

        if self.coinval == 'all':
            if self.u_from.is_registered():
                self.coinval = self.u_from.get_balance(self.coin)
            else:
                self.coinval = 0

        # Sanity check
        if not bool(self.service):
            raise Exception("HkAction::__init__: Service not set in message")

        if not bool(self.command):
            raise Exception("HkAction::__init__: Type of command not set in message")

        if not bool(self.u_from):
            raise Exception("HkAction::__init__: u_from not set in message")
        if self.command in ['givetip', 'withdraw']:
            if not (bool(self.u_to) ^ bool(self.addr_to)):
                raise Exception("HkAction::__init__(command=%s): u_to xor addr_to must be set" % (self.command))

        # Convert coinval and fiat to decimal, if necesary
        if self.coinval and type(self.coinval) == unicode and self.coinval.replace('.', '').isnumeric():
            self.coinval = Decimal(self.coinval)
        if self.fiatval and type(self.fiatval) == unicode and self.fiatval.replace('.', '').isnumeric():
            self.fiatval = Decimal(self.fiatval)

        # Truncate precisoin
        if self.coinval:
            self.coinval = Decimal(str(self.coinval).replace(',',''))
            lg.debug("HkAction::init() Converting coinval to decimal %s", self.coinval)
            self.coinval = Decimal(Decimal(trunc(self.coinval * 100000000)) / 100000000)

        lg.debug("< HkAction::__init__() DONE")



    # Clear notifications
    def clear(self):
        del self.notification[:]
        self.notification = []
        return self
    


    # Return string representation of self
    def __str__(self):
        pass
        me = "<HkAction: command=%s, msg=%s, from_user=%s, to_user=%s, to_addr=%s, coin=%s, fiat=%s, coin_val=%s, fiat_val=%s, subr=%s, verify=%s, haikuberu=%s, config1=%s, config2=%s, config3=%s, config4=%s, config5=%s, config6=%s, config7=%s, config8=%s, config9=%s, config10=%s>"
        me = me % (
        self.command, self.msg, self.u_from, self.u_to, self.addr_to, self.coin, self.fiat, self.coinval, self.fiatval,
        self.subreddit, self.verify, self.haikuberu, self.config1, self.config2, self.config3, self.config4, self.config5, self.config6, self.config7, self.config8, self.config9, self.config10)
        return me



    # Save an action to the database
    def save(self, state = None, error = None):
        lg.debug("> HkAction::save(%s)", state)
        
        # set local var for action_id's value needed in saving
        action_id = 0
        
        # Store the error for notifications later
        self.error = error

        # Store the state for notifications later
        self.state = state

        # Make sure no negative values exist
        if self.coinval < 0.0:
            self.coinval = 0.0
        if self.fiatval < 0.0:
            self.fiatval = 0.0
        
        # Start action insert
        sql = "REPLACE INTO action (action_id, type, service_id, state, error, timestamp, from_user, to_user, to_addr, coin_val, fiat_val,coin, fiat, config1, config2, config3, config4, config5, config6, config7, config8, config9, config10, txid)"
        sql += " values (%s, %s, %s, %s, %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        lg.error('> HkAction::save() message: %s ' % sql)

        try:
            mysqlexec = self.haikuberu.db.execute(sql,
                    (self.action_id,
                     self.command,
                     self.service_id,
                     state,
                     error,
                     self.created_utc,
                     self.u_from.username.lower(),
                     self.u_to.username.lower() if self.u_to else None,
                     self.addr_to,
                     self.coinval,
                     self.fiatval,
                     self.coin,
                     self.fiat,
                     self.config1,
                     self.config2,
                     self.config3,
                     self.config4,
                     self.config5,
                     self.config6,
                     self.config7,
                     self.config8,
                     self.config9,
                     self.config10,
                     self.txid))
            if mysqlexec.rowcount <= 0:
                raise Exception("query didn't affect any rows")
            else:
                self.action_id = int(mysqlexec.lastrowid)
                lg.debug("HkAction::save() New Action Id %s", self.action_id)
        except Exception as e:
            lg.error("HkAction::save(%s): error executing query <%s>: %s", state, sql % (
                     self.action_id,
                     self.command,
                     self.service_id,
                     state,
                     error,
                     realutc,
                     self.u_from.username.lower(),
                     self.u_to.username.lower() if self.u_to else None,
                     self.addr_to,
                     self.coinval,
                     self.fiatval,
                     self.coin,
                     self.fiat,
                     self.config1,
                     self.config2,
                     self.config3,
                     self.config4,
                     self.config5,
                     self.config6,
                     self.config7,
                     self.config8,
                     self.config9,
                     self.config10), e)
            raise

        lg.debug("< HkAction::save() DONE")
        return True



    # Call appropriate function depending on action command
    def do(self):
        lg.debug("> HkAction::do() %s", self.command)

        if self.command == 'accept':
            ret = self.accept()
        elif self.command == 'decline':
            ret = self.decline()
        elif self.command == 'givetip':
            ret = self.givetip()
        elif self.command == 'history':
            ret = self.history()
        elif self.command == 'info':
            ret = self.info()
        elif self.command == 'register':
            ret = self.register()
        elif self.command == 'withdraw':
            ret = self.givetip()
        elif self.command == 'gold':
            ret = self.gold()
        else:
            # 'redeem', 'rates', 'deposit', 'link', 'connect'
            lg.info("HkAction::do(): action %s is disabled", self.command)
            return False

        # Remove item from queue
        self.clear_queue()
        
        # Return self otherwise testing becomes a pita
        return self



    # Clear the current item from the message queue
    def clear_queue(self):
        if self.queue_id:
            lg.info("HkAction::clear_queue(): clearing %s from queue.", self.queue_id)
            self.haikuberu.delete_messasge(self.queue_id, self.queue_res_id)
        else:
            lg.info("HkAction::clear_queue(): not from queue... skipping.")
        
        
            
    # History
    def history(self):
        lg.debug("HkAction::history()")

        if not self.u_from.is_registered():
            self.save('failed', 'not_registered')
            return self.error_notification('not_registered')

        self.save('completed')

        # Base notification data
        data = {
            'type'          : 'history',
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'addr_from'     : self.u_from.get_addr('dog'),
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10,
            'associated'    : self.u_from.get_usernames(),
            'history'       : self.u_from.get_history(),
            'total_doge_sent'       : str(self.u_from.total_sent()),
            'total_doge_received'   : str(self.u_from.total_received()),
            'total_fiat_sent'       : str(self.u_from.total_fiat_sent()),
            'total_fiat_received'   : str(self.u_from.total_fiat_received()),
            'balance'               : str(self.u_from.get_balance(self.coin))
        }
        self.haikuberu.push_messasge_out(json.dumps(data))
        self.notification.append(data.copy())

        return self



    # Gold
    def gold(self):
        lg.debug("HkAction::history()")

        if not self.u_from.is_registered():
            self.save('failed', 'not_registered')
            return self.error_notification('not_registered')
        
        # If there is a fiat issue, return
        if self.haikuberu.coin_value('dog', 'usd') <= 0:
            self.save('failed', 'fiat_error')
            self.error_notification('fiat_error')
            return self

        # Calculate the fiat and round to nearest 100
        self.coinval = trunc(4 / self.haikuberu.coin_value('dog', 'usd'))
        self.coinval -= self.coinval % 100
        
        self.fiatval = 4
        
        # Fiat sanity check
        if self.coinval < 10000:
            self.save('failed', 'fiat_error')
            self.error_notification('fiat_error')
            return self

        # Check if u_from has registered
        if not self.u_from.is_registered():
            self.save('failed', 'not_registered')
            self.error_notification('not_registered')
            return self
 
        print self.coinval
 
        # Check u_from balance
        balance_avail = self.u_from.get_balance(coin=self.coin)
        if(balance_avail < self.coinval):
            self.save('failed', 'balance_too_low')
            self.error_notification('balance_too_low')
            return self

        # Move coins
        self.u_from.sub_coin(self.coin, self.coinval)
        reddit_bot = user.HkUser(self.haikuberu, 'reddit', 'dogetipbot')
        reddit_bot.add_coin(self.coin, self.coinval)
        
        self.save('completed')
        
        # Base notification data
        data = {
            'type'          : 'gold_sent',
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'u_to'          : self.u_to.username,
            'addr_from'     : self.u_from.get_addr('dog'),
            'coinval'       : self.coinval,
            'fiatval'       : self.fiatval,
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10,
        }
        self.haikuberu.push_messasge_out(json.dumps(data))
        self.notification.append(data.copy())
        
        if self.u_to and not self.u_to.is_registered():
            data['type'] = 'gold_received'
            self.haikuberu.push_messasge_out(json.dumps(data))
            self.notification.append(data.copy())        

        return self


    # Info
    def info(self):
        lg.debug("HkAction::info()")

        if not self.u_from.is_registered():
            self.save('failed', 'not_registered')
            return self.error_notification('not_registered')

        self.save('completed')

        # Base notification data
        data = {
            'type'          : 'info',
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'addr_from'     : self.u_from.get_addr('dog'),
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10,
            'associated'    : self.u_from.get_usernames(),
            'total_doge_sent'       : str(self.u_from.total_sent()),
            'total_doge_received'   : str(self.u_from.total_received()),
            'total_fiat_sent'       : str(self.u_from.total_fiat_sent()),
            'total_fiat_received'   : str(self.u_from.total_fiat_received()),
            'balance'               : str(self.u_from.get_balance(self.coin))
        }
        self.haikuberu.push_messasge_out(json.dumps(data))
        self.notification.append(data.copy())

        return self



    # Accept pending tips
    def accept(self):
        lg.debug("> HkAction::accept()")

        # Register as new user if necessary
        if not self.u_from.is_registered():
            if not self.u_from.register():
                lg.warning("HkAction::accept(): self.u_from.register() failed")
                self.save('failed')
                return False

        # Get pending actions
        actions = get_actions(service = self.service, command = 'givetip', to_user = self.u_from.username, state = 'pending', haikuberu = self.haikuberu)
        if actions:
            # Accept each action
            for a in actions:
                a.givetip(is_pending=True)

        # Save action to database
        self.save('completed')

        lg.debug("< HkAction::accept() DONE")
        return True



    # Decine pending tips
    def decline(self):
        lg.debug("> HkAction::decline()")

        actions = get_actions(command='givetip', to_user = self.u_from.username, state = 'pending', haikuberu = self.haikuberu)
        if actions:
            for a in actions:
                # Move coins back into a.u_from account
                lg.info("HkAction::decline(): moving %s %s from %s to %s", a.coinval, a.coin.upper(), 'dogetipbot', a.u_from.username)

                # Move coins from dogetipbot back to a.u_from account
                b = user.HkUser(self.haikuberu, 'reddit', 'dogetipbot')
                b.sub_coin(coin=a.coin, amount=a.coinval)
                a.u_from.add_coin(coin=a.coin, amount=a.coinval)

                # Save transaction as declined
                a.save('declined')

        # Save action to database
        self.save('failed')

        lg.debug("< HkAction::decline() DONE")
        return True



    def expire(self):
        """
        Expire a pending tip
        """
        lg.debug("> HkAction::expire()")

        # Move coins back into self.u_from account
        lg.info("HkAction::expire(): moving %s %s from %s to %s", self.coinval, self.coin.upper(), self.haikuberu.conf.service[self.service].username, self.u_from.username)

        # Move coins from dogetipbot back to a.u_from account
        b = user.HkUser(self.haikuberu, self.service, self.haikuberu.conf.service[self.service].username)
        b.sub_coin(coin = self.coin, amount = self.coinval)
        self.u_from.add_coin(coin = self.coin, amount = self.coinval)

        # Save transaction as expired
        self.haikuberu.db.execute("UPDATE action SET state = 'expired' WHERE action_id = %s ", (self.action_id))

        lg.debug("< HkAction::expire() DONE")
        return True



    def validate(self, is_pending=False):
        """
        Validate an action
        """
        lg.debug("> HkAction::validate()")

        if self.command in ['givetip', 'withdraw']:
            # Fiat yo
            self.fiat = 'usd'
            
            if self.coinval == None:
                self.coinval = 0
            
            self.fiatval = self.haikuberu.coin_value('dog', 'usd') * self.coinval

            # Final check - is this a to_addr transaction and is the address owned by dogetipbot?
            if self.addr_to:
                # Address validation
                try:
                    if not addressvalidate.is_dogecoin_address(self.addr_to):
                        raise ValueError("Not an address")
                except ValueError:
                    self.save('failed', 'addr_invalid')
                    self.tip_notification()
                    return False
                
                sqlcheck = "SELECT user_id from address where address = %s "
                mysqlrow = self.haikuberu.db.execute(sqlcheck,(self.addr_to)).fetchone()
                lg.debug('HkAction::validate(): Checking if user is sending to a dogetipbot address')
                lg.debug(sqlcheck, (self.addr_to))
                if not mysqlrow:
                    lg.debug("HkAction::givetip(%s): external address, hit the blockchain",self.addr_to)
                else:
                    # Address is owned by dogetipbot, now figure out service/username
                    lg.debug("HkAction::givetip(%s): sneaky motherfucker! found a user_id %s", self.addr_to, mysqlrow['user_id'])
                    user_id = mysqlrow['user_id']
                    sql = "SELECT username.username, service.service_name FROM username JOIN service ON service.service_ID = username.service_id where username.user_id = %s AND username.service_id = %s"
                    mysqlrow = self.haikuberu.db.execute(sql,(user_id, self.service_id)).fetchone()
                    if not mysqlrow:
                        lg.debug('HkAction::givetip(): Failed in a bad spot, no username/service found for user_id THIS SHOULDNT HAPPEN')
                    else:
                        self.u_to=user.HkUser(self.haikuberu, mysqlrow['service_name'], mysqlrow['username'])
                        lg.debug("HkAction::givetip(%s): sneaky motherfucker! it's really %s from %s service",self.addr_to,mysqlrow['username'], mysqlrow['service_name'])

            # Check if u_from has registered
            if not self.u_from.is_registered():
                lg.debug("HkAction::validate(): %s", 'From User Not Registered')
                self.save('failed', 'not_registered')
                self.tip_notification()
                return False

            # Verify that u_from has coin address
            if not self.u_from.get_addr(coin=self.coin):
                lg.error("HkAction::validate(): user %s doesn't have %s address", self.u_from.username, self.coin.upper())
                self.save('failed')
                return False

            # Verify minimum transaction size
            txkind = 'givetip' if self.u_to else 'withdraw'
            if self.coinval < self.haikuberu.conf.coins[self.coin].minconf[txkind]:

                lg.debug("HkAction::validate(): tip below minimum amt CHEAP ASS")
                self.save('failed', 'tip_below_minimum')
                self.tip_notification()
                return False

            # Verify balance (unless it's a pending transaction being processed, in which case coins have been already moved to pending acct)
            if self.u_to and not is_pending:
                # Tip to user (requires less confirmations)
                balance_avail = self.u_from.get_balance(coin=self.coin)
                if(balance_avail < self.coinval):
                    lg.debug("HkAction::validate(): Not Enough Coins To send the tip")
                    self.save('failed', 'balance_too_low')
                    self.tip_notification()
                    return False

            elif self.addr_to:
                # Tip/withdrawal to address (requires more confirmations)
                balance_avail = self.u_from.get_balance(coin=self.coin)
                if balance_avail < self.coinval:
                    lg.debug("HkAction::validate():  Im pretty sure this is just a repetetive fail")
                    self.save('failed')
                    return False

            # Check if u_to has any pending coin tips from u_from
            if self.u_to and not is_pending:
                if check_action(command='givetip', state='pending', to_user=self.u_to.username, from_user=self.u_from.username, coin=self.coin, haikuberu=self.haikuberu, service=self.service):
                    lg.debug("HkAction::validate(): TIP FAILED")
                    self.save('failed')
                    return False

            # Check if u_to has registered, if applicable
            if self.u_to and not self.u_to.is_registered():
                # u_to not registered:
                # - move tip into pending account
                # - save action as 'pending'
                # - notify u_to to accept tip <<< LOL FIGURE OUT ON YOUR OWN
                b = user.HkUser(self.haikuberu, self.service, self.haikuberu.conf.service[self.service].username)

                # Move coins into pending account
                minconf = self.haikuberu.coins[self.coin].conf.minconf.givetip
                lg.info("HkAction::validate(): moving %s %s from %s to %s (minconf=%s)...", self.coinval, self.coin.upper(), self.u_from.username, self.haikuberu.conf.service[self.service].username, minconf)

                # move from user to dogetipbot
                self.u_from.get_balance(coin=self.coin)
                b.get_balance(coin=self.coin)
                self.u_from.sub_coin(coin=self.coin, amount=self.coinval)
                b.add_coin(coin=self.coin, amount=self.coinval)

                # Save action as pending
                self.save('pending')
                
                # Send pending notifications
                self.tip_notification()

                # Action saved as 'pending', return false to avoid processing it further
                return False

            # Validate addr_to, if applicable
            if self.addr_to:
                if not self.haikuberu.coins[self.coin].validateaddr(_addr=self.addr_to):
                    lg.debug("HkAction::validate(): address not valid")
                    self.save('failed', 'addr_invalid')
                    self.tip_notification()
                    return False

            # Validate motherfucking balance if its a withdraw and there is not user_to set
            if self.addr_to and not self.u_to:
                hotwallet_amt = self.haikuberu.coins['dog'].conn.getbalance()
                if (self.coinval > hotwallet_amt):
                    lg.debug("HkAction::validate(): HOT WALLET DEPLETED")
                    self.save('failed')
                    if self.haikuberu.conf.misc.notify.enabled:
                        self.haikuberu.notify(_msg="Transaction exceeded hot wallet balance. User affected: " + self.u_from.username + " " + str(self.coinval))
                    return False

        # Action is valid
        lg.debug("< HkAction::validate() DONE")
        return True



    # Give tip
    def givetip(self, is_pending=False):

        # Debug
        lg.debug("> HkAction::givetip()")
        my_id = "NoMessageID"
        
        self.is_pending = is_pending
        
        # Return value assumes failure
        return_value = False
        
        # Set message ID (unique ID) if there is one
        if self.msg_id:
            my_id = self.msg_id

        # Check if action has been processed
        if check_action(command = self.command, msg_id = my_id, haikuberu = self.haikuberu, is_pending = is_pending, service = self.service):
            # Found action in database, returning
            lg.warning("HkAction::givetip(): duplicate action %s (msg.id %s), ignoring", self.command, my_id)
            return False

        # Validate action
        if not self.validate(is_pending = is_pending):
            # Couldn't validate action, returning
            return False

        # Sending to a user
        if self.u_to:
            # Pending check
            if is_pending:
                # This is accept() of pending transaction, so move coins from pending account to receiver
                lg.info("HkAction::givetip(): moving %f %s from %s to %s...", self.coinval, self.coin.upper(), 'dogetipbot', self.u_to.username)
                b = user.HkUser(self.haikuberu, self.service, self.haikuberu.conf.service[self.service].username)
                b.sub_coin(coin=self.coin, amount=self.coinval)
                self.u_to.add_coin(coin=self.coin, amount=self.coinval)
            else:
                # This is not accept() of pending transaction, so move coins from tipper to receiver
                lg.info("HkAction::givetip(): moving %f %s from %s to %s...", self.coinval, self.coin.upper(), self.u_from.username, self.u_to.username)
                self.u_from.sub_coin(coin=self.coin, amount=self.coinval)
                self.u_to.add_coin(coin=self.coin, amount=self.coinval)

            # Transaction succeeded (save returns True on success)
            return_value = self.save('completed')

        elif self.addr_to:
            # Process tip to address
            try:
                lg.info("HkAction::givetip(): sending %f %s to %s...", self.coinval, self.coin, self.addr_to)
                
                # Send withdraw to blockchain
                self.txid = self.haikuberu.coins[self.coin].sendtoaddr(_userfrom=self.u_from.username, _addrto=self.addr_to, _amount=self.coinval)

                # Subtract coins from user account
                self.u_from.sub_coin(coin=self.coin, amount=self.coinval)

                # Transaction is pending until confirmed
                return_value = self.save('pending')
                
                # Put in unprocessed table for confirmation check
                self.haikuberu.db.execute("INSERT INTO unprocessed SET txid = '" + self.txid + "' ")

            except Exception as e:
                # Transaction failed
                self.save('failed')
                lg.error("HkAction::givetip(): sendtoaddr() failed")

        # Now send notifications
        self.tip_notification()
        
        # Done
        lg.debug("< HkAction::givetip() DONE")
        return None



    def register(self):
        """
        Register a new user
        """
        lg.debug("> HkAction::register()")

        action_type = 'register'

        # If user exists, do nothing
        if self.u_from.is_registered():
            lg.debug("HkAction::register(%s): user already exists; ignoring request", self.u_from.username)
            self.save('failed', 'already_registered')
            action_type = 'already_registered'

            # Save action to database
            self.save('failed', 'already_registered')
        else:
            self.u_from.register()

            # Save action to database
            self.save('completed')

        # Base notification data
        data = {
            'type'          : action_type,
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'addr_from'     : self.u_from.get_addr('dog'),
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10,
            'associated'    : self.u_from.get_usernames(),
            'total_doge_sent'       : str(self.u_from.total_sent()),
            'total_doge_received'   : str(self.u_from.total_received()),
            'total_fiat_sent'       : str(self.u_from.total_fiat_sent()),
            'total_fiat_received'   : str(self.u_from.total_fiat_received()),
            'balance'               : str(self.u_from.get_balance(self.coin))
        }
        self.haikuberu.push_messasge_out(json.dumps(data))
        self.notification.append(data.copy())

        return self






    
    
    # Tip notifications, lots of logic here
    def tip_notification(self):
        # Base notification data
        data = {
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'is_new_shibe'  : self.u_from.is_new_user(),
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10
        }
        
        # Generic message with balance (used for completed and pending)
        if self.u_to:
            balance_generic = { 'u_to': self.u_to.username, 'coinval': str(self.coinval), 'fiatval': str(self.fiatval), 'fiat' : self.fiat }
        else:
            balance_generic = { 'addr_to': self.addr_to, 'coinval': str(self.coinval), 'fiatval': str(self.fiatval), 'fiat' : self.fiat }
        
        # Merge base data with the balance data
        balance_generic.update(data)

        # Success or error
        if self.state == 'completed':
            # Success
            if self.u_to:
                # To a user

                # From user
                if self.is_pending is False:
                    u_from_sent = balance_generic.copy()
                    u_from_sent.update({ 'type': 'tip_sent', 'balance': str(self.u_from.get_balance(self.coin)), 'addr_from' : self.u_from.get_addr('dog') })
                    if self.addr_to:
                         u_from_sent.update({ 'type': 'tip_sent_sneaky', 'addr_to': self.addr_to })
                    else:
                         u_from_sent.update({ 'addr_to': self.u_to.get_addr('dog') })
                        
                    self.haikuberu.push_messasge_out(json.dumps(u_from_sent))
                    self.notification.append(u_from_sent.copy())

                # To user (Same data so just update the generic data to a 'tip_received' type)
                u_to_sent = balance_generic.copy()
                u_to_sent.update({ 'type': 'tip_received', 'balance': str(self.u_to.get_balance(self.coin)), 'addr_from' : self.u_from.get_addr('dog') })
                if self.addr_to:
                     u_to_sent.update({ 'type': 'tip_received_sneaky', 'addr_to': self.addr_to })
                else:
                    u_to_sent.update({ 'addr_to': self.u_to.get_addr('dog') })
                     
                     
                self.haikuberu.push_messasge_out(json.dumps(u_to_sent))
                self.notification.append(u_to_sent.copy())
            elif self.addr_to: # Remember an address can be set along with a u_to in certain cases (handled above)
                # To an address

                # From user
                u_from_sent = balance_generic.copy()
                u_from_sent.update({ 'type': 'withdraw', 'balance': str(self.u_from.get_balance(self.coin)), 'addr_from' : self.u_from.get_addr('dog') })
                self.haikuberu.push_messasge_out(json.dumps(u_from_sent))
                self.notification.append(u_from_sent.copy())
                
                # No notification for an address, duh
        elif self.state == 'failed':
            # Error
            
            # Not registered
            if self.error == 'not_registered':
                u_from_error = { 'type' : 'not_registered' }
                u_from_error.update(data)
                self.haikuberu.push_messasge_out(json.dumps(u_from_error))
                self.notification.append(u_from_error.copy())
            elif self.error == 'balance_too_low':
                u_from_error = { 'type' : 'balance_too_low', 'balance': str(self.u_from.get_balance(self.coin)) }
                u_from_error.update(data)
                self.haikuberu.push_messasge_out(json.dumps(u_from_error))
                self.notification.append(u_from_error.copy())
            elif self.error == 'tip_below_minimum':
                u_from_error = { 'type' : 'tip_below_minimum' }
                u_from_error.update(data)
                self.haikuberu.push_messasge_out(json.dumps(u_from_error))
                self.notification.append(u_from_error.copy())
            elif self.error == 'addr_invalid':
                u_from_error = { 'type' : 'addr_invalid', 'addr_to': self.addr_to }
                u_from_error.update(data)
                self.haikuberu.push_messasge_out(json.dumps(u_from_error))
                self.notification.append(u_from_error.copy())
           
        elif self.state == 'pending':
            # To a non registered ('pending' in action table) user

            # Expiration time
            seconds = int(self.haikuberu.conf.misc.times.expire_pending_hours * 3600)
            expiration_time = time.mktime(time.gmtime()) + seconds

            # From user
            u_from_sent = balance_generic.copy()
            u_from_sent.update({ 'type': 'tip_sent', 'balance': str(self.u_from.get_balance(self.coin)), 'addr_from' : self.u_from.get_addr('dog') })
            self.haikuberu.push_messasge_out(json.dumps(u_from_sent))
            self.notification.append(u_from_sent.copy())

            # To user (tip incoming)
            if self.u_to:
                u_to_sent = balance_generic.copy()
                u_to_sent.update({ 'type': 'tip_incoming', 'time_to_expire': expiration_time, 'addr_from' : self.u_from.get_addr('dog') })
                self.haikuberu.push_messasge_out(json.dumps(u_to_sent))
                self.notification.append(u_to_sent.copy())



    def error_notification(self, error_type):
        # Base notification data
        data = {
            'type'          : error_type,
            'service'       : self.service,
            'command'       : self.command,
            'u_from'        : self.u_from.username,
            'config1'       : self.config1,
            'config2'       : self.config2,
            'config3'       : self.config3,
            'config4'       : self.config4,
            'config5'       : self.config5,
            'config6'       : self.config6,
            'config7'       : self.config7,
            'config8'       : self.config8,
            'config9'       : self.config9,
            'config10'      : self.config10
        }
        self.haikuberu.push_messasge_out(json.dumps(data))
        self.notification.append(data.copy())
        
        return self



def check_action(command=None, state=None, coin=None, service=None, msg_id=None, timestamp=None, from_user=None, to_user=None, subr=None, haikuberu=None, is_pending=False, verify=None, channel=None):
    """
    Return True if action with given attributes exists in database
    """
    lg.debug("> check_action(%s)", command)

    if not bool(service):
        raise Exception("> CheckAction failed : service not set, this should never happen")



    # Build SQL query
    sql = "SELECT * FROM action "
    sql_terms = []
    if command or state or coin or msg_id or timestamp or from_user or to_user or subr or is_pending or service:
        sql += " WHERE "
        if command:
            sql_terms.append("type = '%s'" % command)
        if service:
            service_id = hkservice.HkService(haikuberu).get_from_name(service)
            sql_terms.append("service_id = '%s'" % service_id)
        if state:
            sql_terms.append("state = '%s'" % state)
        if coin:
            sql_terms.append("coin = '%s'" % coin)
        if msg_id:
            sql_terms.append("config1 = '%s'" % msg_id)
        if timestamp:
            sql_terms.append("action.timestamp = %s" % timestamp)
        if from_user:
            sql_terms.append("action.from_user = '%s'" % from_user.lower())
        if to_user:
            sql_terms.append("action.to_user = '%s'" % to_user.lower())
        if subr:
            sql_terms.append("config2 = '%s'" % subr)
        if channel:
            sql_terms.append("config1 = '%s'" % channel)
        if is_pending:
            sql_terms.append("state <> 'pending'")
        sql += ' AND '.join(sql_terms)


    try:
        lg.debug("check_action(): <%s>", sql)
        mysqlexec = haikuberu.db.execute(sql)
        if mysqlexec.rowcount <= 0:
            lg.debug("< check_action() DONE (no)")
            return False
        else:
            lg.debug("< check_action() DONE (yes)")
            return True
    except Exception as e:
        lg.error("check_action(): error executing <%s>: %s", sql, e)
        raise

    lg.warning("< check_action() DONE (should not get here)")
    return None



def get_actions(command=None, state=None, deleted_msg_id=None, deleted_created_utc=None, channel=None, coin=None, msg_id=None, timestamp=None, from_user=None, to_user=None, subr=None, haikuberu=None, verify=None, service=None, created_utc = None):
    """
    Return an array of HkAction objects from database with given attributes
    """
    lg.debug("> get_actions(%s)", command)

    # Build SQL query
    sql = "SELECT * FROM action JOIN service ON service.service_id = action.service_id "
    sql_terms = []
    if command or state or coin or msg_id or timestamp or from_user or to_user or subr or service:
        sql += " WHERE "
        if command:
            sql_terms.append("action.type = '%s'" % command)
        if state:
            sql_terms.append("action.state = '%s'" % state)
        if coin:
            sql_terms.append("action.coin = '%s'" % coin)
        if msg_id:
            sql_terms.append("action.config1 = '%s'" % msg_id)
        if timestamp:
            sql_terms.append("action.timestamp %s" % timestamp)
        if channel:
            sql_terms.append("aaction.config1 %s" % channel)
        if from_user:
            sql_terms.append("action.from_user = '%s'" % from_user.lower())
        if to_user:
            sql_terms.append("action.to_user = '%s'" % to_user.lower())
        if subr:
            sql_terms.append("action.config3 = '%s'" % subr)
        sql += ' AND '.join(sql_terms)

    while True:
        try:
            r = []
            lg.debug("get_actions(): <%s>", sql)
            mysqlexec = haikuberu.db.execute(sql)
            print sql

            if mysqlexec.rowcount <= 0:
                lg.debug("< get_actions() DONE (no)")
                return r

            for m in mysqlexec:
                lg.debug("get_actions(): found %s", m['action_id'])


                request = dict()
                request['body'] = json.dumps({
                    "service"       : m['service_name'],
                    "u_from"        : m['from_user'],
                    "u_to"          : m['to_user'],
                    "coin"          : m['coin'],
                    "coin_val"      : str(m['coin_val']) if m['coin_val'] else None,
                    "type"          : m['type'],
                    "action_id"     : m['action_id']
                })
                
                # Perform request
                act = HkAction(haikuberu, request)
                act.config1 = m['config1']
                act.config2 = m['config2']
                act.config3 = m['config3']
                act.config4 = m['config4']
                act.config5 = m['config5']
                act.config6 = m['config6']
                act.config7 = m['config7']
                act.config8 = m['config8']
                act.config9 = m['config9']
                act.config10 = m['config10']
                r.append(act)

            lg.debug("< get_actions() DONE (yes)")
            return r

        except Exception as e:
            lg.error("get_actions(): error executing <%s>: %s", sql, e)
            raise

    lg.warning("< get_actions() DONE (should not get here)")
    return None


