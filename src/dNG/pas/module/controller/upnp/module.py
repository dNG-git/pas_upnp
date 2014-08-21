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

import socket

from dNG.pas.controller.http_upnp_response import HttpUpnpResponse
from dNG.pas.data.settings import Settings
from dNG.pas.module.controller.abstract_http import AbstractHttp as AbstractHttpController
from dNG.pas.net.upnp.control_point import ControlPoint

class Module(AbstractHttpController):
#
	"""
module for "upnp"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractHttpController)

:since: v0.1.00
		"""

		AbstractHttpController.__init__(self)

		self.client_user_agent = None
		"""
Client user agent
		"""
	#

	def init(self, request, response):
	#
		"""
Initialize block from the given request and response.

:param request: Request object
:param response: Response object

:since: v0.1.00
		"""

		AbstractHttpController.init(self, request, response)

		user_agent = self.request.get_header("User-Agent")

		if (Settings.get("pas_upnp_http_client_name_use_cache", False)):
		#
			user_agent_blacklist = Settings.get("pas_upnp_http_client_name_blacklist", [ ])
			if (user_agent != None and user_agent in user_agent_blacklist): user_agent = None

			host = self.request.get_client_host()
			ip_address_list = socket.getaddrinfo(host, None, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

			for ip_address_data in ip_address_list:
			#
				if (user_agent == None):
				#
					user_agent = ControlPoint.get_instance().get_http_client_name_of_ip(ip_address_data[4][0])
					if (user_agent != None): break
				#
				else: ControlPoint.get_instance().add_http_client_name_to_ip(user_agent, ip_address_data[4][0])
			#
		#

		self.client_user_agent = user_agent

		if (isinstance(self.response, HttpUpnpResponse)): self.response.set_client_user_agent(self.client_user_agent)
	#
#

##j## EOF