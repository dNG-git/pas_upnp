# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.variable
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;upnp

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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from struct import pack, unpack
from time import localtime, strftime
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.pythonback import direct_bytes, direct_str

class direct_variable(object):
#
	"""
The UPnP service action callable.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	RE_NODE_NAME_XMLNS = re.compile("^(.+?):(\\w+)$")
	RE_UUID = re.compile("^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$")

	@staticmethod
	def get_native_type(xml_parser, xml_node):
	#
		"""
Returns a native type definition for the dataType identified.
		"""

		if (isinstance(xml_node, dict) and "value" in xml_node):
		#
			var_return = str

			if ("attributes" in xml_node and "type" in xml_node['attributes']):
			#
				if (xml_node['attributes']['type'].startswith("urn:")): var_return = ( str, "xmlns", xml_node['attributes']['type'] )
				else:
				#
					re_result = direct_variable.RE_NODE_NAME_XMLNS.match(xml_node['attributes']['type'])
					uri = xml_parser.ns_get_uri(xml_node['attributes']['type'])

					if (re_result == None or uri == ""): var_return = False
					else: var_return = ( str, "xmlns", "{0}:{1}".format(uri, re_result.group(2)) )
				#
			#
			elif (xml_node['value'] == "bin.base64"): var_return = ( str, "base64" )
			elif (xml_node['value'] == "bin.hex"): var_return = ( str, "hex" )
			elif (xml_node['value'] == "i1"): var_return = ( int, "b" )
			elif (xml_node['value'] == "i2"): var_return = ( int, "h" )
			elif (xml_node['value'] == "i4" or xml_node['value'] == "int"): var_return = int
			elif (xml_node['value'] == "r4"): var_return = ( float, "f" )
			elif (xml_node['value'] == "r8" or xml_node['value'] == "float" or xml_node['value'] == "number"): var_return = float
			elif (xml_node['value'] == "fixed.14.4"): var_return = ( float, "f14.4" )
			elif (xml_node['value'] == "char"): var_return = ( str, "c" )
			elif (xml_node['value'] == "date"): var_return = ( int, "date" )
			elif (xml_node['value'] == "dateTime"): var_return = ( int, "dateTime" )
			elif (xml_node['value'] == "dateTime.tz"): var_return = ( int, "dateTime.tz" )
			elif (xml_node['value'] == "time"): var_return = ( int, "time" )
			elif (xml_node['value'] == "time.tz"): var_return = ( int, "time.tz" )
			elif (xml_node['value'] == "boolean"): var_return = bool
			elif (xml_node['value'] == "ui1"): var_return = ( int, "B" )
			elif (xml_node['value'] == "ui2"): var_return = ( int, "H" )
			elif (xml_node['value'] == "ui4"): var_return = ( int, "I" )
			elif (xml_node['value'] == "uri"): var_return = ( str, "uri" )
			elif (xml_node['value'] == "uuid"): var_return = ( str, "uuid" )
		#
		else: var_return = False

		return var_return
	#

	# strictEqual(Date.parse('-010000-02-03T04:05'), Date.UTC(-10000, 1, 3, 4, 5, 0, 0), '-010000-02-03T04:05');

	@staticmethod
	def get_upnp_value(name, variable, value):
	#
		"""
Returns a native type definition for the dataType identified.
		"""

		if (type(variable['type']) == tuple):
		#
			value_normalized = (direct_str(value) if (variable['type'][0] == str) else value)
			var_type = type(value_normalized)

			if (var_type != variable['type'][0]): raise TypeError("Given value mismatches defined format for '{0}'".format(name))
			elif (len(variable['type']) > 2):
			#
				pass
			#
			elif (len(variable['type'][1]) > 1):
			#
				if (variable['type'][1] == "base64"): var_return = direct_str(b64encode(direct_bytes(value) if (value == value_normalized) else value))
				elif (variable['type'][1] == "f14.4"): var_return = "{0:14.4g}".format(value).strip()
				elif (variable['type'][1] == "date"): var_return = strftime("%Y-%m-%d", localtime(value))
				elif (variable['type'][1] == "dateTime"): var_return = strftime("%Y-%m-%dT%H:%M:%S", localtime(value))
				elif (variable['type'][1] == "dateTime.tz"): var_return = strftime("%Y-%m-%dT%H:%M:%S%z", localtime(value))
				elif (variable['type'][1] == "hex"): var_return = direct_str(hexlify(direct_bytes(value) if (value == value_normalized) else value))
				elif (variable['type'][1] == "time"): var_return = strftime("%H:%M:%S", localtime(value))
				elif (variable['type'][1] == "time.tz"): var_return = strftime("%H:%M:%S%z", localtime(value))
				elif (variable['type'][1] == "uri" and len(urlsplit(value).scheme.strip()) < 1): raise TypeError("Given value is not a valid URI for '{0}'".format(name))
				elif (variable['type'][1] == "uuid" and direct_variable.RE_UUID.match(value_normalized) == None): raise TypeError("Given value is not a valid UUID for '{0}'".format(name))
				else: var_return = value_normalized
			#
			else:
			#
				pack("={0}".format(variable['type'][1]), (direct_bytes(value) if (var_type == str and value == value_normalized) else value))
				var_return = "{0}".format(value_normalized)
			#
		#
		else:
		#
			if (variable['type'] == str): value = direct_str(value)
			var_type = type(value)

			if (var_type != variable['type']): raise TypeError("Given value mismatches defined format for '{0}'".format(name))
			elif (variable['type'] == bool): var_return = "{0:b}".format(value)
			elif (variable['type'] == int): var_return = "{0:d}".format(value)
			elif (variable['type'] == float): var_return = "{0:f}".format(value)
			else: var_return = value
		#

		return var_return
	#
#

##j## EOF