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

from dNG.controller.http_upnp_request import HttpUpnpRequest
from dNG.data.upnp.upnp_exception import UpnpException
from dNG.data.upnp.devices.abstract_device import AbstractDevice
from dNG.data.upnp.services.abstract_service import AbstractService

from .module import Module

class Xml(Module):
    """
Service for "m=upnp;s=xml"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def execute_get_device(self):
        """
Action for "get_device"

:since: v0.2.00
        """

        if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_core_400")
        upnp_device = self.request.get_upnp_device()
        if (not isinstance(upnp_device, AbstractDevice)): raise UpnpException("pas_http_core_400", 401)

        client_settings = self.get_client_settings()
        upnp_device.set_client_settings(client_settings)

        self.response.init(True, compress = client_settings.get("upnp_http_compression_supported", True))
        self.response.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.response.set_raw_data("<?xml version='1.0' encoding='UTF-8' ?>" + upnp_device.get_xml())
    #

    def execute_get_service(self):
        """
Action for "get_service"

:since: v0.2.00
        """

        if (not isinstance(self.request, HttpUpnpRequest)): raise UpnpException("pas_http_core_400")
        upnp_service = self.request.get_upnp_service()
        if (not isinstance(upnp_service, AbstractService)): raise UpnpException("pas_http_core_400", 401)

        client_settings = self.get_client_settings()
        upnp_service.set_client_settings(client_settings)

        self.response.init(True, compress = client_settings.get("upnp_http_compression_supported", True))
        self.response.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.response.set_raw_data("<?xml version='1.0' encoding='UTF-8' ?>" + upnp_service.get_xml())
    #
#
