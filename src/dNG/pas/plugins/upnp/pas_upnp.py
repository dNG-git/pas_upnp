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

from dNG.pas.data.upnp.client import Client
from dNG.pas.net.upnp.abstract_ssdp import AbstractSsdp
from dNG.pas.plugins.hook import Hook

def on_device_added(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.onDeviceAdded"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	_return = last_return

	user_agent = (params['identifier']['ssdp_server_name']
	              if ("identifier" in params and "ssdp_server_name" in params['identifier']) else
	              None
	             )

	ssdp_quirks = Client.load_user_agent(user_agent).get("upnp_quirks_ssdp")

	if (type(ssdp_quirks) is list):
	#
		for mode in ssdp_quirks:
		#
			AbstractSsdp.add_quirks_mode(mode)
			_return = True
		#
	#

	return _return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.upnp.ControlPoint.onDeviceAdded", on_device_added)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.upnp.ControlPoint.onDeviceAdded", on_device_added)
#

##j## EOF