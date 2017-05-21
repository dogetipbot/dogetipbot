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

# dogecoin address validation
# author: Atif Nazir a@block.io

import string
from hashlib import sha256

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def _bytes_to_long(bytestring, byteorder):
    """Convert a bytestring to a long

    For use in python version prior to 3.2
    """
    result = []
    if byteorder == 'little':
        result = (v << i * 8 for (i, v) in enumerate(bytestring))
    else:
        result = (v << i * 8 for (i, v) in enumerate(reversed(bytestring)))
    return sum(result)

def _long_to_bytes(n, length, byteorder):
    """Convert a long to a bytestring

    For use in python version prior to 3.2
    Source:
    http://bugs.python.org/issue16580#msg177208
    """
    if byteorder == 'little':
        indexes = range(length)
    else:
        indexes = reversed(range(length))
    return bytearray((n >> i * 8) & 0xff for i in indexes)

def decode_base58(bitcoin_address, length):
    """Decode a base58 encoded address

    This form of base58 decoding is bitcoind specific. Be careful outside of
    bitcoind context.
    """
    n = 0
    for char in bitcoin_address:
        try:
            n = n * 58 + __b58chars.index(char)
        except:
            msg = u"Character not part of Bitcoin's base58: '%s'"
            raise ValueError(msg % (char,))
    try:
        return n.to_bytes(length, 'big')
    except AttributeError:
        # Python version < 3.2
        return _long_to_bytes(n, length, 'big')

def encode_base58(bytestring):
    """Encode a bytestring to a base58 encoded string
    """
    # Count zero's
    zeros = 0
    for i in range(len(bytestring)):
        if bytestring[i] == 0:
            zeros += 1
        else:
            break
    try:
        n = int.from_bytes(bytestring, 'big')
    except AttributeError:
        # Python version < 3.2
        n = _bytes_to_long(bytestring, 'big')
    result = ''
    (n, rest) = divmod(n, 58)
    while n or rest:
        result += __b58chars[rest]
        (n, rest) = divmod(n, 58)
    return zeros * '1' + result[::-1]  # reverse string

def validate(bitcoin_address, magicbyte=0):
    """Check the integrity of a bitcoin address

    Returns False if the address is invalid.
    >>> validate('1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i')
    True
    >>> validate('')
    False
    """

    if isinstance(magicbyte, int):
        magicbyte = (magicbyte,)
    clen = len(bitcoin_address)

    if clen < 27 or clen > 35: # XXX or 34?
        return False
    allowed_first = tuple(string.digits)
    try:
        bcbytes = decode_base58(bitcoin_address, 25)
    except ValueError:
        return False

    # Check magic byte (for other altcoins, fix by Frederico Reiven)
    for mb in magicbyte:
        if bcbytes.startswith(chr(int(mb))):
            break
    else:
        return False


    # Compare checksum
    checksum = sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
    if bcbytes[-4:] != checksum:
        return False
    # Encoded bytestring should be equal to the original address,
    # for example '14oLvT2' has a valid checksum, but is not a valid btc
    # address
    return bitcoin_address == encode_base58(bcbytes)

def get_address_version(strAddress):
  """ Returns None if strAddress is invalid.  Otherwise returns integer version of address. """
  addr = decode_base58(strAddress,25)
  if addr is None: return None
  version = addr[0]

  return version

def is_dogecoin_address(addr):
  # returns false if the address is not a valid Dogecoin address

  vbyte = get_address_version(addr)

  if vbyte != 22 and vbyte != 30:
    return False

  # version byte is fine, let's check if the checksum is valid
  return validate(addr, vbyte)



#print is_dogecoin_address('9tVpQDnpftNT9qpWbP6gz3GE4Y3a94cmyt')
#print is_dogecoin_address('DFundmtrigzA6E25Swr2pRe4Eb79bGP8G1')
#print is_dogecoin_address('1HTL18EnUAgCjb8n2x3NN7bmVUmmDcnzBZ')