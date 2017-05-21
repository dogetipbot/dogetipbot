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
"""
    This file is part of ALTcointip.

    ALTcointip is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ALTcointip is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ALTcointip.  If not, see <http://www.gnu.org/licenses/>.
"""

import ctb_user, ctb_misc, ctb_stats

import logging, praw, re, time, decimal
import simplejson as json
from random import randint
from decimal import *
import yaml
from iron_mq import *
from math import trunc
import datetime
import time
import requests, requests.auth
from requests.exceptions import HTTPError, ConnectionError, Timeout

lg = logging.getLogger('cointipbot')

class CtbAction(object):
    """
    Action class for cointip bot
    """

    type=None           # 'accept', 'decline', 'history', 'info', 'register', 'givetip', 'withdraw', 'rates', 'deposit'
    state=None          # 'completed', 'pending', 'failed', 'declined'
    txid=None           # cryptocoin transaction id, a 64-char string, if applicable

    u_from=None         # CtbUser instance
    u_to=None           # CtbUser instance, if applicable
    addr_to=None        # destination cryptocoin address of 'givetip' and 'withdraw' actions, if applicable


    coin=None           # coin for this action (for example, 'ltc')
    fiat=None           # fiat for this action (for example, 'usd'), if applicable
    coin_val=None        # coin value of 'givetip' and 'withdraw' actions
    fiat_val=None        # fiat value of the 'givetip' or 'withdraw' action
    keyword=None        # keyword that's used instead of coin_val/fiatval
    verify=None         # verify this tip?

    subreddit=None      # subreddit that originated the action, if applicable

    msg=None            # Reddit object pointing to originating message/comment

    ctb=None            # CointipBot instance

    deleted_msg_id=None	        # Used for accepting tips if the original message was deleted
    deleted_created_utc=None    # Used for accepting tips if the original message was deleted

    is_pull_queue=None          # Determines if message is from the pull queue
    msg_type=None               #When getting pull queue msg, type of msg to send
    is_new_shibe=None           #When getting pull queue msg, need to know if new shibe or not
    balance =None               #When getting pull queue msg, sometimes need balance
    addr_from=None              #When getting pull queue msg, sometimes need address of user sending (history/balance etc)
    total_doge_sent=None        #When getting pull queue msg, for history need total doge sent
    total_doge_received=None    #When getting pull queue msg, for history need total doge received
    history_list = None         #When getting pull queue msg, for history need history
    associated = None           #When getting pull queue msg, Need associated accounts
    total_fiat_received=None
    total_fiat_sent = None
    queue_id = None             #MSGID from queue so we can delete it after the action is over
    reservation_id = None		#reservation_id from queue so we can delete it
    message_body = None         #hack for stupid body messages of fullnames starting with t4
    permalink = None            #hack for stupid body messages of fullnames starting with t4#
    fullname = None             #hack for stupid body messages of fullnames starting with t4#

    def __init__(self, atype=None, msg=None, deleted_msg_id=None, deleted_created_utc=None, from_user=None, to_user=None, to_addr=None, coin=None, fiat='usd', coin_val=None, fiat_val=None, subr=None, ctb=None, keyword=None, verify=None, is_pull_queue=False, msg_type=None, is_new_shibe=False, balance=None, txid=None, addr_from=None, total_doge_sent=None, total_doge_received=None, history_list=None, associated=None, total_fiat_received=None, total_fiat_sent=None, queue_id=None, reservation_id = None, msg_body = None, permalink=None, fullname=None):
        """
        Initialize CtbAction object with given parameters and run basic checks
        """
        lg.debug("> CtbAction::__init__(type=%s)", atype)

        self.type = atype

        self.coin = 'dog'
        self.fiat = fiat.lower() if fiat else None
        if coin_val != 'all' and coin_val is not None:
            self.coin_val = Decimal(coin_val)
        else:
            self.coin_val = coin_val
        self.fiat_val = Decimal(fiat_val) if fiat_val else None
        self.keyword = keyword.lower() if keyword else None

        self.msg = msg
        self.ctb = ctb
        self.deleted_msg_id = deleted_msg_id
        self.deleted_created_utc = deleted_created_utc
        self.verify = verify

        self.addr_to = to_addr
        self.u_to = ctb_user.CtbUser(name=to_user, ctb=ctb) if to_user else None
        self.u_from = ctb_user.CtbUser(name=msg.author.name, redditobj=msg.author, ctb=ctb) if (msg and msg.author) else ctb_user.CtbUser(name=from_user, ctb=ctb)
        self.subreddit = subr

        self.is_pull_queue = is_pull_queue
        self.msg_type = msg_type if msg_type else None
        self.is_new_shibe = is_new_shibe if is_new_shibe else None
        self.balance = balance if balance else None
        self.txid = txid if txid else None
        self.addr_from = addr_from if addr_from else None
        self.total_doge_received = total_doge_received if total_doge_received else None
        self.total_doge_sent = total_doge_sent if total_doge_sent else None
        self.associated = associated if associated else None
        self.history_list = history_list if history_list else None
        self.total_fiat_received = total_fiat_received if total_fiat_received else None
        self.total_fiat_sent = total_fiat_sent if total_fiat_sent else None
        self.queue_id = queue_id
        self.reservation_id = reservation_id
        self.msg_body = msg_body if msg_body else None
        self.permalink = permalink if permalink else None
        self.fullname = fullname if fullname else None

        # Do some checks
        if not self.type:
            raise Exception("CtbAction::__init__(type=?): type not set")
        if not self.ctb:
            raise Exception("CtbAction::__init__(type=%s): no reference to CointipBot", self.type)




        lg.debug("CtbAction::__init__(): %s", self)




        lg.debug("< CtbAction::__init__(atype=%s, from_user=%s) DONE", self.type, self.u_from.name)

    def __str__(self):
        """""
        Return string representation of self
        """
        me = "<CtbAction: type=%s, msg=%s, u_from=%s, u_to=%s, addr_to=%s, coin=%s, fiat=%s, coin_val=%s, fiat_val=%s, subreddit=%s, verify=%s, is_pull_queue=%s, msg_type=%s, is_new_shibe=%s, balance=%s, txid=%s, addr_from=%s, total_doge_received=%s, total_doge_sent=%s, ctb=%s>"
        me = me % (self.type, self.msg, self.u_from, self.u_to, self.addr_to, self.coin, self.fiat, self.coin_val, self.fiat_val, self.subreddit, self.verify, self.is_pull_queue, self.msg_type, self.is_new_shibe, self.balance, self.txid, self.addr_from, self.total_doge_received, self.total_doge_sent, self.ctb)
        return me

    def send_to_push_queue(self):
        """
        Send request to haikuberu for processing
        """
        req = dict()
        #first make sure no negative values exist
        if self.coin_val != 'all':
            if self.coin_val < 0.0:
                self.coin_val = 0.0
        if self.fiat_val < 0.0:
            self.fiat_val = 0.0

        realutc = None
        realmsgid = None
        
        if self.msg:
            realmsgid=self.msg.id
            realutc=self.msg.created_utc
            req['created_utc'] = trunc(realutc)
        else:
            realmsgid=self.deleted_msg_id
            tuple_time=self.deleted_created_utc
            realutc = time.mktime(tuple_time.timetuple())
            req['created_utc'] = realutc
        

        req['service'] = 'reddit'
        
        req['type'] = self.type

        if self.u_from:
            req['u_from'] = self.u_from.name.lower()
        if self.u_to:
            req['u_to'] = self.u_to.name.lower()
        if self.addr_to:
            req['addr_to'] = self.addr_to

        if self.coin_val:
            req['coin_val'] = str(self.coin_val)
        if self.verify:
            req['verify'] = 1
        if realmsgid:
            req['msgid'] = realmsgid
        if self.fullname:
            req['fullname'] = self.fullname
        else:
            req['fullname'] = self.msg.fullname


        if self.subreddit:
            req['subreddit'] = self.subreddit.display_name

        if self.msg:
            if hasattr(self.msg, 'permalink'):
                req['permalink'] = self.msg.permalink

        if self.permalink:
            req['permalink'] = self.permalink

        request = json.dumps(req)
        
        self.ctb.push_queue.post(request)

    def save_pending(self, state=None):
        """
        Save pending action to database
        """
        lg.debug("> CtbAction::save_pending(%s)", state)

        # Make sure no negative values exist
        if self.coin_val < 0.0:
            self.coin_val = 0.0
        if self.fiat_val < 0.0:
            self.fiat_val = 0.0

        realutc = None
        realmsgid = None

        if self.msg:
            realmsgid=self.msg.id
            realutc=self.msg.created_utc
        else:
            realmsgid=self.deleted_msg_id
            realutc=self.deleted_created_utc
        msg_body = None
        if self.msg.fullname:
            fullname = self.msg.fullname
            fullname = fullname.split('_')
            if 't4' in fullname:
                msg_body = self.msg.body
            else:
                msg_body = None
        conn = self.ctb.db
        sql = "REPLACE INTO pending_action (type, state, created_utc, from_user, to_user, to_addr, coin_val, fiat_val, txid, coin, fiat, subreddit, verify, msg_id, fullname, msg_link, msg_body)"
        sql += " values (%s, %s, from_unixtime(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        try:
            mysqlexec = conn.execute(sql,
                    (self.type,
                     state,
                     realutc,
                     self.u_from.name.lower(),
                     self.u_to.name.lower() if self.u_to else None,
                     self.addr_to,
                     self.coin_val,
                     self.fiat_val,
                     self.txid,
                     self.coin,
                     self.fiat,
                     self.subreddit,
                     1 if self.verify else 0,
                     realmsgid,
                     self.msg.fullname,
                     self.msg.permalink if hasattr(self.msg, 'permalink') else None,
                     msg_body if msg_body else None))
            if mysqlexec.rowcount <= 0:
                raise Exception("query didn't affect any rows")
        except Exception as e:
            lg.error("CtbAction::save(%s): error executing query <%s>: %s", state, sql % (
                self.type,
                state,
                realutc,
                self.u_from.name.lower(),
                self.u_to.name.lower() if self.u_to else None,
                self.addr_to,
                self.coinval,
                self.fiatval,
                self.txid,
                self.coin,
                self.fiat,
                self.subreddit,
                realmsgid,
                self.msg.permalink if hasattr(self.msg, 'permalink') else None,
                msg_body if msg_body else None), e)
            raise

        lg.debug("< CtbAction::add_pending() DONE")
        return True

    def error(self):
        """
        If command & type are different its an error so send appropriate message
        """

        if self.msg_type == 'coldstorage_hit':
            msg = self.ctb.jenv.get_template('coldstorage.tpl').render(a=self, ctb=self.ctb)
            lg.debug("CtbAction::error(): coldstorage_hit: " + msg)
            self.u_from.tell(subj="Yeeeep. You broke the bank!", msg=msg)
            self.clear_queue()
            return True

        if self.msg_type == 'balance_too_low':
            #balance_avail = Decimal(self.balance)
            #msg = self.ctb.jenv.get_template('tip-low-balance.tpl').render(balance=balance_avail, action_name='tip', a=self, ctb=self.ctb)
            lg.debug("CtbAction::error(): balance_too_low: ")
            #send balance too low for gold fails
            if self.type == 'gold':
                msg = self.ctb.jenv.get_template('gold-low-balance.tpl').render(a=self, ctb=self.ctb)
                self.u_from.tell(subj="+gold failed balance too low", msg=msg)
            self.clear_queue()
            return True

        if self.msg_type == 'tip_below_minimum':
            #msg = self.ctb.jenv.get_template('tip-below-minimum.tpl').render(min_value=4, a=self, ctb=self.ctb)
            lg.debug("CtbAction::error(): tip_below_minimum ignore")
            #self.u_from.tell(subj="+tip failed", msg=msg)
            self.clear_queue()
            return True

        if self.msg_type == 'not_registered':
            msg = self.ctb.jenv.get_template('not-registered.tpl').render(a=self, ctb=self.ctb)
            lg.debug("CtbAction::error(): not_registered " + msg)
            self.u_from.tell(subj="+info failed", msg=msg)
            self.clear_queue()
            return True

        if self.msg_type == 'tip_incoming':
            if self.u_to is None or self.u_to.is_on_reddit() ==False:
                lg.debug("CtbAction::error(): tip_incoming TO ADDRESS DELETING or user doesn't exist")
                self.clear_queue()
                return True
            else:

                msg=self.ctb.jenv.get_template('tip-incoming.tpl').render(a=self, ctb=self.ctb)
                lg.debug("CtbAction::error(): tip_incoming " + msg)
                self.u_to.tell(subj="+tip incoming", msg=msg)
                self.clear_queue()
                return True

        if self.msg_type == 'already_registered':
            lg.debug('CtbAction::error(): already_registered')
            self.clear_queue()
            return True

        if self.msg_type == 'fiat_error':
            lg.debug('CtbAction::error(): fiat error awwww shit')
            msg=self.ctb.jenv.get_template('fiat-error.tpl').render(a=self, ctb=self.ctb)
            self.u_from.tell(subj="+something went super wrong ", msg=msg)
            self.clear_queue()
            return True

        if self.msg_type == 'gold_received':
            lg.debug('CtbAction::error(): unregistered user got gilded homie')
            msg=self.ctb.jenv.get_template('gold-not-registered.tpl').render(a=self, ctb=self.ctb)
            self.u_to.tell(subj="+You just got reddit gold from a dogetipbot user! ", msg=msg)
            self.clear_queue()
            return True

        lg.debug('CtbAction::error(): reached end of error')
        return None


    def do(self):
        """
        Call appropriate function depending on action type
        """
        lg.debug("> CtbAction::do()")

        if self.type == 'deposit':
            return self.deposit()

        if not self.ctb.conf.regex.actions[self.type].enabled:
            lg.info("CtbAction::do(): action %s is disabled", self.type)
            return False

        if self.msg_type in ['coldstorage_hit', 'balance_too_low', 'tip_below_minimum', 'not_registered', 'tip_incoming', 'already_registered', 'fiat_error', 'gold_received']:
            return self.error()

        if self.type == 'accept':
            self.type = 'info'
            return self.info()

        if self.type == 'decline':
            return self.decline()

        if self.type == 'givetip':
            result = self.givetip()
            return result

        if self.type == 'history':
            return self.history()

        if self.type == 'info':
            return self.info()

        if self.type == 'register':
            self.type = 'info'
            return self.info()

        if self.type == 'withdraw':
            return self.givetip()

        if self.type == 'gold':
            return self.gold()


        lg.debug("< CtbAction::do() DONE")
        return None


    def clear_queue(self):
        if self.queue_id:
            lg.info("CtbAction::clear_queue(): clearing msg: %s  from queue.", self.queue_id, )
            self.ctb.delete_message(self.queue_id, self.reservation_id)
        else:
            lg.info("CtbAction::clear_queue(): not from queue... skipping.")


    def deposit(self):
        """
        Provide user with deposit message
        """
        my_balance = Decimal(self.balance)
        my_balance = '{0:.2f}'.format(my_balance)
        total_deposited = Decimal(self.coin_val)
        total_deposited = '{0:.2f}'.format(total_deposited)
        msg = self.ctb.jenv.get_template('deposit.tpl').render(user=self.u_from.name.lower(), balance=my_balance, deposit=self.coin, coin_val=total_deposited,  ctb=self.ctb)
        lg.debug("CtbAction::deposit(): sending message: %s", msg)
        self.u_from.tell(subj='Deposit Confirmation', msg=msg, msgobj=None)
        self.clear_queue()
        return True

    def history(self):
        """
        Provide user with transaction history
        """

        # Generate history array
        history = []
        keys = []

        #such a fuckin ghetto way of fixing up the configs we want
        keys = ['type', 'state', 'from_user', 'to_user', 'timestamp', 'to_addr', 'coin_val', 'coin', 'fiat_val', 'fiat', 'config3']

        if self.history_list is not None:
            for m in self.history_list:
                history_entry= []

                for k in keys:

                    history_entry.append(ctb_stats.format_value(m, k, self.u_from.name.lower(), self.ctb, compact=True))
                history.append(history_entry)
        
        tips_sent = Decimal(self.total_doge_sent)
        tips_rcvd = Decimal(self.total_doge_received)
        usd_sent = Decimal(self.total_fiat_sent) if self.total_fiat_sent else None
        usd_rcvd = Decimal(self.total_fiat_received) if self.total_fiat_received else None

        #change config3 to subreddit
        keys = [key.replace('config3', 'subreddit') for key in keys]
        balance_avail = Decimal(self.balance)
        my_addr = self.addr_from
        # Send message to user
        msg = self.ctb.jenv.get_template('history.tpl').render(history=history, sent=tips_sent, rcvd=tips_rcvd, usd_sent=usd_sent, usd_rcvd=usd_rcvd, addr=my_addr, balance=balance_avail, keys=keys, limit=50, a=self, ctb=self.ctb)
        lg.debug("CtbAction::history(): %s", msg)
        self.u_from.tell(subj="+history", msg=msg)
        self.clear_queue()
        return True

    def givetip(self):
        lg.debug('> CtbAction::givetip()')


        if self.msg_type=="tip_sent_sneaky":
            lg.debug('CtbAction::givetip() withdraw/tip to address sneaky sent ')
            balance_avail = Decimal(self.balance)
            my_addr = self.addr_from
            msg = self.ctb.jenv.get_template('withdraw-sneaky-from.tpl').render(addr=my_addr, balance=balance_avail, a=self, ctb=self.ctb)
            lg.debug("CtbAction::givetip(): tip_sent_sneaky: " + msg)
            self.u_from.tell(subj="you got some dogecoins", msg=msg)


        if self.msg_type == "tip_received_sneaky":
            lg.debug('CtbAction::givetip() withdraw/tip to address sneaky received ')
            balance_avail = Decimal(self.balance)
            my_addr = self.addr_to
            msg = self.ctb.jenv.get_template('withdraw-sneaky-to.tpl').render(addr=my_addr, balance=balance_avail, a=self, ctb=self.ctb)
            lg.debug("CtbAction::givetip(): tip_received_sneaky: " + msg)
            self.u_to.tell(subj="you withdrew some dogecoins", msg=msg)



        if self.msg_type == 'addr_invalid':
            lg.debug('CtbAction::givetip() Address Invalid ')
            msg = self.ctb.jenv.get_template('address-invalid.tpl').render(a=self, ctb=self.ctb)
            lg.debug("CtbAction::error(): addr_invalid: " + msg)
            self.u_from.tell(subj="+tip failed", msg=msg)


        if self.type == 'withdraw' and self.msg_type not in ['tip_received_sneaky', 'tip_sent_sneaky']:
            msg = self.ctb.jenv.get_template('confirmation.tpl').render(title='wow ^so ^verify', a=self, ctb=self.ctb)
            lg.debug("CtbAction::givetip(): ATTEMPTING-WITHDRAW" + msg)
            if (self.verify or self.coin_val >= 1000):
                #if not ctb_misc.praw_call(self.msg.reply, msg):
                self.u_from.tell(subj="+withdraw succeeded", msg=msg)
                lg.debug("< CtbAction::givetip() DONE")
                self.clear_queue()
                return True
            else:
                self.u_from.tell(subj="+withdraw succeeded", msg=msg)
                lg.debug("< CtbAction::givetip() DONE")
                self.clear_queue()
                return True

        if self.msg_type == 'tip_received':
            if self.is_new_shibe:
                balance_avail = Decimal(self.balance)
                my_addr = self.addr_to
                msg = self.ctb.jenv.get_template('tip-received.tpl').render(addr=my_addr, balance=balance_avail, a=self, ctb=self.ctb)
                lg.debug("CtbAction::givetip(): " + msg)
                self.u_to.tell(subj="+tip received", msg=msg)
            else:
                lg.debug("CtbAction::givetip(): OLD SHIBE. NO MESSAGE.")


        # Send confirmation to u_from
        # note to change code to add withdrawal if not to_addr
        if self.msg_type == 'tip_sent':
            if self.is_new_shibe:
                balance_avail = Decimal(self.balance)
                my_addr = self.addr_from
                msg = self.ctb.jenv.get_template('tip-sent.tpl').render(addr=my_addr, balance=balance_avail, a=self, ctb=self.ctb)
                lg.debug("CtbAction::givetip(): ATTMEPTING TIP-SENT" + msg)
                self.u_from.tell(subj="+tip sent", msg=msg)
            else:
                lg.debug("CtbAction::givetip(): OLD SHIBE. NO MESSAGE.")

            if self.verify or self.coin_val >= 1000:
                lg.debug("CtbAction::givetip(): action being verified: %s ", self)
                msg = self.ctb.jenv.get_template('tip-confirmation.tpl').render(title='wow ^so ^verify', a=self, ctb=self.ctb)
                lg.debug("CtbAction::givetip(): " + msg)
                if self.msg:
                    if self.ctb.conf.reddit.messages.verified:

                        ctb_misc.praw_call(self.msg.reply, msg)

                        lg.info("-------------------VERIFIED!: %s",self.verify)
                    else:
                        lg.info("NO FULLNAME CANT VERIFY for")
        lg.debug("< CtbAction::givetip() DONE")
        self.clear_queue()
        return True


    def gold(self):
        lg.debug('CTBAction:: gold() beginning: ')
        #prep to_user for stupid praw call
        #to_user_prawobj = ctb_misc.praw_call(self.ctb.reddit.get_redditor, self.u_to.name)

        if self.msg_type == 'gold_sent':
            #define the verify response for gilding
            lg.debug('access token found %s', self.ctb.conf.reddit.access_token)

            msg = self.ctb.jenv.get_template('gold-confirm.tpl').render(title='wow ^such ^gold', a=self, ctb=self.ctb)

            #try to guild comment
            if self.msg:
                #have to manually call the stupid api
                #set up headers and requests shit for manual api call
                headers = {"Authorization": "bearer " + self.ctb.conf.reddit.access_token, "User-Agent": self.ctb.conf.reddit.auth.user}
                parentcomment = ctb_misc.praw_call(self.ctb.reddit.get_info, thing_id=self.msg.parent_id)
                while True:
                    lg.debug('trying to gild this fullname %s', parentcomment.fullname)
                    gild_url = 'https://oauth.reddit.com/api/v1/gold/gild/' + parentcomment.fullname
                    lg.debug('CtbAction::gold trying to use this url : %s', gild_url)

                    #api call to gild
                    response = requests.post(gild_url,headers=headers )
                    if response.status_code == 200:
                        lg.debug('CtbAction::gold sent successfully')
                        break
                    else:
                        lg.debug('Gild Api call failed retrying')
                        r_info = json.loads(response.content)
                        lg.debug('got this as result %s', r_info)
                        time.sleep(10)
                        pass


                ctb_misc.praw_call(self.msg.reply, msg)
                lg.info("Gold Verified")
            else:
                lg.info("CtbAction::gold(): error gilding to user %s no fullname found for message", self.u_to.name)
        lg.debug("< CtbAction::gold() DONE")
        self.clear_queue()
        return True

    def info(self):
        """
        Send user info about account
        """
        lg.debug("> CtbAction::info()")
        lg.debug("> CtbAction::info():  self.ctb.coin_value(self.ctb.conf.coins[i.coin].unit, 'usd')")
        if self.balance is None:
            self.balance = 0.0

        info = []
        for c in sorted(self.ctb.coins):
            coininfo = ctb_misc.DotDict({})
            coininfo.coin = c
            try:
                # Get tip balance
                coininfo.balance = Decimal(self.balance)
                info.append(coininfo)
            except Exception as e:
                lg.error("CtbAction::info(%s): error retrieving %s coininfo: %s", self.u_from.name, c, e)
                raise

        fiat_total = Decimal(0.0)
        for i in info:
            i.fiat_symbol = self.ctb.conf.fiat.usd.symbol
            if self.ctb.coin_value(self.ctb.conf.coins[i.coin].unit, 'usd') > 0.0:
                lg.debug('CtbAction::info')
                i.fiat_balance = i.balance * self.fiat_val
                fiat_total += i.fiat_balance

        for i in info:
            i.address = self.addr_from


        if self.associated is not None:
            associated = self.associated

        # Format and send message
        msg = self.ctb.jenv.get_template('info.tpl').render(info=info, fiat_symbol=self.ctb.conf.fiat.usd.symbol, fiat_total=fiat_total, a=self, associated=associated, ctb=self.ctb)
        lg.debug('CtbAction::info() attempting to send message')
        self.u_from.tell(subj="+info", msg=msg)

        lg.debug("< CtbAction::info() DONE")
        self.clear_queue()
        return True


