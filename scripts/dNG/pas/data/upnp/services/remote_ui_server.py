# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.RemoteUiServer
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

from .abstract_service import AbstractService

class RemoteUiServer(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:RemoteUIServer:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def get_compatible_uis(self, input_device_profile, ui_filter = ""):
	#
		"""
Calls the given hook and returns the result.

:return: (mixed) Data returned by the called hook
:since:  v0.1.01
		"""

		print(input_device_profile)
		print(ui_filter)
		return None
	#

	def init_service(self, device, service_id = None, configid = None):
	#
		"""
Initialize a host service.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		if (service_id == None): service_id = "RemoteUIServer"
		AbstractService.init_service(self, device, service_id, configid)

		self.actions = {
			"GetCompatibleUIs": {
				"argument_variables": [
					{ "name": "InputDeviceProfile", "variable": "A_ARG_TYPE_DeviceProfile" },
					{ "name": "UIFilter", "variable": "A_ARG_TYPE_String" }
				],
				"return_variable": { "name": "UIListing", "variable": "A_ARG_TYPE_CompatibleUIs" },
				"result_variables": [ ]
			}
		}

		self.service_id = service_id
		self.spec_major = 1
		self.spec_minor = 1
		self.type = "RemoteUIServer"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"

		self.variables = {
			"A_ARG_TYPE_DeviceProfile": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
			"A_ARG_TYPE_CompatibleUIs": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			},
			"A_ARG_TYPE_String": {
				"is_sending_events": True,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			}
		}

		return True
	#
#

##j## EOF