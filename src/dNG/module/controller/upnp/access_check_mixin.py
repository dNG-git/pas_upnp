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

import socket

from dNG.data.http.translatable_error import TranslatableError
from dNG.net.upnp.control_point import ControlPoint

class AccessCheckMixin(object):
    """
Mixin to validate that the requesting client is allowed to access UPnP
resources.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def _ensure_access_granted(self):
        """
Validates that the requesting client is allowed to access UPnP resources.

:since: v0.2.00
        """

        client_host = self.request.get_client_host()
        upnp_control_point = ControlPoint.get_instance()

        if (client_host is None): is_allowed = False
        else:
            ip_address_paths = socket.getaddrinfo(client_host, self.request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
            is_allowed = (False if (len(ip_address_paths) < 1) else upnp_control_point.is_ip_allowed(ip_address_paths[0][4][0]))
        #

        if (not is_allowed): raise TranslatableError("core_access_denied", 403)
    #
#
