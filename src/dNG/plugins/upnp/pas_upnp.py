# -*- coding: utf-8 -*-

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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
"""

from dNG.data.settings import Settings
from dNG.data.upnp.client_settings import ClientSettings
from dNG.net.upnp.abstract_ssdp import AbstractSsdp
from dNG.plugins.hook import Hook

def on_device_added(params, last_return = None):
    """
Called for "dNG.pas.upnp.ControlPoint.onDeviceAdded"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
    """

    _return = last_return

    user_agent = (params['identifier']['ssdp_server_name']
                  if ("identifier" in params and "ssdp_server_name" in params['identifier']) else
                  None
                 )

    ssdp_quirks = ClientSettings(user_agent).get("upnp_quirks_ssdp")

    if (type(ssdp_quirks) is list):
        for mode in ssdp_quirks:
            AbstractSsdp.add_quirks_mode(mode)
        #

        _return = True
    #

    return _return
#

def on_startup(params, last_return = None):
    """
Called for "dNG.pas.upnp.ControlPoint.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
    """

    ssdp_quirks = Settings.get("pas_upnp_client_quirks")

    if (type(ssdp_quirks) is list):
        for mode in ssdp_quirks: AbstractSsdp.add_quirks_mode(mode)
    #

    return last_return
#

def register_plugin():
    """
Register plugin hooks.

:since: v0.2.00
    """

    Hook.register("dNG.pas.upnp.ControlPoint.onDeviceAdded", on_device_added)
    Hook.register("dNG.pas.upnp.ControlPoint.onStartup", on_startup)
#

def unregister_plugin():
    """
Unregister plugin hooks.

:since: v0.2.00
    """

    Hook.unregister("dNG.pas.upnp.ControlPoint.onDeviceAdded", on_device_added)
    Hook.unregister("dNG.pas.upnp.ControlPoint.onStartup", on_startup)
#
