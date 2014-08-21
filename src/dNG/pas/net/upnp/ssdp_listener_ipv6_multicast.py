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

from copy import copy
from struct import pack
import socket

from dNG.pas.net.udp_ne_ipv6_socket import UdpNeIpv6Socket
from dNG.pas.net.server.dispatcher import Dispatcher
from .ssdp_request import SsdpRequest

class SsdpListenerIpv6Multicast(Dispatcher):
#
	"""
Listener instance receiving IPv6 multicast SSDP messages.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, ip, multicast_address = "ff02::c"):
	#
		"""
Constructor __init__(SsdpListenerIpv6Multicast)

:param ip: IPv6 address

:since: v0.1.00
		"""

		self.listener_active = False
		"""
True if multicast listener is active
		"""
		self.listener_if_index = 0
		"""
Listener IPv6 interface index
		"""
		self.multicast_addresses = [ ]
		"""
Multicast addresses to listen for on this socket
		"""

		# pylint: disable=no-member

		# Split listener interface from IPv6 address and find corresponding index
		if ("%" in ip and hasattr(socket, "if_nameindex")):
		#
			if_list = { if_name: index for index, if_name in socket.if_nameindex() }

			( ip, _if ) = ip.split("%", 1)
			self.listener_if_index = (if_list[_if] if (_if in if_list) else int(_if))
		#

		listener_socket = UdpNeIpv6Socket(( "::", 1900 ))
		Dispatcher.__init__(self, listener_socket, SsdpRequest, 1)

		self.add_address(multicast_address)
	#

	def add_address(self, multicast_address):
	#
		"""
Adds a new IPv6 multicast address to listen for SSDP messages.

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (multicast_address not in self.multicast_addresses and socket.has_ipv6):
		#
			try:
			#
				self.listener_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, socket.inet_pton(socket.AF_INET6, multicast_address) + pack("I", self.listener_if_index))
				self.multicast_addresses.append(multicast_address)

				if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.run()- reporting: Added listener for '{1} {2:d}'", self, multicast_address, self.listener_if_index, context = "pas_upnp")
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.debug(handled_exception, context = "pas_upnp")
			#
		#
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

	def remove_address(self, multicast_address):
	#
		"""
Removes an IPv6 multicast address currently listening for SSDP messages.

:since: v0.1.00
		"""

		if (multicast_address in self.multicast_addresses):
		#
			self.listener_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_LEAVE_GROUP, socket.inet_pton(socket.AF_INET6, multicast_address) + pack("I", self.listener_if_index))
			self.multicast_addresses.remove(multicast_address)
		#
	#

	def run(self):
	#
		"""
Run the main loop for this server instance.

:since: v0.1.00
		"""

		if (not self.listener_active):
		#
			if (len(self.multicast_addresses) > 0):
			#
				self.listener_active = True
				Dispatcher.run(self)
			#
			elif (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.run()- reporting: No IPv6 multicast addresses bound", self, context = "pas_upnp")
		#
	#

	def stop(self):
	#
		"""
Stops the listener and unqueues all running sockets.

:since: v0.1.00
		"""

		# pylint: disable=broad-except,no-member

		if (self.listener_active):
		#
			multicast_addresses = (self.multicast_addresses.copy() if (hasattr(self.multicast_addresses, "copy")) else copy(self.multicast_addresses))

			for multicast_address in multicast_addresses:
			#
				try: self.remove_address(multicast_address)
				except Exception as handled_exception:
				#
					if (self.log_handler != None): self.log_handler.debug(handled_exception, context = "pas_upnp")
				#
			#

			self.listener_active = False
		#

		Dispatcher.stop(self)
	#
#

##j## EOF