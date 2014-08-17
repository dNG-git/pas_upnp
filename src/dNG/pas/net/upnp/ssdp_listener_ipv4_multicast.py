# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

import socket

from dNG.pas.net.udp_ne_ipv4_socket import UdpNeIpv4Socket
from dNG.pas.net.server.dispatcher import Dispatcher
from .ssdp_request import SsdpRequest

class SsdpListenerIpv4Multicast(Dispatcher):
#
	"""
Listener instance receiving IPv4 multicast SSDP messages.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, ip):
	#
		"""
Constructor __init__(SsdpListenerIpv4Multicast)

:param ip: IPv4 address

:since: v0.1.00
		"""

		self.listener_active = False
		"""
True if multicast listener is active
		"""
		self.listener_ip = ip
		"""
Listener IPv6 address
		"""

		listener_socket = UdpNeIpv4Socket(( "", 1900 ))

		Dispatcher.__init__(self, listener_socket, SsdpRequest, 1)
	#

	def is_listening(self):
	#
		"""
Returns true if the listener is active.

:return: (bool) Listener state
:since:  v0.1.00
		"""

		return self.listener_active
	#

	def run(self):
	#
		"""
Run the main loop for this server instance.

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (not self.listener_active):
		#
			try:
			#
				mreq = (socket.inet_pton(socket.AF_INET, "239.255.255.250") + socket.inet_pton(socket.AF_INET, self.listener_ip)
				        if (hasattr(socket, "inet_pton")) else
				        socket.inet_aton("239.255.255.250") + socket.inet_aton(self.listener_ip)
				       )

				self.listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

				self.listener_active = True

				if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.run()- reporting: Started listening on '{1}'", self, self.listener_ip, context = "pas_upnp")
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.debug(handled_exception, context = "pas_upnp")
			#
		#

		Dispatcher.run(self)
	#

	def stop(self):
	#
		"""
Stops the listener and unqueues all running sockets.

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.listener_active):
		#
			try: self.listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_pton(socket.AF_INET, "239.255.255.250") + socket.inet_pton(socket.AF_INET, self.listener_ip))
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.debug(handled_exception, context = "pas_upnp")
			#

			self.listener_active = False
		#

		Dispatcher.stop(self)
	#
#

##j## EOF