# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.devices.callable_device
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

from socket import gethostname

from dNG.pas.data.upnp.services.callable_service import direct_callable_service
from .abstract_device import direct_abstract_device

class direct_callable_device(direct_abstract_device):
#
	"""
Implementation for "urn:schemas-direct-netware-de:device:CallableDevice:1".

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def init_device(self, control_point, udn, configid = None):
	#
		"""
Initialize a host device.

:return: (bool) Returns true if initialization was successful.
:since: v0.1.00
		"""

		direct_abstract_device.init_device(self, control_point, udn, configid)

		self.device_model = "UPnP Python server"
		self.device_model_desc = "Python based UPnP server software"
		self.device_model_url = "http://www.direct-netware.de/redirect.py?pas;upnp"
		self.device_model_version = "#echo(pasUPnPVersion)#"
		self.manufacturer = "direct Netware Group"
		self.manufacturer_url = "http://www.direct-netware.de"
		self.name = "{0} UPnP server".format(gethostname())
		self.spec_major = 1
		self.spec_minor = 1
		self.type = "CallableDevice"
		self.upnp_domain = "schemas-direct-netware-de"
		self.version = "1"

		service = direct_callable_service()
		if (service.init_service(self, configid = self.configid)): self.service_add(service)

		return True
	#
#

##j## EOF