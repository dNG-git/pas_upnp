# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.action
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

from .variable import direct_variable

class direct_action(object):
#
	"""
The UPnP service action callable.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, service, action, variables):
	#
		"""
Constructor __init__(direct_action)

:since: v0.1.00
		"""

		self.action = action
		self.argument_variables = [ ]
		self.result_variables = [ ]
		self.return_variable = None
		self.service = service

		for argument_variable in variables['argument_variables']: self.argument_variables.append({ "name": argument_variable['name'], "variable": self.service.get_definition_variable(argument_variable['variable']) })
		for result_variable in variables['result_variables']: self.result_variables.append({ "name": result_variable['name'], "variable": self.service.get_definition_variable(result_variable['variable']) })

		if (variables['return_variable'] != None): self.return_variable = { "name": variables['return_variable']['name'], "variable": self.service.get_definition_variable(variables['return_variable']['variable']) }
	#

	def __call__(self, **kwargs):
	#
		"""
python.org: Called when the instance is "called" as a function.

:param kwargs: UPnP "in" arguments

:since: v0.1.00
		"""

		arguments = (self.argument_variables.copy() if (hasattr(self.argument_variables, "copy")) else copy(self.argument_variables))

		for name in kwargs:
		#
			for argument in arguments:
			#
				if (name == argument['name']): argument['value'] = direct_variable.get_upnp_value(argument['name'], argument['variable'], kwargs[name])
			#
		#

		for argument in arguments:
		#
			if ("value" not in argument):
			#
				if ("value" in argument['variable']): argument['value'] = direct_variable.get_upnp_value(argument['name'], argument['variable'], argument['variable']['value'])
				else: raise UnboundLocalError("'{0}' is not defined and has no default value".format(argument['name']))
			#
		#

		self.service.request_soap_action(self.action, arguments)
	#

#

##j## EOF