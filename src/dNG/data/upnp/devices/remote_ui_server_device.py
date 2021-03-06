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

from dNG.data.upnp.services.remote_ui_server import RemoteUiServer

from .abstract_device import AbstractDevice

class RemoteUiServerDevice(AbstractDevice):
    """
The UPnP RemoteUIServerDevice:1 device implementation.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(RemoteUiServerDevice)

:since: v0.2.00
        """

        AbstractDevice.__init__(self)

        self.type = "RemoteUIServerDevice"
        self.upnp_domain = "schemas-upnp-org"
        self.version = "1"
    #

    def init_device(self, control_point, udn = None, configid = None):
        """
Initialize a host device.

:return: (bool) Returns true if initialization was successful.
:since: v0.2.00
        """

        AbstractDevice.init_device(self, control_point, udn, configid)

        self.device_model = "UPnP remote UI server"
        self.device_model_desc = "Python based UPnP remote UI server"
        self.device_model_url = "https://www.direct-netware.de/redirect?pas;upnp"
        self.device_model_version = "#echo(pasUPnPVersion)#"
        self.manufacturer = "direct Netware Group"
        self.manufacturer_url = "http://www.direct-netware.de"

        service = RemoteUiServer()
        if (service.init_host(self, configid = self.configid)): self.add_service(service)

        return True
    #
#
