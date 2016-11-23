# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;upnp

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,no-name-in-module

from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from struct import pack
from time import localtime, strftime
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.data.binary import Binary
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.runtime.value_exception import ValueException

class Variable(object):
    """
This class provides static methods to convert variables between the native
and the UPnP format.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    BOOL_TRUE = "1"
    """
String representation for True
    """
    BOOL_FALSE = "0"
    """
String representation for false
    """
    RE_NODE_NAME_XMLNS = re.compile("^(.+):(\\w+)$")
    """
RegEx for "*:*" node attributes
    """
    RE_UUID = re.compile("^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$")
    """
RegEx for UUIDs
    """

    @staticmethod
    def get_native(native_type, value):
        """
Returns the native value for the given variable definition and UPnP encoded
value.

:param native_type: Native type definition
:param value: Native python value

:return: (str) UPnP encoded value
:since:  v0.2.00
        """

        if (type(native_type) is tuple):
            if (native_type[1] == "xmlns"): _return = value
            elif (native_type[1] == "base64"): _return = Binary.raw_str(b64decode(Binary.utf8_bytes(value)))
            elif (native_type[1] == "date"): _return = RfcBasics.get_iso8601_timestamp(value, has_time = False)
            elif (native_type[1] == "dateTime"): _return = RfcBasics.get_iso8601_timestamp(value, has_timezone = False)
            elif (native_type[1] == "dateTime.tz"): _return = RfcBasics.get_iso8601_timestamp(value)
            elif (native_type[1] == "hex"): _return = Binary.raw_str(unhexlify(Binary.utf8_bytes(value)))
            elif (native_type[1] == "time"): _return = RfcBasics.get_iso8601_timestamp(value, False, has_timezone = False)
            elif (native_type[1] == "time.tz"): _return = RfcBasics.get_iso8601_timestamp(value, False)
            elif (native_type[1] == "uri" and re.match("^\\w+\\:\\w", value) is None): raise ValueException("Given value mismatches defined format for URIs")
            elif (native_type[1] == "uuid" and (not value.startswith("uuid:"))): raise ValueException("Given value mismatches defined format for UUIDs")
            elif (native_type[0] is not str): _return = native_type[0](value)
        elif (native_type is not str): _return = native_type(value)
        else: _return = value

        return _return
    #

    @staticmethod
    def get_native_type(variable):
        """
Returns a native type definition for the dataType identified for the given
variable definition.

:param variable: Variable definition

:return: (mixed) Native type definition
:since: v0.2.00
        """

        if (isinstance(variable, dict) and "type" in variable):
            _return = str

            if (variable['type'] == "bin.base64"): _return = ( str, "base64" )
            elif (variable['type'] == "bin.hex"): _return = ( str, "hex" )
            elif (variable['type'] == "i1"): _return = ( int, "b" )
            elif (variable['type'] == "i2"): _return = ( int, "h" )
            elif (variable['type'] == "i4"): _return = int
            elif (variable['type'] in ( "i8", "int" )): _return = ( int, "q" )
            elif (variable['type'] == "r4"): _return = ( float, "f" )
            elif (variable['type'] in ( "r8", "float", "number" )): _return = float
            elif (variable['type'] == "fixed.14.4"): _return = ( float, "f14.4" )
            elif (variable['type'] == "char"): _return = ( str, "c" )
            elif (variable['type'] == "date"): _return = ( int, "date" )
            elif (variable['type'] == "dateTime"): _return = ( int, "dateTime" )
            elif (variable['type'] == "dateTime.tz"): _return = ( int, "dateTime.tz" )
            elif (variable['type'] == "time"): _return = ( int, "time" )
            elif (variable['type'] == "time.tz"): _return = ( int, "time.tz" )
            elif (variable['type'] == "boolean"): _return = bool
            elif (variable['type'] == "ui1"): _return = ( int, "B" )
            elif (variable['type'] == "ui2"): _return = ( int, "H" )
            elif (variable['type'] == "ui4"): _return = ( int, "I" )
            elif (variable['type'] == "ui8"): _return = ( int, "Q" )
            elif (variable['type'] == "uri"): _return = ( str, "uri" )
            elif (variable['type'] == "uuid"): _return = ( str, "uuid" )
            elif (variable['type'] == "xmlns" and "type_xmlns" in variable): _return = ( str, "xmlns", variable['type_xmlns'] )
        else: _return = False

        return _return
    #

    @staticmethod
    def get_native_type_from_xml(xml_parser, xml_node):
        """