def init_regex(ctb):
    """
    Initialize regular expressions used to match messages and comments
    """
    lg.debug("> init_regex()")

    cc = ctb.conf.coins
    fiat = ctb.conf.fiat
    actions = ctb.conf.regex.actions
    ctb.runtime['regex'] = []

    for a in vars(actions):
        if actions[a].simple:

            # Add simple message actions (info, register, accept, decline, history, rates)

            entry = ctb_misc.DotDict(
                {'regex':       actions[a].regex,
                 'action':      a,
                 'rg_amount':   0,
                 'rg_keyword':  0,
                 'rg_address':  0,
                 'rg_to_user':  0,
                 'rg_verify':   0,
                 'coin':        None,
                 'fiat':        None,
                 'keyword':     None
                })
            lg.debug("init_regex(): ADDED %s: %s", entry.action, entry.regex)
            ctb.runtime['regex'].append(entry)

        else:

            # Add non-simple actions (givetip, withdraw)

            for r in sorted(vars(actions[a].regex)):
                lg.debug("init_regex(): processing regex %s", actions[a].regex[r].value)
                rval1 = actions[a].regex[r].value
                rval1 = rval1.replace('{REGEX_TIP_INIT}', ctb.conf.regex.values.tip_init.regex)
                rval1 = rval1.replace('{REGEX_USER}', ctb.conf.regex.values.username.regex)
                rval1 = rval1.replace('{REGEX_AMOUNT}', ctb.conf.regex.values.amount.regex)
                rval1 = rval1.replace('{REGEX_KEYWORD}', ctb.conf.regex.values.keywords.regex)

                if actions[a].regex[r].rg_coin > 0:

                    for c in sorted(vars(cc)):

                        if not cc[c].enabled:
                            continue
                        lg.debug("init_regex(): processing coin %s", c)

                        rval2 = rval1.replace('{REGEX_COIN}', cc[c].regex.units)
                        rval2 = rval2.replace('{REGEX_ADDRESS}', cc[c].regex.address)

                        if actions[a].regex[r].rg_fiat > 0:

                            for f in sorted(vars(fiat)):

                                if not fiat[f].enabled:
                                    continue
                                # lg.debug("init_regex(): processing fiat %s", f)

                                rval3 = rval2.replace('{REGEX_FIAT}', fiat[f].regex.units)
                                entry = ctb_misc.DotDict(
                                    {'regex':           rval3,
                                     'action':          a,
                                     'rg_amount':       actions[a].regex[r].rg_amount,
                                     'rg_keyword':      actions[a].regex[r].rg_keyword,
                                     'rg_address':      actions[a].regex[r].rg_address,
                                     'rg_to_user':      actions[a].regex[r].rg_to_user,
                                     'rg_verify':       actions[a].regex[r].rg_verify,
                                     'coin':            cc[c].unit,
                                     'fiat':            fiat[f].unit
                                    })
                                lg.debug("init_regex(): ADDED %s: %s", entry.action, entry.regex)
                                ctb.runtime['regex'].append(entry)

                        else:

                            entry = ctb_misc.DotDict(
                                {'regex':           rval2,
                                 'action':          a,
                                 'rg_amount':       actions[a].regex[r].rg_amount,
                                 'rg_keyword':      actions[a].regex[r].rg_keyword,
                                 'rg_address':      actions[a].regex[r].rg_address,
                                 'rg_to_user':      actions[a].regex[r].rg_to_user,
                                 'rg_verify':       actions[a].regex[r].rg_verify,
                                 'coin':            cc[c].unit,
                                 'fiat':            None
                                })
                            lg.debug("init_regex(): ADDED %s: %s", entry.action, entry.regex)
                            ctb.runtime['regex'].append(entry)

                elif actions[a].regex[r].rg_fiat > 0:

                    for f in sorted(vars(fiat)):

                        if not fiat[f].enabled:
                            continue
                        lg.debug("init_regex(): processing fiat %s", f)

                        rval2 = rval1.replace('{REGEX_FIAT}', fiat[f].regex.units)
                        entry = ctb_misc.DotDict(
                            {'regex':           rval2,
                             'action':          a,
                             'rg_amount':       actions[a].regex[r].rg_amount,
                             'rg_keyword':      actions[a].regex[r].rg_keyword,
                             'rg_address':      actions[a].regex[r].rg_address,
                             'rg_to_user':      actions[a].regex[r].rg_to_user,
                             'rg_verify':       actions[a].regex[r].rg_verify,
                             'coin':            None,
                             'fiat':            fiat[f].unit
                            })
                        lg.debug("init_regex(): ADDED %s: %s", entry.action, entry.regex)
                        ctb.runtime['regex'].append(entry)

                elif actions[a].regex[r].rg_keyword > 0:

                    entry = ctb_misc.DotDict(
                        {'regex':           rval1,
                         'action':          a,
                         'rg_amount':       actions[a].regex[r].rg_amount,
                         'rg_keyword':      actions[a].regex[r].rg_keyword,
                         'rg_address':      actions[a].regex[r].rg_address,
                         'rg_to_user':      actions[a].regex[r].rg_to_user,
                         'rg_verify':       actions[a].regex[r].rg_verify,
                         'coin':            None,
                         'fiat':            None
                        })
                    lg.debug("init_regex(): ADDED %s: %s", entry.action, entry.regex)
                    ctb.runtime['regex'].append(entry)

    lg.info("< init_regex() DONE (%s expressions)", len(ctb.runtime['regex']))
    return None


