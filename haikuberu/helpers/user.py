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
from decimal import *
from os import urandom
from iron_cache import *
from math import trunc
import json, os, sys, logging, re, time, yaml, db, misc, datetime, hkservice

logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger('haikuberu')



class HkUser(object):

    # Objects
    haikuberu  = None

    # Basic properties
    username   = None
    service    = None
    service_id = None
    user_id    = None
    giftamount = None
    joindate   = None
    addr       = {}
    usernames  = {}


    
    # String representation of the object
    def __str__(self):
        me = "<HkUser: usernames=%s, giftamnt=%s, joindate=%s, addr=%s, haikuberu=%s, user_id=%s>"
        me = me % (self.usernames, self.giftamount, self.joindate, self.addr, self.haikuberu, self.user_id)
        return me



    # Initialize user object
    def __init__(self, haikuberu = None, service = None, username = None):

        # Ensure haikuberu instance was set
        if not bool(haikuberu):
            raise Exception("HkUser::__init__(): haikuberu must be set")
        self.haikuberu = haikuberu

        # Ensure username is set
        if not bool(username):
            raise Exception("HkUser::__init__(): name must be set")
        self.username = username

        # Ensure service name is set
        if not bool(service):
            raise Exception("HkUser::__init__(): service must be set")
        self.service = service
        
        # Ensure service name maps to a service_id
        self.service_id = hkservice.HkService(self.haikuberu).get_from_name(self.service)
        
        # Get user_id based on service and username
        try:
            self.user_id = misc.get_user_id(self.haikuberu, self.service_id, self.username)
        except:
            lg.debug("< HkUser::No user ID found")



    # Get user history
    def get_history(self):
        
        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::get_history(%s): user_id must be set first" % self.username)

        sqlcmd = "CALL GetUserHistory(%s, 50, 1)"
        sqlrows = self.haikuberu.db.execute(sqlcmd, (self.user_id))
        if sqlrows == None:
            lg.debug("< HkUser::get_history(%s, %s) FAILED SHOULDNT HAPPEN O SHIT ")
            return []
        else:
            lg.debug("Returned Rows %s", sqlrows)
            ret = []
            for row in sqlrows:
                lg.debug("< HkUser:get_history : history added %s", row)
                row = dict(row.items())
                row['coin_val'] = str(row['coin_val'])
                row['fiat_val'] = str(row['fiat_val'])
                row['coin'] = str(row['coin'])
                row['fiat'] = str(row['fiat'])
                row['timestamp'] = str(row['timestamp'])
                ret.append(row)
            return list(ret)



    # Get the coin balance
    def get_balance(self, coin = None):
        
        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::balance(%s): user_id must be set first" % self.username)
        
        # Check that a coin type is set
        if not bool(coin):
            raise Exception("HkUser::balance(%s): coin not set" % self.username)

        lg.info("HkUser::balance(%s): getting %s balance", self.user_id, coin)
        
        # Get balance from DB
        sql = "SELECT balance from address WHERE user_id = %s AND coin = %s"
        mysqlrow = self.haikuberu.db.execute(sql, (self.user_id, coin)).fetchone()
        
        # Check for result
        if mysqlrow == None or mysqlrow['balance'] == None:
            lg.debug("< HkUser::this should never happen")
            raise Exception("HkUser::balance(%s) balance not found" % self.username)
        else:
            currentbalance = (mysqlrow['balance'])
        
        # Return the balance
        return currentbalance


    # Total sent
    def total_sent(self):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::add_coin(%s): user_id must be set first" % self.username)

        # Get balance and add
        sqlcmd = "SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = " + str(int(self.user_id)) + " AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND action.type='givetip' "

        # Get balance
        total = self.haikuberu.get_field(sqlcmd)
        
        if total:
            total = Decimal(total)
        else:
            total = 0
        
        return Decimal(Decimal(trunc(total * 100000000)) / 100000000)



    # Total fiat sent
    def total_fiat_sent(self):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::add_coin(%s): user_id must be set first" % self.username)

        # Get balance and add
        sqlcmd = "SELECT SUM(action.fiat_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = " + str(int(self.user_id)) + " AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND action.type='givetip' "

        # Get balance
        total = self.haikuberu.get_field(sqlcmd)
        
        if total:
            total = Decimal(total)
        else:
            total = 0
        
        return Decimal(Decimal(trunc(total * 100000000)) / 100000000)



    # Total sent
    def total_received(self):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::add_coin(%s): user_id must be set first" % self.username)

        # Get balance and add
        sqlcmd = "SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = " + str(int(self.user_id)) + " AND action.to_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND action.type='givetip' "

        # Get balance
        total = self.haikuberu.get_field(sqlcmd)
        
        if total:
            total = Decimal(total)
        else:
            total = 0
        
        return Decimal(Decimal(trunc(total * 100000000)) / 100000000)



    # Total sent
    def total_fiat_received(self):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::add_coin(%s): user_id must be set first" % self.username)

        # Get balance and add
        sqlcmd = "SELECT SUM(action.fiat_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = " + str(int(self.user_id)) + " AND action.to_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND action.type='givetip' "

        # Get balance
        total = self.haikuberu.get_field(sqlcmd)
        
        if total:
            total = Decimal(total)
        else:
            total = 0
        
        return Decimal(Decimal(trunc(total * 100000000)) / 100000000)



    # Add coins
    def add_coin(self, coin = None, amount = 0):
        
        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::add_coin(%s): user_id must be set first" % self.username)
        
        # Check that a coin type is set
        if not bool(coin):
            raise Exception("HkUser::add_coin(%s): coin not set" % self.username)

        # Check that the balance is greater than 0
        if amount <= 0:
            raise Exception("HkUser::add_coin(%s): amount less than or equal to zero" % self.username)

        # Amount should only have a precision of 8
        amount = Decimal(Decimal(trunc(amount * 100000000)) / 100000000)

        # Get balance and add
        newbal = Decimal(trunc((Decimal(self.get_balance(coin)) + Decimal(amount)) * 100000000)) / 100000000

        # Update balance
        sqlcmd = "UPDATE address SET balance = %s WHERE user_id = %s AND coin = %s"
        sqlinsert = self.haikuberu.db.execute(sqlcmd, (newbal, self.user_id, coin))
        lg.info("< HAIKUBERU INFO :: BALANCE UPDATE FOR %s", self.user_id)

        # Return new balance
        return newbal



    # Sub coins
    def sub_coin(self, coin = None, amount = 0):
        
        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::sub_coin(%s): user_id must be set first" % self.username)
        
        # Check that a coin type is set
        if not bool(coin):
            raise Exception("HkUser::sub_coin(%s): coin not set" % self.username)

        # Check that the balance is greater than 0
        if amount <= 0:
            raise Exception("HkUser::sub_coin(%s): amount less than or equal to zero" % self.username)

        # Amount should only have a precision of 8
        amount = Decimal(Decimal(trunc(amount * 100000000)) / 100000000)

        # Get balance and add
        newbal = Decimal(trunc((Decimal(self.get_balance(coin)) - Decimal(amount)) * 100000000)) / 100000000

        # Make sure the new balance is greater than zero
        if newbal < 0:
            raise Exception("HkUser::sub_coin(%s): new balance is less than zero" % self.username)

        # Update balance
        sqlcmd = "UPDATE address SET balance = %s WHERE user_id = %s AND coin = %s"
        sqlinsert = self.haikuberu.db.execute(sqlcmd, (newbal, self.user_id, coin))
        lg.info("< HAIKUBERU INFO :: BALANCE UPDATE FOR %s", self.user_id)

        # Return new balance
        return newbal


    
    # Get coin address
    def get_addr(self, coin=None):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::get_addr(%s): user_id must be set first" % self.username)
        
        # Check if the address has already been loaded
        if hasattr(self.addr, coin):
            return self.addr[coin]

        lg.debug("> HkUser::get_addr(%s, %s)", self.user_id, coin)

        # Load address from database
        sql = "SELECT address from address WHERE user_id = %s AND coin = %s"
        mysqlrow = self.haikuberu.db.execute(sql, (self.user_id, coin.lower())).fetchone()
        if mysqlrow == None:
            lg.debug("< HkUser::get_addr(%s, %s) DONE (no)", self.user_id, coin)
            raise Exception("HKUser::get_addr() no address found")
        else:
            self.addr[coin] = mysqlrow['address']
            lg.debug("< HkUser::get_addr(%s, %s) DONE (%s)", self.user_id, coin, self.addr[coin])
            return self.addr[coin]



    # Delete a user
    def delete_user(self):

        # Check that a user_id is set
        if not bool(self.user_id):
            raise Exception("HkUser::get_addr(%s): user_id must be set first" % self.username)

        # Remove user record from database
        sql = "DELETE FROM user WHERE user_id = %s"
        mysqlexec = self.haikuberu.db.execute(sql, self.user_id)
        if mysqlexec.rowcount <= 0:
            lg.warning("delete_user(%s): rowcount <= 0 while executing <%s>", self.user_id, sql % self.user_id)

        lg.debug("< delete_user(%s) DONE", self.user_id)
        return True



    # Register a user
    def register(self):
        
        # Debug
        lg.debug("< HkUser::register(%s) START", self.username)

        # Check that a user_id is not already set
        lg.debug("> HkUser::register(%s)", self.username)
        if bool(self.user_id):
            raise Exception("HkUser::register(%s): user_id must not be set" % self.username)
        
        # Start transaction
        trans = self.haikuberu.db.begin()
        try:
            # Insert user and get primary key
            mysqlexec = self.haikuberu.db.execute("INSERT INTO user (joindate) VALUES (NOW())")
            self.user_id = int(mysqlexec.lastrowid)
            
            # Insert username
            sql_addusername = "INSERT INTO username (service_id, username, user_id) VALUES (%s, %s, %s)"
            mysqlexec = self.haikuberu.db.execute(sql_addusername, (self.service_id, self.username.lower(), self.user_id))

            # Insert address
            # @todo multiple coin type address support
            coin = 'dog'
            wallet_name = self.username.lower() + ':' + str(self.user_id)
            
            # Generate address
            new_address = self.haikuberu.coins['dog'].getnewaddr(_user=wallet_name)

            sql_addr = "INSERT INTO address (user_id, coin, address, balance, wallet_name) VALUES (%s, %s, %s, 0, %s)"
            mysqlexec = self.haikuberu.db.execute(sql_addr, (self.user_id, coin, new_address, wallet_name))

            # All good, commit
            trans.commit()
        except:
            # Something bad happened, roll back
            trans.rollback()
            lg.debug("< HkUser::register(%s) Insert error - Rolling back", self.username)
            raise

        lg.debug("< HkUser::register(%s) DONE", self.username)
        return self



    # Check is user is new
    def is_new_user(self):
        sql = "SELECT joindate, DATEDIFF(joindate, NOW()) AS `days` FROM user WHERE user_id = %s"
        mysqlexec = self.haikuberu.db.execute(sql, self.user_id).fetchone()
        if mysqlexec is None:
            return True
        else:
            return (abs(int(mysqlexec['days'])) <= 7)



    def delete_username(self):
        """
        Delete _username from t_users and t_addrs tables
        """
        lg.debug("> delete_username(%s)", self.name)

        try:
            sql = "DELETE FROM usernames WHERE username = %s"

            mysqlexec = self.haikuberu.db.execute(sql, self.name.lower())
            if mysqlexec.rowcount <= 0:
                lg.warning("delete_username(%s): rowcount <= 0 while executing <%s>", self.name, sql % self.name.lower())

        except Exception, e:
            lg.error("delete_username(%s): error while executing <%s>: %s", self.name, sql % self.name.lower(), e)
            return False

        lg.debug("< delete_username(%s) DONE", self.name)
        return True


    
    # Check if a user is registered
    def is_registered(self):
        """
        Return true if user is registered with Haikuberu
        """
        #lg.debug("> HkUser::is_registered(%s)", self.user_id)
        if not bool(self.user_id):
            lg.debug("< HkUser is_registered(): USER IS NOT REGISTERED")
            return False
        else:
            lg.debug("< HkUser is_registered(): USER IS REGISTERED")
            return True


    def get_usernames(self):
        '''
        Sets the usernames variable to a dict of services + usernames
        '''

        if not bool(self.user_id):
            lg.debug("< HkUser:get_usernames() Failed: No user_id set")
            return None

        sqlcmd = "SELECT username.username, service.service_name FROM username JOIN service ON service.service_id = username.service_id WHERE username.user_id = %s ORDER BY username.username_id ASC"
        sqlrows = self.haikuberu.db.execute(sqlcmd, (self.user_id))
        if sqlrows == None:
            lg.debug("< HkUser::get_usernames(%s, %s) FAILED SHOULDNT HAPPEN O SHIT ")
            return None
        else:
            lg.debug("Returned Rows %s", sqlrows)
            ret = []
            for row in sqlrows:
                lg.debug("< HkUser:get_usernames : Username found %s", row)
                ret.append({
                    'username' : row['username'],
                    'service_name' : row['service_name']
                })
            return list(ret)
