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

# pylint: disable=import-error,no-name-in-module

import socket

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.http.streaming import Streaming
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.resources.abstract_stream import AbstractStream
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.upnp.control_point import ControlPoint
from dNG.pas.plugins.hook import Hook
from .dlna_headers_mixin import DlnaHeadersMixin
from .module import Module

class Stream(Module, DlnaHeadersMixin):
#
	"""
Service for "m=upnp;s=stream"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def execute_resource(self):
	#
		"""
Action for "resource"

:since: v0.1.03
		"""

		rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))

		client_host = self.request.get_client_host()
		client_settings = self.get_client_settings()
		upnp_control_point = ControlPoint.get_instance()

		self.response.init(True, compress = client_settings.get("upnp_http_compression_supported", True))

		if (client_host is None): is_allowed = False
		else:
		#
			ip_address_paths = socket.getaddrinfo(client_host, self.request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
			is_allowed = (False if (len(ip_address_paths) < 1) else upnp_control_point.is_ip_allowed(ip_address_paths[0][4][0]))
		#

		resource = None

		if (is_allowed):
		#
			if (client_settings.get("upnp_stream_filter_resource_id_hook_call", False)):
			#
				rid_filtered = Hook.call("dNG.pas.upnp.Stream.filterResourceID",
				                         rid = rid,
				                         request = self.request,
				                         response = self.response,
				                         client_user_agent = self.client_user_agent
				                        )

				if (rid_filtered is not None): rid = rid_filtered
			#

			resource = Resource.load_cds_id(rid, self.client_user_agent)
		#

		stream_resource = None

		if (resource is not None):
		#
			stream_resource = (resource
			                   if (isinstance(resource, AbstractStream)) else
			                   resource.get_content(0)
			                  )
		#

		if (stream_resource is not None):
		#
			if (self.response.is_supported("headers")):
			#
				Stream._add_dlna_headers(self.request, self.response, resource, stream_resource)
				self.response.set_header("Content-Type", resource.get_mimetype())
			#

			stream_url = InputFilter.filter_control_chars(stream_resource.get_resource_id())

			if (client_settings.get("upnp_stream_filter_url_hook_call", False)):
			#
				stream_url_filtered = Hook.call("dNG.pas.upnp.Stream.filterUrl",
				                                resource = resource,
				                                stream_resource = stream_resource,
				                                url = stream_url,
				                                request = self.request,
				                                response = self.response,
				                                client_user_agent = self.client_user_agent
				                               )

				if (stream_url_filtered is not None): stream_url = stream_url_filtered
			#

			stream_url_elements = urlsplit(stream_url)

			streamer_class = (None
			                  if (stream_url_elements.scheme == "") else
			                  "".join([ word.capitalize() for word in stream_url_elements.scheme.split("-") ])
			                 )

			streamer = (None
			            if (streamer_class == "") else
			            NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(streamer_class), False)
			           )

			if (client_settings.get("upnp_stream_handle_event_hook_call", False)):
			#
				Hook.call("dNG.pas.upnp.Stream.onHandle",
				          resource = resource,
				          stream_resource = stream_resource,
				          streamer = streamer,
				          request = self.request,
				          response = self.response,
				          client_user_agent = self.client_user_agent
				         )
			#

			Streaming.handle_url(self.request, streamer, stream_url, self.response)
		#
		else: self.response.handle_critical_error("core_access_denied")
	#
#

##j## EOF