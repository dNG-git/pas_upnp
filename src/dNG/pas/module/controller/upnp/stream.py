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
from dNG.pas.vfs.implementation import Implementation

# pylint: disable=import-error,no-name-in-module

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.http.streaming import Streaming
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.streamer.file_like import FileLike
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hook import Hook
from .access_check_mixin import AccessCheckMixin
from .dlna_headers_mixin import DlnaHeadersMixin
from .module import Module

class Stream(Module, AccessCheckMixin, DlnaHeadersMixin):
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

	def __init__(self):
	#
		"""
Constructor __init__(AbstractHttpController)

:since: v0.1.00
		"""

		Module.__init__(self)
		AccessCheckMixin.__init__(self)
		DlnaHeadersMixin.__init__(self)
	#

	def execute_resource(self):
	#
		"""
Action for "resource"

:since: v0.1.03
		"""

		rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))

		client_settings = self.get_client_settings()

		self.response.init(True, compress = client_settings.get("upnp_http_compression_supported", True))

		self._ensure_access_granted()

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

		if (resource is None): raise TranslatableError("pas_http_core_404", 404)

		if ((not resource.is_supported("stream_vfs_url"))
		    and (not resource.is_supported("vfs_url"))
		   ): raise TranslatableError("pas_http_core_400", 400)

		if (self.response.is_supported("headers")):
		#
			Stream._add_dlna_headers(self.request, self.response, resource)

			self.response.set_header("Content-Type", resource.get_mimetype())
		#

		vfs_url = (resource.get_stream_vfs_url()
		           if (resource.is_supported("stream_vfs_url"))
		           else resource.get_vfs_url()
		          )

		if (client_settings.get("upnp_stream_filter_url_hook_call", False)):
		#
			vfs_url_filtered = Hook.call("dNG.pas.upnp.Stream.filterUrl",
			                             resource = resource,
			                             vfs_url = vfs_url,
			                             request = self.request,
			                             response = self.response,
			                             client_user_agent = self.client_user_agent
			                            )

			if (vfs_url_filtered is not None): vfs_url = vfs_url_filtered
		#

		vfs_url_elements = urlsplit(vfs_url)

		streamer_class = (""
		                  if (vfs_url_elements.scheme == "") else
		                  "".join([ word.capitalize() for word in vfs_url_elements.scheme.split("-") ])
		                 )

		streamer = None

		if (streamer_class == "" or (not NamedLoader.is_defined("dNG.pas.data.streamer.{0}".format(streamer_class)))):
		#
			vfs_object = Implementation.load_vfs_url(vfs_url, True)
			if (not vfs_object.is_valid()): raise TranslatableError("pas_http_core_400", 400)

			streamer = FileLike()
			streamer.set_file(vfs_object)
			streamer.set_size(resource.get_size())
		#
		else:
		#
			streamer = NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(streamer_class))
			if (not streamer.open_url(vfs_url)): raise TranslatableError("pas_http_core_400", 400)
		#

		if (client_settings.get("upnp_stream_handle_event_hook_call", False)):
		#
			Hook.call("dNG.pas.upnp.Stream.onHandle",
			          resource = resource,
			          streamer = streamer,
			          request = self.request,
			          response = self.response,
			          client_user_agent = self.client_user_agent
			         )
		#

		Streaming.handle(self.request, streamer, self.response)
	#
#

##j## EOF