def eval_message(msg, ctb):
    """
    Evaluate message body and insert into the pending_action
    database if successful
    """
    lg.debug("> eval_message()")

    body = msg.body
    #lg.info(vars(msg)) #debug
    for r in ctb.runtime['regex']:

        # Attempt a match
        rg = re.compile(r.regex, re.IGNORECASE|re.DOTALL)
        #lg.debug("matching '%s' with '%s'", msg.body, r.regex)
        m = rg.search(body)

        if m:
            # Match found
            lg.debug("eval_message(): match found")

            # Extract matched fields into variables
            to_addr = m.group(r.rg_address) if r.rg_address > 0 else None
            amount = m.group(r.rg_amount) if r.rg_amount > 0 else None
            keyword = m.group(r.rg_keyword) if r.rg_keyword > 0 else None

            if keyword is not None:
                keyword = keyword.lower()
                lg.debug("eval_message(): keyword %s", keyword)
                if keyword == 'all':
                    amount = 'all'
                else:
                    amount  = ctb.conf.keywords[keyword].value
                    if type(amount) == str:
                        amount = eval(amount)
                    elif type(amount) == float:
                        amount = Decimal(amount)

            if ((to_addr == None) and (r.action == 'givetip')):
                lg.debug("eval_message(): can't tip with no to_addr")
                return None


            # Return CtbAction instance with given variables
            return CtbAction(   atype=r.action,
                                msg=msg,
                                from_user=msg.author,
                                to_user=None,
                                to_addr=to_addr,
                                coin='dog',
                                coin_val=amount if not r.fiat else None,
                                fiat=r.fiat,
                                fiat_val=amount if r.fiat else None,
                                keyword=keyword,
                                ctb=ctb)

    # No match found
    lg.debug("eval_message(): no match found")
    return None

