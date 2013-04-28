# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.service_proxy
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

from .action import direct_action
from .variable import direct_variable

class direct_service_proxy(object):
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
Constructor __init__(direct_service_proxy)

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

	def __getattr__(self, name):
	#
		"""
python.org: Called when an attribute lookup has not found the attribute in
the usual places (i.e. it is not an instance attribute nor is it found in the
class tree for self).

:param name: Attribute name

:return: (direct_action) UPnP action callable
:since:  v0.1.00
		"""

		if (self.actions != None and name in self.actions): return direct_action(self.service, name, self.actions[name])
		elif (self.variables != None and name in self.variables): return direct_variable(self.service, name, self.variables[name])
		else: raise AttributeError("UPnP SCPD does not contain a definition for '{0}'".format(name))
	#
#

##j## EOF