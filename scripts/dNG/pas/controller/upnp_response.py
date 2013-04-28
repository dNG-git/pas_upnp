# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.upnp_response
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

from os import uname

from dNG.data.xml_writer import direct_xml_writer
from dNG.pas.data.text.l10n import direct_l10n
from .abstract_http_response import direct_abstract_http_response

class direct_upnp_response(direct_abstract_http_response):
#
	"""
The following class implements the response object for XHTML content.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def init(self, cache = False, compress = True):
	#
		"""
Important headers will be created here. This includes caching, cookies, the
compression setting and information about P3P.

:param cache: Allow caching at client
:param compress: Send page GZip encoded (if supported)

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -response.init(cache, compress)- (#echo(__LINE__)#)")

		os_uname = uname()

		self.set_header("Content-Type", "text/xml; charset=UTF-8")
		self.set_header("Server", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.50".format(os_uname[0], os_uname[2]))
	#

	def send(self):
	#
		"""
Sends the prepared response.

:since: v0.1.00
		"""

		if (not self.initialized): self.init()

		if (self.data != None):
		#
			self.send_headers()
			self.stream_response.send_data(self.data)
			self.data = None
		#
		else:
		#
			self.set_header("HTTP/1.1", "HTTP/1.1 500 Internal Server Error", True)

			if (self.errors == None): self.send_error(501, direct_l10n.get("errors_core_unknown_error"))
			else: self.send_error((self.errors[0]['code'] if ("code" in self.errors[0]) else 501), self.errors[0]['message'])
		#
	#

	def send_error(self, code, description):
	#
		"""
Return a UPNP response for the requested SOAP action.

:param action: SOAP action called
:param result: UPnP result arguments

:since: v0.1.00
		"""

		xml_parser = direct_xml_writer()

		xml_parser.node_add("Envelope", attributes = { "xmlns": "http://schemas.xmlsoap.org/soap/envelope/", "encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
		xml_parser.node_add("Envelope Header")

		xml_parser.node_add("Envelope Body Fault faultcode", "Client")
		xml_parser.node_set_cache_path("Envelope Body")

		xml_parser.node_add("Envelope Body Fault faultstring", "UPnPError")
		xml_parser.node_add("Envelope Body Fault detail UPnPError", attributes = { "xmlns": "urn:schemas-upnp-org:control-1.0" })
		xml_parser.node_set_cache_path("Envelope Body Fault detail UPnPError")

		xml_parser.node_add("Envelope Body Fault detail UPnPError errorCode", "{0:d}".format(code))
		xml_parser.node_add("Envelope Body Fault detail UPnPError errorDescription", description)

		self.data = xml_parser.cache_export(True)
		self.send()
	#

	def send_result(self, action, result = [ ]):
	#
		"""
Return a UPNP response for the requested SOAP action.

:param action: SOAP action called
:param result: UPnP result arguments

:since: v0.1.00
		"""

		pass
	#
#

##j## EOF