Returns a native type definition for the dataType identified at the given
XML node.

:param xml_parser: XML parser instance
:param xml_node: XML node to parse

:return: (mixed) Native type definition
:since: v0.2.00
        """

        if (isinstance(xml_node, dict) and "value" in xml_node):
            _return = False

            if ("attributes" in xml_node and "type" in xml_node['attributes']):
                if (xml_node['attributes']['type'].startswith("urn:")): _return = _return = Variable.get_native_type({ "type": "xmlns", "type_xmlns": xml_node['attributes']['type'] })
                else:
                    re_result = Variable.RE_NODE_NAME_XMLNS.match(xml_node['attributes']['type'])
                    uri = xml_parser.get_ns_uri(xml_node['attributes']['type'])

                    if (re_result is not None and uri != ""): _return = _return = Variable.get_native_type({ "type": "xmlns", "type_xmlns": "{0}:{1}".format(uri, re_result.group(2)) })
                #
            else: _return = Variable.get_native_type({ "type": xml_node['value'] })
        else: _return = False

        return _return
    #

    @staticmethod
    def get_upnp_duration(value):
        """
Returns a valid UPnP encoded duration for the given value.

:param value: Native value as int or float

:return: (str) UPnP encoded value
:since:  v0.2.00
        """

        seconds = int(value % 60)
        minutes = (0 if (value < 60) else int(value / 60))

        if (minutes < 60): hours = 0
        else:
            hours = int(minutes / 60)
            minutes = int(minutes % 60)
        #

        return "{0:0=2d}:{1:0=2d}:{2:0=7.4f}".format(hours, minutes, seconds + round(value % 1, 4))
    #

    @staticmethod
    def get_upnp_value(variable, value):
        """
Returns a valid UPnP encoded value for the given variable definition and
value.

:param variable: Variable definition
:param value: Native python value

:return: (str) UPnP encoded value
:since:  v0.2.00
        """

        native_type = Variable.get_native_type(variable)

        if (type(native_type) is tuple):
            value_normalized = (Binary.str(value) if (native_type[0] == str) else value)
            value_normalized_type = type(value_normalized)

            if (value_normalized_type != native_type[0]): raise ValueException("Given value mismatches defined format")
            elif (len(native_type) > 2):
                if (native_type[1] != "xmlns"): raise ValueException("Invalid native type definition")
                _return = value_normalized
            elif (len(native_type[1]) > 1):
                if (native_type[1] == "base64"): _return = Binary.str(b64encode(Binary.bytes(value) if (value == value_normalized) else value))
                elif (native_type[1] == "f14.4"): _return = "{0:14.4g}".format(value).strip()
                elif (native_type[1] == "date"): _return = strftime("%Y-%m-%d", localtime(value))
                elif (native_type[1] == "dateTime"): _return = strftime("%Y-%m-%dT%H:%M:%S", localtime(value))
                elif (native_type[1] == "dateTime.tz"): _return = strftime("%Y-%m-%dT%H:%M:%S%Z", localtime(value))
                elif (native_type[1] == "hex"): _return = Binary.str(hexlify(Binary.bytes(value) if (value == value_normalized) else value))
                elif (native_type[1] == "time"): _return = strftime("%H:%M:%S", localtime(value))
                elif (native_type[1] == "time.tz"): _return = strftime("%H:%M:%S%Z", localtime(value))
                elif (native_type[1] == "uri" and len(urlsplit(value).scheme.strip()) < 1): raise ValueException("Given value is not a valid URI")
                elif (native_type[1] == "uuid" and Variable.RE_UUID.match(value_normalized) is None): raise ValueException("Given value is not a valid UUID")
                else: _return = value_normalized
            else:
                pack("={0}".format(native_type[1]),
                                   (Binary.utf8_bytes(value)
                                    if (value_normalized_type == str and value == value_normalized) else
                                    value
                                   )
                                  )

                _return = "{0}".format(value_normalized)
            #
        else:
            if (native_type is str): value = Binary.str(value)
            if (type(value) is not native_type): raise ValueException("Given value mismatches defined format")

            if (native_type is bool): _return = "{0:b}".format(value)
            elif (native_type is int): _return = str(value)
            elif (native_type is float): _return = "{0:f}".format(value)
            else: _return = value
        #

        return _return
    #
#
