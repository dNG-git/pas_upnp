# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.callable_service
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

from dNG.data.json_parser import direct_json_parser
from dNG.pas.plugins.hooks import direct_hooks
from .abstract_service import direct_abstract_service

class direct_callable_service(direct_abstract_service):
#
	"""
Implementation for "urn:schemas-direct-netware-de:service:CallableService:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def call_hook(self, hook, json_arguments):
	#
		"""
Calls the given hook and returns the result.

:return: (mixed) Data returned by the called hook
:since:  v0.1.01
		"""

		json_parser = direct_json_parser()
		arguments = ({ } if (json_arguments.strip() == "") else json_parser.json2data(json_arguments))

		result = direct_hooks.call(hook, **arguments)
		return json_parser.data2json(result)
	#

	def init_service(self, device, service_id = None, configid = None):
	#
		"""
Initialize a host service.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		if (service_id == None): service_id = "CallableService"
		direct_abstract_service.init_service(self, device, service_id, configid)

		self.actions = {
			"CallHook": {
				"argument_variables": [ { "name": "Hook", "variable": "A_ARG_TYPE_Hook" }, { "name": "JsonArguments", "variable": "A_ARG_TYPE_Json" } ],
				"return_variable": { "name": "JsonResult", "variable": "A_ARG_TYPE_Json" },
				"result_variables": [ ]
			}
		}

		self.service_id = service_id
		self.spec_major = 1
		self.spec_minor = 1
		self.type = "CallableService"
		self.upnp_domain = "schemas-direct-netware-de"
		self.version = "1"

		self.variables = {
			"A_ARG_TYPE_Hook": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string"
			},
			"A_ARG_TYPE_Json": {
				"is_sending_events": False,
				"is_multicasting_events": False,
				"type": "string",
				"value": ""
			}
		}

		return True
	#
#

##j## EOF