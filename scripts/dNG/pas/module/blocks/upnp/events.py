# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.upnp.Events
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
from time import time
import re

from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.services.abstract_service import AbstractService
from dNG.pas.net.upnp.gena import Gena
from dNG.pas.plugins.hooks import Hooks
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def execute_subscribe(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		os_uname = uname()

		self.response.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
		self.response.set_header("Server", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.50".format(os_uname[0], os_uname[2]))

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_error_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_error_400", 401)

		Hooks.call("dNG.pas.http.l10n.upnp.events.init")

		callback_url = self.request.get_header("Callback")
		gena_sid = self.request.get_header("SID")
		upnp_service.client_set_user_agent(self.request.get_header("User-Agent"))

		if ((callback_url != None and self.request.get_header("NT") == "upnp:event") or gena_sid != None):
		#
			gena = Gena.get_instance()
			timeout = self.request.get_header("Timeout")

			re_result = (None if (timeout == None) else re.match("^Second-(\d+)$", timeout))

			if (re_result == None):
			#
				client = Client.load_user_agent(self.request.get_header("User-Agent"))
				timeout = (1800 if (client == None) else client.get("upnp_subscription_timeout", 1800))
			#
			else: timeout = int(re_result.group(1))

			if (gena_sid == None):
			#
				gena_sid = gena.register(upnp_service.get_name(), callback_url.strip("<>"), timeout)
				gena.return_instance()

				if (gena_sid == False): raise UpnpException("pas_http_error_404", 412)
				else:
				#
					self.response.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
					self.response.set_header("SID", gena_sid)
					self.response.set_header("Timeout", "Second-{0:d}".format(timeout))
					self.response.set_raw_data("")
				#
			#
			else:
			#
				result = gena.reregister(upnp_service.get_name(), gena_sid, timeout)
				gena.return_instance()

				if (result == False): raise UpnpException("pas_http_error_404", 412)
				else:
				#
					self.response.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
					self.response.set_header("SID", gena_sid)
					self.response.set_header("Timeout", "Second-{0:d}".format(timeout))
					self.response.set_raw_data("")
				#
			#
		#
		else: raise UpnpException("pas_http_error_400", 400)
	#

	def execute_unsubscribe(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		os_uname = uname()

		self.response.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
		self.response.set_header("Server", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.50".format(os_uname[0], os_uname[2]))

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_error_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_error_400", 401)

		Hooks.call("dNG.pas.http.l10n.upnp.events.init")

		gena_sid = self.request.get_header("SID")
		upnp_service.client_set_user_agent(self.request.get_header("User-Agent"))

		if (gena_sid == None): raise UpnpException("pas_http_error_400", 400)
		else:
		#
			gena = Gena.get_instance()

			if (gena.deregister(upnp_service.get_name(), gena_sid)):
			#
				self.response.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
				self.response.set_raw_data("")
			#
			else: raise UpnpException("pas_http_error_404", 412)
		#
	#
#

##j## EOF