def eval_db_message(msg_body, permalink, fullname, id, verify, fiat, coin, coin_val, to_addr, to_user, from_user, created_utc, type, ctb):
    """
    Evaluate message body and insert into the pending_action
    database if successful
    """
    lg.debug("> eval_message()")

    body = msg_body
    #lg.info(vars(msg)) #debug
    for r in ctb.runtime['regex']:

        # Attempt a match
        rg = re.compile(r.regex, re.IGNORECASE|re.DOTALL)
        #lg.debug("matching '%s' with '%s'", msg.body, r.regex)
        m = rg.search(body)

        if m:
            # Match found
            lg.debug("eval_message(): match found")

            # Extract matched fields into variables
            to_addr = m.group(r.rg_address) if r.rg_address > 0 else None
            amount = m.group(r.rg_amount) if r.rg_amount > 0 else None
            keyword = m.group(r.rg_keyword) if r.rg_keyword > 0 else None

            if keyword is not None:
                keyword = keyword.lower()
                lg.debug("eval_message(): keyword %s", keyword)
                if keyword == 'all':
                    amount = 'all'
                else:
                    amount  = ctb.conf.keywords[keyword].value
                    if type(amount) == str:
                        amount = eval(amount)
                    elif type(amount) == float:
                        amount = Decimal(amount)

            if ((to_addr == None) and (r.action == 'givetip')):
                lg.debug("eval_message(): can't tip with no to_addr")
                return None


            # Return CtbAction instance with given variables
            return CtbAction(   atype=type,
                                msg=None,
                                from_user=from_user,
                                to_user=None,
                                to_addr=to_addr,
                                coin='dog',
                                coin_val=amount if not r.fiat else None,
                                fiat=r.fiat,
                                fiat_val=amount if r.fiat else None,
                                keyword=keyword,
                                fullname = fullname,
                                deleted_created_utc = created_utc,
                                deleted_msg_id= id,
                                permalink=permalink,
                                ctb=ctb)

    # No match found
    lg.debug("eval_message(): no match found")
    return None


