# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.AbstractSsdp
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

from os import uname
import socket

from dNG.data.rfc.http import Http
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.udp_ne_ipv4_socket import UdpNeIpv4Socket
from dNG.pas.net.udp_ne_ipv6_socket import UdpNeIpv6Socket

class AbstractSsdp(Http):
#
	"""
This class contains a generic SSDP message implementation. Its based on HTTP
for UDP.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, target, port = 1900, source_port = None):
	#
		"""
Constructor __init__(AbstractSsdp)

:since: v0.1.00
		"""

		self.ssdp_family = None
		"""
SSDP target family
		"""
		self.ssdp_host = None
		"""
SSDP target host
		"""

		Http.__init__(self, "ssdp://{0}:{1:d}/*".format(target, port))
		self.set_ipv6_link_local_interface(Settings.get("pas_global_ipv6_link_local_interface"))

		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.socket = None
		"""
Active SSDP message socket
		"""
		self.source_port = None
		"""
Sets a specific source port for messages sent.
		"""
		self.udp_hops = int(Settings.get("pas_upnp_ssdp_udp_hops", 2))
		"""
UDP validity (IPv4 TTL / IPv6 Hops) for SSDP messages.
		"""

		if (self.log_handler != None): self.set_event_handler(self.log_handler)
		if (self.path == "/*"): self.path = "*"
	#

	def __del__(self):
	#
		"""
Destructor __del__(AbstractSsdp)

:since: v0.1.00
		"""

		if (self.socket != None): self.socket.close()
	#

	def configure(self, url):
	#
		"""
Returns a connection to the HTTP server.

:param url: URL to be called

:access: protected
:since:  v0.1.00
		"""

		Http.configure(self, url)

		self.ssdp_host = (self.host[1:-1] if (":" in self.host) else self.host)
		address_paths = socket.getaddrinfo(self.ssdp_host, self.port, socket.AF_UNSPEC, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		if (len(address_paths) == 1): self.ssdp_family = address_paths[0][0]
	#

	def request(self, method, data = None):
	#
		"""
Invoke a given SSDP method on the unicast or multicast recipient.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		if (data != None): data = Binary.utf8_bytes(data)
		os_uname = uname()

		headers = self.headers.copy()
		headers['SERVER'] = "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.50".format(os_uname[0], os_uname[2])
		headers['HOST'] = "{0}:{1:d}".format(self.host, self.port)
		headers['CONTENT-LENGTH'] = (0 if (data == None) else len(data))

		ssdp_header = "{0} {1} HTTP/1.1\r\n".format(method.upper(), self.path)

		for header_name in headers:
		#
			if (type(headers[header_name]) == list):
			#
				for header_value in headers[header_name]: ssdp_header += "{0}: {1}\r\n".format(header_name, header_value)
			#
			else: ssdp_header += "{0}: {1}\r\n".format(header_name, headers[header_name])
		#

		ssdp_header = Binary.utf8_bytes("{0}\r\n".format(ssdp_header))

		data = (ssdp_header if (data == None) else ssdp_header + data)
		return self.write_data(data)
	#

	def request_get(self, params = None, separator = ";"):
	#
		"""
Invoke the GET method on the unicast or multicast recipient.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		return self.request("GET")
	#

	def request_head(self, params = None, separator = ";"):
	#
		"""
Invoke the HEAD method on the unicast or multicast recipient.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		return self.request("HEAD")
	#

	def request_post(self, data = None, params = None, separator = ";"):
	#
		"""
Invoke the POST method on the unicast or multicast recipient.

:param data: HTTP body
:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		return self.request("POST", data)
	#

	def write_data(self, data):
	#
		"""
Send the given data to the defined recipient.

:param data: SSDP message

:access: protected
:return: (bool) Request result
:since:  v0.1.00
		"""

		var_return = True

		try:
		#
			if (self.ssdp_family == socket.AF_INET):
			#
				self.socket = UdpNeIpv4Socket()
				if (self.source_port != None): self.socket.bind(( "", self.source_port ))
				if (hasattr(socket, "IP_MULTICAST_LOOP")): self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
				if (hasattr(socket, "IP_MULTICAST_TTL")): self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.udp_hops)
			#
			else:
			#
				self.socket = UdpNeIpv6Socket()
				if (self.source_port != None): self.socket.bind(( "::", self.source_port ))
				if (hasattr(socket, "IPV6_MULTICAST_LOOP")): self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 0)
				if (hasattr(socket, "IPV6_MULTICAST_HOPS")): self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.udp_hops)
			#

			self.socket.sendto(data, ( self.ssdp_host, self.port ))
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			var_return = False
		#

		return var_return
	#
#

##j## EOF