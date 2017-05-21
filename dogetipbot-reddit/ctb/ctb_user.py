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

import ctb_misc

import logging, time, praw, re

from decimal import *

lg = logging.getLogger('cointipbot')

class CtbUser(object):
    """
    User class for cointip bot
    """

    # Basic properties
    name=None
    giftamount=None
    joindate=None
    addr={}
    banned=False

    # Objects
    prawobj=None
    ctb=None

    def __init__(self, name=None, redditobj=None, ctb=None):
        """
        Initialize CtbUser object with given parameters
        """
        #lg.debug("> CtbUser::__init__(%s)", name)

        if not bool(name):
            raise Exception("CtbUser::__init__(): name must be set")
        self.name = name

        if not bool(ctb):
            raise Exception("CtbUser::__init__(): ctb must be set")
        self.ctb = ctb

        if bool(redditobj):
            self.prawobj = redditobj

        # Determine if user is banned
        if ctb.conf.reddit.banned_users:
            if ctb.conf.reddit.banned_users.method == 'subreddit':
                for u in ctb.reddit.get_banned(ctb.conf.reddit.banned_users.subreddit):
                    if self.name.lower() == u.name.lower():
                        self.banned = True
            elif ctb.conf.reddit.banned_users.method == 'list':
                for u in ctb.conf.reddit.banned_users.list:
                    if self.name.lower() == u.lower():
                        self.banned = True
            else:
                lg.warning("CtbUser::__init__(): invalid method '%s' in banned_users config" % ctb.conf.reddit.banned_users.method)

        #lg.debug("< CtbUser::__init__(%s) DONE", name)

    def __str__(self):
        """
        Return string representation of self
        """
        me = "<CtbUser: name=%s, giftamnt=%s, joindate=%s, addr=%s, redditobj=%s, ctb=%s, banned=%s>"
        me = me % (self.name, self.giftamount, self.joindate, self.addr, self.prawobj, self.ctb, self.banned)
        return me



    def is_on_reddit(self):
        """
        Return true if username exists Reddit. Also set prawobj pointer while at it.
        """
        lg.debug("> CtbUser::is_on_reddit(%s)", self.name)

        # Return true if prawobj is already set
        if bool(self.prawobj):
            lg.debug("< CtbUser::is_on_reddit(%s) DONE via OBJ SET (yes)", self.name)
            return True


        self.prawobj = ctb_misc.praw_call(self.ctb.reddit.get_redditor, self.name)
        if self.prawobj:
            return True
        else:
            return False

        #except Exception as e:
            #lg.debug("< CtbUser::is_on_reddit(%s) DONE (no)", self.name)
            #return False

        lg.warning("< CtbUser::is_on_reddit(%s): returning None (shouldn't happen)", self.name)
        return None


    def tell(self, subj=None, msg=None, msgobj=None):
        """
        Send a Reddit message to user
        """
        lg.debug("> CtbUser::tell(%s)", self.name)

        if not bool(subj) or not bool(msg):
            raise Exception("CtbUser::tell(%s): subj or msg not set", self.name)


        #This should not happen ever
        if not self.is_on_reddit():
            #raise Exception("CtbUser::tell(%s): not a Reddit user", self.name)
            return None

        if bool(msgobj):
            lg.debug("CtbUser::tell(%s): replying to message", msgobj.id)
            ctb_misc.praw_call(msgobj.reply, msg)
        else:
            lg.debug("CtbUser::tell(%s): sending message", self.name)
            ctb_misc.praw_call(self.prawobj.send_message, subj, msg)

        lg.debug("< CtbUser::tell(%s) DONE", self.name)
        return True

    def register(self):
        """
        Add user to database and generate coin addresses
        """
        lg.debug("> CtbUser::register(%s)", self.name)




        lg.debug("< CtbUser::register(%s) DONE", self.name)
        return True

