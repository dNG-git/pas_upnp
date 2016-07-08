# -*- coding: utf-8 -*-
##j## BOF

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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
"""

import re

from dNG.data.binary import Binary
from dNG.data.upnp.client_settings import ClientSettings
from dNG.module.named_loader import NamedLoader
from dNG.net.http.raw_client import RawClient as HttpClient
from dNG.net.server.handler import Handler
from dNG.plugins.hook import Hook

class SsdpRequest(Handler):
#
	"""
Class for handling a received SSDP message.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	BINARY_HTTP_HEADER_SEPARATOR = Binary.bytes("\r\n\r\n")
	"""
Newline bytes used in raw HTTP data
	"""
	RE_HEADER_MAX_AGE = re.compile("(^|[ ,]+)max\\-age=(\\d+)([, ]+|$)")
	"""
RegEx to extract the "Max-Age" header value
	"""

	def _thread_run(self):
	#
		"""
Active conversation

:since: v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._thread_run()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		ssdp_data = self.get_data(65535)

		headers = (None if (ssdp_data == "") else HttpClient.get_headers(ssdp_data))
		ssdp_request = None

		if (headers is not None and "@http" in headers):
		#
			ssdp_request_data = headers['@http'].split(" ", 2)

			if (len(ssdp_request_data) > 2 and ssdp_request_data[2].startswith("HTTP/")):
			#
				ssdp_request = ssdp_request_data[0].upper()
				ssdp_request_path = ssdp_request_data[1]
				http_version = (1.1 if (ssdp_request_data[2] == "HTTP/1.1") else 1)
			#
		#

		if (ssdp_request == "NOTIFY" and ssdp_request_path == "*" and "NT" in headers and "NTS" in headers and "USN" in headers):
		#
			bootid = (int(headers['BOOTID.UPNP.ORG']) if ("BOOTID.UPNP.ORG" in headers) else None)
			configid = (int(headers['CONFIGID.UPNP.ORG']) if ("CONFIGID.UPNP.ORG" in headers) else None)
			control_point = NamedLoader.get_singleton("dNG.net.upnp.ControlPoint")
			user_agent = headers.get("SERVER")

			client_settings = ClientSettings.load_user_agent(user_agent)

			if (client_settings.get("ssdp_notify_use_filter", False)):
			#
				headers_filtered = Hook.call("dNG.pas.upnp.SsdpRequest.filterHeaders", headers = headers, user_agent = user_agent)
				if (headers_filtered is not None): headers = headers_filtered
			#

			if (headers['NTS'] == "ssdp:alive" or headers['NTS'] == "ssdp:update"):
			#
				if ("CACHE-CONTROL" in headers and "LOCATION" in headers and "SERVER" in headers):
				#
					bootid_old = None

					if (headers['NTS'] == "ssdp:update"):
					#
						bootid = (int(headers['NEXTBOOTID.UPNP.ORG']) if ("NEXTBOOTID.UPNP.ORG" in headers) else None)
						bootid_old = (int(headers['BOOTID.UPNP.ORG']) if ("BOOTID.UPNP.ORG" in headers) else None)
					#

					re_result = SsdpRequest.RE_HEADER_MAX_AGE.search(headers['CACHE-CONTROL'])
					unicast_port = (int(headers['SEARCHPORT.UPNP.ORG']) if ("SEARCHPORT.UPNP.ORG" in headers) else None)

					if (re_result is not None): control_point.update_usn(headers['SERVER'], headers['USN'], bootid, bootid_old, configid, int(re_result.group(2)), unicast_port, http_version, headers['LOCATION'], headers)
					elif (self.log_handler is not None): self.log_handler.debug("{0!r} ignored broken NOTIFY CACHE-CONTROL '{1}'", self, headers['CACHE-CONTROL'], context = "pas_upnp")
				#
				elif (self.log_handler is not None): self.log_handler.debug("{0!r} ignored incomplete NOTIFY {1!r}", self, headers, context = "pas_upnp")
			#
			elif (headers['NTS'] == "ssdp:byebye"): control_point.delete_usn(headers['USN'], bootid, configid, headers)
			elif (self.log_handler is not None): self.log_handler.debug("{0!r} received unknown NOTIFY {1!r}", self, headers, context = "pas_upnp")
		#
		elif (ssdp_request == "M-SEARCH" and ssdp_request_path == "*" and "MAN" in headers and headers['MAN'].strip("\"") == "ssdp:discover" and "ST" in headers):
		#
			wait_timeout = (int(headers['MX']) if ("MX" in headers) else 1)
			if (wait_timeout > 5): wait_timeout = 5

			ssdp_search_class = NamedLoader.get_class("dNG.net.upnp.SsdpSearch")
			ssdp_search_class.handle_request(self.address, wait_timeout, headers['ST'], headers)
		#
	#
#

##j## EOF