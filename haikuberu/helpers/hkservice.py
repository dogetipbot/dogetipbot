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
import logging

logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger('haikuberu')

class HkService(object):

    haikuberu = None

    
    
    def __init__(self, haikuberu):
        self.haikuberu = haikuberu
    
    
    
    def get_from_name(self, service_name = None):
    
        sql = "SELECT service_id FROM service WHERE service_name = %s"
        mysqlexec = self.haikuberu.db.execute(sql, service_name).fetchone()
        
        if mysqlexec is None:
            lg.debug("Misc:get_from_name RETURNED NONE NO SERVICE FOUND")
            raise ValueError('Service name not found')
        else:
            return int(mysqlexec['service_id'])
        