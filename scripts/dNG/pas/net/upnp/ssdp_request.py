# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.SsdpRequest
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

import re

from dNG.data.rfc.http import Http
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.server.handler import Handler

class SsdpRequest(Handler):
#
	"""
Class for handling a received SSDP message.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since;      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	RE_HTTP_HEADER_MAX_AGE = re.compile("(^|[ ,]+)max\-age=(\d+)([, ]+|$)")

	def thread_run(self):
	#
		"""
Active conversation

:access: protected
:since:  v1.0.0
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ssdpRequest.thread_run()- (#echo(__LINE__)#)")

		http_data = self.get_data(512)
		http_request = None

		if (http_data != None):
		#
			http_headers = Http.header_get(http_data)

			if ("@http" in http_headers):
			#
				http_request_data = http_headers['@http'].split(" ", 2)

				if (len(http_request_data) > 2 and http_request_data[2].startswith("HTTP/")):
				#	
					http_request = http_request_data[0].upper()
					http_request_path = http_request_data[1]
					http_request_version = (1.1 if (http_request_data[2] == "HTTP/1.1") else 1)
				#
			#
		#

		if (http_request == "NOTIFY" and http_request_path == "*" and "NT" in http_headers and "NTS" in http_headers and "USN" in http_headers):
		#
			bootid = (int(http_headers['BOOTID.UPNP.ORG']) if ("BOOTID.UPNP.ORG" in http_headers) else None)
			configid = (int(http_headers['CONFIGID.UPNP.ORG']) if ("CONFIGID.UPNP.ORG" in http_headers) else None)
			control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")

			if (http_headers['NTS'] == "ssdp:alive" or http_headers['NTS'] == "ssdp:update"):
			#
				if ("CACHE-CONTROL" in http_headers and "LOCATION" in http_headers and "SERVER" in http_headers):
				#
					bootid_old = None

					if (http_headers['NTS'] == "ssdp:update"):
					#
						bootid = (int(http_headers['NEXTBOOTID.UPNP.ORG']) if ("NEXTBOOTID.UPNP.ORG" in http_headers) else None)
						bootid_old = (int(http_headers['BOOTID.UPNP.ORG']) if ("BOOTID.UPNP.ORG" in http_headers) else None)
					#

					re_result = SsdpRequest.RE_HTTP_HEADER_MAX_AGE.search(http_headers['CACHE-CONTROL'])
					unicast_port = (int(http_headers['SEARCHPORT.UPNP.ORG']) if ("SEARCHPORT.UPNP.ORG" in http_headers) else None)

					if (re_result != None): control_point.update_usn(http_headers['SERVER'], http_headers['USN'], bootid, bootid_old, configid, int(re_result.group(2)), unicast_port, http_request_version, http_headers['LOCATION'], http_headers)
					elif (self.log_handler != None): self.log_handler.debug("pas.upnp ignored incomplete NOTIFY nts '{0}'".format(http_headers['NTS']))
				#
				elif (self.log_handler != None): self.log_handler.debug("pas.upnp ignored incomplete NOTIFY nts '{0}'".format(http_headers['NTS']))
			#
			elif (http_headers['NTS'] == "ssdp:byebye"): control_point.delete_usn(http_headers['USN'], bootid, configid, http_headers)
			elif (self.log_handler != None): self.log_handler.debug("pas.upnp received unknown NOTIFY nts '{0}'".format(http_headers['NTS']))

			control_point.return_instance()
		#
		elif (http_request == "M-SEARCH" and http_request_path == "*" and "MAN" in http_headers and http_headers['MAN'].strip("\"") == "ssdp:discover" and "ST" in http_headers):
		#
			wait_timeout = (int(http_headers['MX']) if ("MX" in http_headers) else 1)
			if (wait_timeout > 5): wait_timeout = 5

			control_point = NamedLoader.get_singleton("dNG.pas.net.upnp.ControlPoint")
			control_point.search(self.address, wait_timeout, http_headers['ST'], http_headers)
			control_point.return_instance()
		#
	#
#

##j## EOF