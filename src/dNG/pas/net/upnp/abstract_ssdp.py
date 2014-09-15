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

from platform import uname
import socket

from dNG.net.http.raw_client import RawClient
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.udp_ne_ipv4_socket import UdpNeIpv4Socket
from dNG.pas.net.udp_ne_ipv6_socket import UdpNeIpv6Socket
from dNG.pas.runtime.instance_lock import InstanceLock

class AbstractSsdp(RawClient):
#
	"""
This class contains a generic SSDP message implementation. Its based on HTTP
for UDP.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=arguments-differ

	QUIRK_OS_LINUX = 1
	"""
Quirk mode replaces the OS string from the SERVER header with "Linux".
	"""
	QUIRK_OS_VERSION = 2
	"""
Quirk mode replaces the OS version from the SERVER header with "0.0".
	"""
	QUIRK_OS_WINDOWS = 4
	"""
Quirk mode replaces the OS string from the SERVER header with "Windows".
	"""
	QUIRK_UPNP_1_0 = 8
	"""
Quirk mode adds UPnP/1.0 version to the SERVER header.
	"""

	_lock = InstanceLock()
	"""
Thread safety lock
	"""
	_os_uname = uname()
	"""
OS uname data
	"""
	quirks_mode = 0
	"""
The quirks mode adds non-standard behaviour to SSDP headers and messages.
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

		RawClient.__init__(self, "ssdp://{0}:{1:d}/*".format(target, port))

		self.ipv4_udp_ttl = int(Settings.get("pas_upnp_ssdp_ipv4_udp_ttl", 2))
		"""
IPv4 TTL for SSDP messages.
		"""
		self.ipv6_udp_hops = int(Settings.get("pas_upnp_ssdp_ipv6_udp_hops", 2))
		"""
IPv6 hops for SSDP messages.
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.source_port = (0 if (source_port == None) else source_port)
		"""
Sets a specific source port for messages sent.
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

		if (self.connection != None): self.connection.close()
	#

	def _configure(self, url):
	#
		"""
Returns a connection to the HTTP server.

:param url: URL to be called

:access: protected
:since:  v0.1.00
		"""

		RawClient._configure(self, url)

		self.ssdp_host = (self.host[1:-1] if (":" in self.host) else self.host)
		address_list = socket.getaddrinfo(self.ssdp_host, self.port, socket.AF_UNSPEC, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		if (len(address_list) == 1): self.ssdp_family = address_list[0][0]
	#

	def _get_connection(self):
	#
		"""
Returns a connection to the configured UDP address.

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		if (self.connection == None):
		#
			if (self.ssdp_family == socket.AF_INET):
			#
				self.connection = UdpNeIpv4Socket()
				self.connection.bind(( "", self.source_port ))
				if (hasattr(socket, "IP_MULTICAST_LOOP")): self.connection.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
				if (hasattr(socket, "IP_MULTICAST_TTL")): self.connection.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ipv4_udp_ttl)

				self.connection.connect(( self.ssdp_host, self.port ))
			#
			else:
			#
				self.connection = UdpNeIpv6Socket()
				self.connection.bind(( "::", self.source_port ))

				if (hasattr(socket, "IPPROTO_IPV6")):
				#
					if (hasattr(socket, "IPV6_MULTICAST_LOOP")): self.connection.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 0)
					if (hasattr(socket, "IPV6_MULTICAST_HOPS")): self.connection.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.ipv6_udp_hops)
				#
			#
		#

		return self.connection
	#

	def request(self, method, data = None):
	#
		"""
Invoke a given SSDP method on the unicast or multicast recipient.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (bool) Request result
:since:  v0.1.00
		"""

		if (data != None): data = Binary.utf8_bytes(data)

		headers = self.headers.copy()

		server_name = "{0}/{1} {2} pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.51 HTTP/1.1"

		headers['SERVER'] = server_name.format(AbstractSsdp._get_os_name(),
		                                       AbstractSsdp._get_os_version(),
		                                       AbstractSsdp._get_upnp_string()
		                                      )

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
		return self._write_data(data)
	#

	def _write_data(self, data):
	#
		"""
Send the given data to the defined recipient.

:param data: SSDP message

:return: (bool) Request result
:since:  v0.1.00
		"""

		# pylint: disable=broad-except

		_return = True

		try: self._get_connection().sendto(data, ( self.ssdp_host, self.port ))
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception, context = "pas_upnp")
			_return = False
		#

		return _return
	#

	@staticmethod
	def add_quirks_mode(mode):
	#
		"""
Adds the defined quirks mode to the already activated ones.

:since: v0.1.00
		"""

		if (type(mode) == str): mode = AbstractSsdp.get_quirks_mode(mode)
		with AbstractSsdp._lock: AbstractSsdp.quirks_mode |= mode
	#

	@staticmethod
	def _get_os_name():
	#
		"""
Returns the OS name based on the currently active quirks mode.

:return: (str) OS name
:since:  v0.1.00
		"""

		if (AbstractSsdp.quirks_mode & AbstractSsdp.QUIRK_OS_LINUX == AbstractSsdp.QUIRK_OS_LINUX): _return = "Linux"
		elif (AbstractSsdp.quirks_mode & AbstractSsdp.QUIRK_OS_WINDOWS == AbstractSsdp.QUIRK_OS_WINDOWS): _return = "Windows"
		else: _return = AbstractSsdp._os_uname[0]

		return _return
	#

	@staticmethod
	def _get_os_version():
	#
		"""
Returns the OS version based on the currently active quirks mode.

:return: (str) OS version
:since:  v0.1.00
		"""

		return ("1.0"
		        if (AbstractSsdp.quirks_mode & AbstractSsdp.QUIRK_OS_VERSION == AbstractSsdp.QUIRK_OS_VERSION) else
		        AbstractSsdp._os_uname[2]
		       )
	#

	@staticmethod
	def get_quirks_mode(mode):
	#
		"""
Adds the defined quirks mode to the already activated ones.

:since: v0.1.00
		"""

		if (mode == "quirk_os_linux"): return AbstractSsdp.QUIRK_OS_LINUX
		elif (mode == "quirk_os_version"): return AbstractSsdp.QUIRK_OS_VERSION
		elif (mode == "quirk_os_windows"): return AbstractSsdp.QUIRK_OS_WINDOWS
		elif (mode == "quirk_upnp_1_0"): return AbstractSsdp.QUIRK_UPNP_1_0
		else: return 0
	#

	@staticmethod
	def _get_upnp_string():
	#
		"""
Returns the supported UPnP specification string based on the currently
active quirks mode.

:return: (str) UPnP specification string
:since:  v0.1.00
		"""

		return ("UPnP/2.0 UPnP/1.0"
		        if (AbstractSsdp.quirks_mode & AbstractSsdp.QUIRK_UPNP_1_0 == AbstractSsdp.QUIRK_UPNP_1_0) else
		        "UPnP/2.0"
		       )
	#

	@staticmethod
	def remove_quirks_mode(mode):
	#
		"""
Removes the defined quirks mode from the activated ones.

:since: v0.1.00
		"""

		with AbstractSsdp._lock: AbstractSsdp.quirks_mode &= ~mode
	#
#

##j## EOF