def eval_comment(comment, ctb):
    """
    Evaluate comment body and  and insert into the pending_action
    database if successful
    """
    lg.debug("> eval_comment()")

    body = comment.body
    for r in ctb.runtime['regex']:
        # Skip non-public actions
        
        if not ctb.conf.regex.actions[r.action].public:
            continue

        # Attempt a match
        rg = re.compile(r.regex, re.IGNORECASE|re.DOTALL)
        lg.debug("eval_comment(): matching '%s' with <%s>", comment.body, r.regex)
        m = rg.search(body)

        if m:
            # Match found
            lg.debug("eval_comment(): match found")

            # Extract matched fields into variables
            u_to = m.group(r.rg_to_user)[1:] if r.rg_to_user > 0 else None
            to_addr = m.group(r.rg_address) if r.rg_address > 0 else None
            amount = m.group(r.rg_amount) if r.rg_amount > 0 else None
            keyword = m.group(r.rg_keyword) if r.rg_keyword > 0 else None
            verify = m.group(r.rg_verify) if r.rg_verify > 0 else None
            if keyword is not None:
                keyword = keyword.lower()
                lg.debug("eval_message(): keyword %s", keyword)
                if keyword == 'all':
                    amount = 'all'
                else:
                    amount = ctb.conf.keywords[keyword].value
                    if type(amount) == str:
                        amount = eval(amount)
                    elif type(amount) == float:
                        amount = Decimal(amount)
            # If no destination mentioned, find parent submission's author
            if not u_to and not to_addr:
                # set u_to to author of parent comment
                parentcomment = ctb_misc.praw_call(ctb.reddit.get_info, thing_id=comment.parent_id)
                #parentcomment = ctb.reddit.get_info(thing_id=comment.parent_id)
                u_to = parentcomment.author
                if u_to is not None:
                    u_to = parentcomment.author.name
                else:
                    # couldn't determine u_to, giving up
                    lg.warning("eval_comment(): couldn't find u_to")
                    return None

            # Check if from_user == to_user
            if u_to and comment.author.name.lower() == u_to.lower():
                lg.warning("eval_comment(): comment.author.name == u_to, ignoring comment")
                return None
                
            # Check if subreddit == promos
            if comment.subreddit == 'promos':
                return None

            # Return CtbAction instance with given variables
            lg.debug("eval_comment(): creating action %s: to_user=%s, to_addr=%s, amount=%s, coin=%s, fiat=%s" % (r.action, u_to, to_addr, amount, r.coin, r.fiat))
            #lg.debug("< eval_comment() DONE (yes)")
            if verify:
                lg.info("appending verify with this: %s",verify)
            return CtbAction(   atype=r.action,
                                msg=comment,
                                to_user=u_to,
                                to_addr=to_addr,
                                coin=r.coin,
                                verify=verify,
                                coin_val=amount if not r.fiat else None,
                                fiat=r.fiat,
                                fiat_val=amount if r.fiat else None,
                                keyword=keyword,
                                subr=comment.subreddit,
                                ctb=ctb)

    # No match found
    lg.debug("< eval_comment() DONE (no match)")
    return None


