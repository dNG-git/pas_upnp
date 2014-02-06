# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.HttpUpnpResponse
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

from collections import OrderedDict
from os import uname
from time import time

from dNG.data.xml_writer import XmlWriter
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.pas.data.binary import Binary
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.upnp_exception import UpnpException
from .abstract_http_response import AbstractHttpResponse

class HttpUpnpResponse(AbstractHttpResponse):
#
	"""
This response class returns UPnP compliant responses.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(HttpUpnpResponse)

:since: v0.1.00
		"""

		AbstractHttpResponse.__init__(self)

		self.client_user_agent = None
		"""
Client user agent
		"""
	#

	def client_set_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.1.00
		"""

		self.client_user_agent = user_agent
	#

	def init(self, cache = False, compress = True):
	#
		"""
Important headers will be created here. This includes caching, cookies, the
compression setting and information about P3P.

:param cache: Allow caching at client
:param compress: Send page GZip encoded (if supported)

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Response.init(cache, compress)- (#echo(__LINE__)#)")

		os_uname = uname()

		self.set_header("Content-Type", "text/xml; charset=UTF-8")
		self.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
		self.set_header("Server", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.50".format(os_uname[0], os_uname[2]))
	#

	def handle_result(self, urn, action, result):
	#
		"""
Returns a UPNP response for the given URN and SOAP action.

:param urn: UPnP URN called
:param action: SOAP action called
:param result: UPnP result arguments

:since: v0.1.00
		"""

		if (isinstance(result, Exception)):
		#
			if (isinstance(result, UpnpException)): self.send_error(result.get_upnp_code(), "{0:l10n_message}".format(result))
			else: self.send_error(501, L10n.get("errors_core_unknown_error"))
		#
		else:
		#
			xml_parser = XmlWriter(node_type = OrderedDict)

			client = Client.load_user_agent(self.client_user_agent)
			if (not client.get("upnp_xml_cdata_encoded", False)): xml_parser.define_cdata_encoding(False)

			xml_parser.node_add("s:Envelope", attributes = { "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/", "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
			xml_parser.node_add("s:Envelope s:Header")

			xml_base_path = "s:Envelope s:Body u:{0}Response".format(action)
			xml_parser.node_add(xml_base_path, attributes = { "xmlns:u": urn })
			xml_parser.node_set_cache_path(xml_base_path)

			for result_value in result: xml_parser.node_add("{0} {1}".format(xml_base_path, result_value['name']), result_value['value'])

			self.data = Binary.utf8_bytes("<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_parser.cache_export(True)))
		#
	#

	def send(self):
	#
		"""
Sends the prepared response.

:since: v0.1.00
		"""

		if (self.data != None):
		#
			if (not self.initialized): self.init()
			self.send_headers()

			self.stream_response.send_data(self.data)
			self.data = None
		#
		elif (not self.are_headers_sent()):
		#
			self.set_header("HTTP/1.1", "HTTP/1.1 500 Internal Server Error", True)

			if (self.errors == None): self.send_error(501, L10n.get("errors_core_unknown_error"))
			else: self.send_error((self.errors[0]['code'] if ("code" in self.errors[0]) else 501), self.errors[0]['message'])
		#
	#

	def send_error(self, code, description):
	#
		"""
Return a UPNP response for the requested SOAP action.

:param code: UPnP error code
:param description: UPnP error description

:since: v0.1.00
		"""

		xml_parser = XmlWriter()

		xml_parser.node_add("s:Envelope", attributes = { "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/", "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
		xml_parser.node_add("s:Envelope s:Header")

		xml_parser.node_add("s:Envelope s:Body s:Fault faultcode", "Client")
		xml_parser.node_set_cache_path("s:Envelope s:Body")

		xml_parser.node_add("s:Envelope s:Body s:Fault faultstring", "UPnPError")
		xml_parser.node_add("s:Envelope s:Body s:Fault detail UPnPError", attributes = { "xmlns": "urn:schemas-upnp-org:control-1.0" })
		xml_parser.node_set_cache_path("s:Envelope s:Body s:Fault detail UPnPError")

		xml_parser.node_add("s:Envelope s:Body s:Fault detail UPnPError errorCode", str(code))
		xml_parser.node_add("s:Envelope s:Body s:Fault detail UPnPError errorDescription", description)

		self.data = Binary.utf8_bytes("<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_parser.cache_export(True)))
		self.send()
	#
#

##j## EOF