# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.ServiceProxy
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

from copy import copy

from dNG.pas.runtime.value_exception import ValueException
from .variable import Variable

class ServiceProxy(object):
#
	"""
The UPnP service proxy provides a pythonic interface to SOAP actions.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, service, actions, variables):
	#
		"""
Constructor __init__(ServiceProxy)

:since: v0.1.00
		"""

		self.actions = actions
		"""
Service actions defined in the SCPD
		"""
		self.service = service
		"""
UPnP service object
		"""
		self.variables = variables
		"""
Service variables defined in the SCPD
		"""
	#

	def __getattr__(self, action_method):
	#
		"""
python.org: Called when an attribute lookup has not found the attribute in
the usual places (i.e. it is not an instance attribute nor is it found in the
class tree for self).

:param action_method: Action method

:return: (Action) UPnP action callable
:since:  v0.1.00
		"""

		# pylint: disable=no-member,undefined-loop-variable

		if (self.actions != None and action_method in self.actions):
		#
			argument_variables = [ ]
			result_variables = [ ]
			return_variable = None
			variables = self.actions[action_method]

			for argument_variable in self.actions[action_method]['argument_variables']: argument_variables.append({ "name": argument_variable['name'], "variable": self.service.get_definition_variable(argument_variable['variable']) })
			for result_variable in self.actions[action_method]['result_variables']: result_variables.append({ "name": result_variable['name'], "variable": self.service.get_definition_variable(result_variable['variable']) })

			if (self.actions[action_method]['return_variable'] != None): return_variable = { "name": variables['return_variable']['name'], "variable": self.service.get_definition_variable(variables['return_variable']['variable']) }

			def proxymethod(**kwargs):
			#
				arguments = (argument_variables.copy() if (hasattr(argument_variables, "copy")) else copy(argument_variables))

				for name in kwargs:
				#
					for argument in arguments:
					#
						if (name == argument['name']): argument['value'] = Variable.get_upnp_value(argument['variable'], kwargs[name])
					#
				#

				for argument in arguments:
				#
					if ("value" not in argument):
					#
						if ("value" not in argument['variable']): raise ValueException("'{0}' is not defined and has no default value".format(argument['name']))
						argument['value'] = Variable.get_upnp_value(argument['variable'], argument['variable']['value'])
					#
				#

				result = self.service.request_soap_action(name, arguments)
			#

			return proxymethod
		#
		elif (self.variables != None and action_method in self.variables): return Variable(self.service, action_method, self.variables[action_method])
		else: raise ValueException("UPnP SCPD does not contain a definition for '{0}'".format(action_method))
	#
#

##j## EOF