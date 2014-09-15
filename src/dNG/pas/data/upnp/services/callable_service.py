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

from dNG.data.json_resource import JsonResource
from dNG.pas.plugins.hook import Hook
from .abstract_service import AbstractService

class CallableService(AbstractService):
#
	"""
Implementation for "urn:schemas-direct-netware-de:service:CallableService:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def call_hook(self, hook, json_arguments):
	#
		"""
Calls the given hook and returns the result.

:return: (mixed) Data returned by the called hook
:since:  v0.1.01
		"""

		# pylint: disable=star-args

		json_resource = JsonResource()
		arguments = ({ } if (json_arguments.strip() == "") else json_resource.json_to_data(json_arguments))

		result = Hook.call(hook, **arguments)
		return json_resource.data_to_json(result)
	#

	def init_host(self, device, service_id = None, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.service_id = service_id
		self.type = "CallableService"
		self.upnp_domain = "schemas-direct-netware-de"
		self.version = "1"

		if (service_id == None): service_id = "CallableService"
		return AbstractService.init_host(self, device, service_id, configid)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		call_hook = { "argument_variables": [ { "name": "Hook", "variable": "A_ARG_TYPE_Hook" },
		                                      { "name": "JsonArguments", "variable": "A_ARG_TYPE_Json" }
		                                    ],
		              "return_variable": { "name": "JsonResult", "variable": "A_ARG_TYPE_Json" },
		              "result_variables": [ ]
		            }

		self.actions = { "CallHook": call_hook }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		self.variables = { "A_ARG_TYPE_Hook": { "is_sending_events": False,
		                                        "is_multicasting_events": False,
		                                        "type": "string"
		                                      },
		                   "A_ARG_TYPE_Json": { "is_sending_events": False,
		                                        "is_multicasting_events": False,
		                                        "type": "string",
		                                        "value": ""
		                                      }
		                 }
	#
#

##j## EOF