def eval_pull_message(msg, ctb):
    """
    Turn the Message from the pull queue into an action
    """
    lg.debug("> eval_pull_message()")
    queue_id = msg['id'] if 'id' in msg else ''
    reservation_id = msg['reservation_id'] if 'reservation_id' in msg else ''
    message = json.loads(msg['body'])
    lg.debug(">eval_pull_message() %s", message)
    service = message.get('service', None)
    if service != 'reddit' or service is None:
        lg.debug('eval_pull_message() SERVICE NOT REDDIT')
        return False

    is_new_shibe = message.get('is_new_shibe', None)
    verify = message.get('config5', None)
    fullname = message.get('config2', None)
    comment = None
    if fullname:
        comment = ctb_misc.praw_call(ctb.reddit.get_info, thing_id=fullname)
        #comment = ctb.reddit.get_info(thing_id=fullname)
        if comment:
            subreddit = comment.subreddit
        else:
            subreddit = None
    else:
        comment = None
        subreddit = None
    u_from = message.get('u_from', None)
    u_to = message.get('u_to', None)
    action = message.get('command', None)
    coin = 'dog'
    amount = message.get('coinval', None)
    to_addr = message.get('addr_to', None)
    msg_type = message.get('type', None)
    txid = message.get('txid', None)
    addr_from = message.get('addr_from', None)
    total_doge_sent = message.get('total_doge_sent', None)
    total_doge_received = message.get('total_doge_received', None)
    history = message.get('history', [])
    associated = message.get('associated', None)
    balance = message.get('balance', None)
    fiatval = message.get('fiatval', None)
    total_fiat_received = message.get('total_fiat_received', 0)
    total_fiat_sent = message.get('total_fiat_sent', 0)

    return CtbAction(
        atype=action,
        from_user=u_from,
        msg=comment,
        to_user=u_to,
        to_addr=to_addr,
        coin=coin,
        verify=verify,
        coin_val=amount,
        subr = subreddit,
        is_pull_queue = True,
        is_new_shibe = is_new_shibe,
        msg_type = msg_type,
        txid = txid,
        addr_from = addr_from,
        total_doge_sent = total_doge_sent,
        total_doge_received = total_doge_received,
        history_list = history,
        associated=associated,
        balance=balance,
        fiat_val=fiatval,
        queue_id=queue_id,
        reservation_id = reservation_id,
        total_fiat_received=total_fiat_received,
        total_fiat_sent=total_fiat_sent,
        ctb=ctb)