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
import logging, re, time, decimal
from pifkoin.bitcoind import Bitcoind, BitcoindException
from httplib import CannotSendRequest
from decimal import *

lg = logging.getLogger('cointipbot')

class CtbCoin(object):
    """
    Coin class for cointip bot
    """
    conn = None
    conf = None

    def __init__(self, _conf = None):
        """
        Initialize CtbCoin with given parameters. _conf is a coin config dictionary defined in conf/coins.yml
        """

        # verify _conf is a config dictionary
        if not _conf or not hasattr(_conf, 'name') or not hasattr(_conf, 'config_file') or not hasattr(_conf, 'txfee'):
            raise Exception("CtbCoin::__init__(): _conf is empty or invalid")

        self.conf = _conf


        lg.info("CtbCoin::__init__():: connected to %s", self.conf.name)
        time.sleep(0.5)












