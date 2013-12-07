# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.upnp.pas_upnp
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

from dNG.pas.data.upnp.client import Client
from dNG.pas.net.upnp.abstract_ssdp import AbstractSsdp
from dNG.pas.plugins.hooks import Hooks

def plugin_control_point_device_add(params, last_return):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.deviceAdd"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	_return = last_return

	user_agent = (params['identifier']['ssdpname'] if ("ssdpname" in params['identifier']) else None)
	client = Client.load_user_agent(user_agent)

	if (client != None):
	#
		ssdp_quirks = client.get("upnp_quirks_ssdp")

		if (type(ssdp_quirks) == list):
		#
			for mode in ssdp_quirks: AbstractSsdp.quirks_mode_add(mode)
		#

		_return = True
	#

	return _return
#

def plugin_deregistration():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hooks.unregister("dNG.pas.upnp.ControlPoint.deviceAdd", plugin_control_point_device_add)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.upnp.ControlPoint.deviceAdd", plugin_control_point_device_add)
#

##j## EOF