# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.services.abstract_service import AbstractService
from dNG.pas.plugins.hook import Hook
from .module import Module

class Control(Module):
#
	"""
Service for "m=upnp;s=control"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def execute_request(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_core_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_core_400", 401)

		Hook.call("dNG.pas.http.l10n.upnp.Control.init")

		soap_request = self.request.get_soap_request()
		upnp_service.set_client_user_agent(self.client_user_agent)

		if (soap_request == None): raise UpnpException("pas_http_core_500")

		self.response.init()
		self.response.handle_result(soap_request['urn'], soap_request['action'], upnp_service.handle_soap_call(soap_request['action'], soap_request['arguments']))
	#
#

##j## EOF