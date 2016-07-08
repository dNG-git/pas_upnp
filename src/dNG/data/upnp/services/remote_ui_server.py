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

from .abstract_service import AbstractService

class RemoteUiServer(AbstractService):
#
	"""
Implementation for "urn:schemas-upnp-org:service:RemoteUIServer:1".

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def get_compatible_uis(self, input_device_profile, ui_filter = ""):
	#
		"""
Calls the given hook and returns the result.

TODO: Add implementation

:return: (mixed) Data returned by the called hook
:since:  v0.2.00
		"""

		print(input_device_profile)
		print(ui_filter)
		return None
	#

	def init_host(self, device, service_id = None, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
		"""

		self.type = "RemoteUIServer"
		self.upnp_domain = "schemas-upnp-org"
		self.version = "1"

		if (service_id is None): service_id = "RemoteUIServer"
		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.2.00
		"""

		get_compatible_uis = { "argument_variables": [ { "name": "InputDeviceProfile", "variable": "A_ARG_TYPE_DeviceProfile" },
		                                               { "name": "UIFilter", "variable": "A_ARG_TYPE_String" }
		                                             ],
		                       "return_variable": { "name": "UIListing", "variable": "A_ARG_TYPE_CompatibleUIs" },
		                       "result_variables": [ ]
		                     }

		self.actions = { "GetCompatibleUIs": get_compatible_uis }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.2.00
		"""

		self.variables = { "A_ARG_TYPE_DeviceProfile": { "is_sending_events": True,
		                                                 "is_multicasting_events": False,
		                                                 "type": "string",
		                                                 "value": ""
		                                               },
		                   "A_ARG_TYPE_CompatibleUIs": { "is_sending_events": True,
		                                                 "is_multicasting_events": False,
		                                                 "type": "string",
		                                                 "value": ""
		                                               },
		                   "A_ARG_TYPE_String": { "is_sending_events": True,
		                                          "is_multicasting_events": False,
		                                          "type": "string",
		                                          "value": ""
		                                        }
		                 }
	#
#

##j## EOF