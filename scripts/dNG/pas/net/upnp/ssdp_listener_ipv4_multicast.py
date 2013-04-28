# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.ssdp_listener_ipv4_multicast
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

import socket

from dNG.pas.net.udpne_ipv4_socket import direct_udpne_ipv4_socket
from dNG.pas.net.server.dispatcher import direct_dispatcher
from .ssdp_request import direct_ssdp_request

class direct_ssdp_listener_ipv4_multicast(direct_dispatcher):
#
	"""
Listener instance receiving multicast SSDP messages.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(direct_ssdp_listener_ipv4_multicast)

:since: v0.1.00
		"""

		self.listener_active = False
		"""
True if multicast listener is active
		"""

		listener_socket = direct_udpne_ipv4_socket(( "", 1900 ))

		direct_dispatcher.__init__(self, listener_socket, direct_ssdp_request, 1)
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

		if (not self.listener_active):
		#
			try:
			#
				self.listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_pton(socket.AF_INET, "239.255.255.250") + socket.inet_pton(socket.AF_INET, "0.0.0.0"))
				self.listener_active = True
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
			#
		#

		direct_dispatcher.run(self)
	#

	def stop(self):
	#
		"""
Stops the listener and unqueues all running sockets.

:since: v0.1.00
		"""

		if (self.listener_active):
		#
			try: self.listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_pton(socket.AF_INET, "239.255.255.250") + socket.inet_pton(socket.AF_INET, "0.0.0.0"))
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
			#
	
			self.listener_active = False
		#

		direct_dispatcher.stop(self)
	#
#

##j## EOF