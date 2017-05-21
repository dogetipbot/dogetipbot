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
import user
import logging, time
from socket import timeout

lg = logging.getLogger('haikuberu')


class DotDict(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [DotDict(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, DotDict(b) if isinstance(b, dict) else b)
    def __getitem__(self, val):
        return getattr(self, val)
    def has_key(self, key):
        return hasattr(self, key)


def get_user_id(haikuberu, service, username):
    '''uses service + username to look up user_id'''
    try:

        lg.debug("> Misc:get_user_id(%s, %s)",service, username)
        sql = "SELECT user_id FROM username WHERE service_id = %s AND username = %s"
        mysqlexec = haikuberu.db.execute(sql, (service, username.lower())).fetchone()
        if mysqlexec is None:
            lg.debug("Misc:get_user_id RETURNED NONE NO USER FOUND")
            raise ValueError("Misc:get_user_id RETURNED NONE NO USER FOUND");
        else:
            for row in mysqlexec:
                lg.debug('Misc:get_user_id: USER_ID RETURNED: %s', row)
                return mysqlexec['user_id']
    except Exception as e:
        lg.debug("Misc:get_user_id:error executing %s", sql)
        raise