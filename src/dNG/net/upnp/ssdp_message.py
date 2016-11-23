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

from .abstract_ssdp import AbstractSsdp

class SsdpMessage(AbstractSsdp):
    """
This class contains the UPnP SSDP message implementation. Its based on HTTP
for UDP.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def send_m_search(self):
        """
Invoke an SSDP M-SEARCH method on the unicast or multicast recipient.

:return: (bool) Request result
:since:  v0.2.00
        """

        return self.request("M-SEARCH")
    #

    def send_notify(self):
        """
Invoke an SSDP NOTIFY method on the unicast or multicast recipient.

:return: (bool) Request result
:since:  v0.2.00
        """

        return self.request("NOTIFY")
    #
#
