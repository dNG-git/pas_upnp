# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.upnp.Identity
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

from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.devices.abstract_device import AbstractDevice
from dNG.pas.data.upnp.services.abstract_service import AbstractService
from .module import Module

class Identity(Module):
#
	"""
Service for "m=upnp;s=identity"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def execute_device(self):
	#
		"""
Action for "index"

:since: v0.1.01
		"""

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_error_400")
		upnp_device = self.request.get_upnp_device()
		if (not isinstance(upnp_device, AbstractDevice)): raise UpnpException("pas_http_error_400", 401)

		self.response.init()
		self.response.set_header("Content-Type", "text/plain")
		self.response.set_raw_data(upnp_device.get_udn())
	#

	def execute_service(self):
	#
		"""
Action for "service"

:since: v0.1.00
		"""

		if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_error_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_error_400", 401)

		self.response.init()
		self.response.set_header("Content-Type", "text/plain")
		self.response.set_raw_data(upnp_service.get_udn())
	#
#

##j## EOF