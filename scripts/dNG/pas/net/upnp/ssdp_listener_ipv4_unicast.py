# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.ssdp_unicast_listener
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

from socket import INADDR_ANY

from dNG.pas.net.udpne_ipv4_socket import direct_udpne_ipv4_socket
from dNG.pas.net.server.dispatcher import direct_dispatcher
from .ssdp_request import direct_ssdp_request

class direct_ssdp_unicast_listener(direct_dispatcher):
#
	"""
Listener instance receiving unicast SSDP messages.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, port = 1900):
	#
		"""
Constructor __init__(direct_ssdp_unicast_listener)

:since: v0.1.00
		"""

		listener_socket = direct_udpne_ipv4_socket(( INADDR_ANY, port ))
		direct_dispatcher.__init__(self, listener_socket, direct_ssdp_request, 25)
	#
#

##j## EOF