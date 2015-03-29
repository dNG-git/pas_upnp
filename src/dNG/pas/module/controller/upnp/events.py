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

from platform import uname
from time import time
import re

from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.services.abstract_service import AbstractService
from dNG.pas.net.upnp.gena import Gena
from dNG.pas.plugins.hook import Hook
from .module import Module

class Events(Module):
#
	"""
Service for "m=upnp;s=events"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def execute_subscribe(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		os_uname = uname()

		self.response.init()
		self.response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
		self.response.set_header("Server", "{0}/{1} UPnP/2.0 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.51 HTTP/1.1".format(os_uname[0], os_uname[2]))

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_core_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_core_400", 401)

		Hook.call("dNG.pas.http.l10n.upnp.Events.init")

		callback_value = self.request.get_header("Callback")
		gena_sid = self.request.get_header("SID")
		upnp_service.set_client_user_agent(self.client_user_agent)

		if ((callback_value is None or self.request.get_header("NT") != "upnp:event")
		    and gena_sid is None
		   ): raise UpnpException("pas_http_core_400", 400)

		gena = Gena.get_instance()
		timeout = self.request.get_header("Timeout")

		re_result = (None if (timeout is None) else re.match("^Second-(\\d+)$", timeout))

		if (re_result is None):
		#
			client = Client.load_user_agent(self.client_user_agent)
			timeout = int(client.get("upnp_subscription_timeout", 1800))
		#
		else: timeout = int(re_result.group(1))

		usn = upnp_service.get_usn()

		if (gena_sid is None):
		#
			gena_variables = self.request.get_header("StateVar")

			gena_sid = gena.register(usn, callback_value, timeout, variables = gena_variables)
			if (gena_sid is None): raise UpnpException("pas_http_core_404", 412)

			self.response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
			self.response.set_header("SID", gena_sid)
			self.response.set_header("Timeout", "Second-{0:d}".format(timeout))
			if (gena_variables != ""): self.response.set_header("Accepted-StateVar", gena_variables)
			self.response.set_raw_data("")
		#
		else:
		#
			result = gena.reregister(usn, gena_sid, timeout)
			if (result == False): raise UpnpException("pas_http_core_404", 412)

			self.response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
			self.response.set_header("SID", gena_sid)
			self.response.set_header("Timeout", "Second-{0:d}".format(timeout))
			self.response.set_raw_data("")
		#
	#

	def execute_unsubscribe(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		os_uname = uname()

		self.response.init()
		self.response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
		self.response.set_header("Server", "{0}/{1} UPnP/2.0 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.51 HTTP/1.1".format(os_uname[0], os_uname[2]))

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_core_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_core_400", 401)

		Hook.call("dNG.pas.http.l10n.upnp.Events.init")

		gena_sid = self.request.get_header("SID")
		upnp_service.set_client_user_agent(self.client_user_agent)

		if (gena_sid is None): raise UpnpException("pas_http_core_400", 400)

		gena = Gena.get_instance()
		usn = upnp_service.get_usn()

		if (not gena.deregister(usn, gena_sid)): raise UpnpException("pas_http_core_404", 412)

		self.response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
		self.response.set_raw_data("")
	#
#

##j## EOF