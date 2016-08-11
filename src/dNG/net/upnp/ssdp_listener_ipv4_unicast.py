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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
"""

from socket import INADDR_ANY

from dNG.net.server.dispatcher import Dispatcher
from dNG.net.udp_ne_ipv4_socket import UdpNeIpv4Socket

from .ssdp_request import SsdpRequest

class SsdpListenerIpv4Unicast(Dispatcher):
#
	"""
Listener instance receiving IPv4 unicast SSDP messages.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, port = 1900):
	#
		"""
Constructor __init__(SsdpListenerIpv4Unicast)

:since: v0.2.00
		"""

		listener_socket = UdpNeIpv4Socket(( INADDR_ANY, port ))
		Dispatcher.__init__(self, listener_socket, SsdpRequest, 25)
	#
#

##j## EOF