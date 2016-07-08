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

from os import path
import os

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.data.cache.file import File as CacheFile
from dNG.data.http.streaming import Streaming
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.media.image import Image as _Image
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.data.streamer.file_like import FileLike
from dNG.data.text.input_filter import InputFilter
from dNG.data.upnp.device import Device
from dNG.data.upnp.resource import Resource
from dNG.data.upnp.resources.abstract_item_resource import AbstractItemResource
from dNG.database.connection import Connection
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.net.upnp.control_point import ControlPoint
from dNG.runtime.not_implemented_class import NotImplementedClass

from .dlna_headers_mixin import DlnaHeadersMixin
from .module import Module

class Image(Module, DlnaHeadersMixin):
#
	"""
Service for "m=upnp;s=image"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def _add_resource_dlna_headers(self, resource):
	#
		"""
Adds DLNA headers of the given resource if requested.
@TODO: Rewrite

:param resource: UPnP resource instance

:since: v0.2.00
		"""

		item_resource = None

		if (resource is not None):
		#
			item_resource = (resource
			                 if (isinstance(resource, AbstractItemResource)) else
			                 resource.get_content(0)
			                )
		#

		if (item_resource is not None):
		#
			Image._add_dlna_headers(self.request, self.response, resource)
		#
	#

	def execute_device_icon(self):
	#
		"""
Action for "device_icon"

:since: v0.2.00
		"""

		usn = InputFilter.filter_control_chars(self.request.get_dsd("uusn", ""))
		mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
		width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
		height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
		depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))

		if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400")

		upnp_control_point = ControlPoint.get_instance()

		if (usn != ""):
		#
			device = upnp_control_point.get_device(Device.get_identifier(usn))
			if (device is None): raise TranslatableException("pas_http_core_400")
			file_path_name = device.get_icon_file_path_name()

			if (file_path_name is not None): self._stream_transformed_file(file_path_name, mimetype, width, height, depth)
		#
	#

	def execute_resource_thumbnail(self):
	#
		"""
Action for "resource_thumbnail"

:since: v0.2.00
		"""

		rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))
		mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
		width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
		height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
		depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))
		type_id = InputFilter.filter_control_chars(self.request.get_dsd("utype_id", ""))

		if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400")

		resource = Resource.load_cds_id(rid, self.client_user_agent)

		if (resource is not None and resource.is_supported("thumbnail_file")):
		#
			self._add_resource_dlna_headers(resource)

			self._stream_transformed_file(resource.get_thumbnail_file_path_name(),
			                              mimetype,
			                              width,
			                              height,
			                              depth,
			                              type_id,
			                              _Image.RESIZE_SCALED_CROP
			                             )
		#
	#

	def execute_transformed_resource(self):
	#
		"""
Action for "transformed_resource"

:since: v0.2.00
		"""

		rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))
		mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
		width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
		height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
		depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))
		type_id = InputFilter.filter_control_chars(self.request.get_dsd("utype_id", ""))

		if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400")

		resource = Resource.load_cds_id(rid, self.client_user_agent)

		if (resource is not None and resource.is_supported("thumbnail_file")):
		#
			self._add_resource_dlna_headers(resource)

			self._stream_transformed_file(resource.get_thumbnail_file_path_name(),
			                              mimetype,
			                              width,
			                              height,
			                              depth,
			                              type_id,
			                              _Image.RESIZE_SCALED_FIT
			                             )
		#
	#

	def _stream_transformed_file(self, file_path_name, mimetype, width, height, depth = 24, type_id = None, resize_mode = _Image.RESIZE_SCALED_FIT):
	#
		"""
Creates and streams the transformed file.

:since: v0.2.00
		"""

		if (issubclass(_Image, NotImplementedClass)
		    or (not _Image().is_supported("transformation"))
		   ): raise TranslatableException("core_unknown_error")

		if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400")

		self.response.set_header("X-Robots-Tag", "noindex")

		is_modified = True
		is_valid = (file_path_name is not None and path.exists(file_path_name) and os.access(file_path_name, os.R_OK))
		last_modified_on_server = 0

		if (is_valid):
		#
			if (self.request.get_header("If-Modified-Since") is not None):
			#
				last_modified_on_client = RfcBasics.get_rfc7231_timestamp(self.request.get_header("If-Modified-Since").split(";")[0])

				if (last_modified_on_client > -1):
				#
					last_modified_on_server = int(os.stat(file_path_name).st_mtime)

					if (last_modified_on_server <= last_modified_on_client):
					#
						is_modified = False
						self.response.set_content_dynamic(False)

						self.response.init(True)
						self.response.set_header("HTTP/1.1", "HTTP/1.1 304 Not Modified", True)
						self.response.set_expires_relative(+63072000)
						self.response.set_last_modified(last_modified_on_server)

						self.response.set_raw_data("")
					#
				#
			#
		#

		if (is_valid and is_modified):
		#
			with Connection.get_instance():
			#
				cache_url = "x-upnp-transformed-image:///{0}?mimetype={1};width={2:d};height={3:d};depth={4:d}"

				cache_url = cache_url.format(quote(file_path_name),
				                             mimetype,
				                             width,
				                             height,
				                             depth
				                            )

				if (type_id is not None
				    and type_id != ""
				   ): cache_url += ";type_id={0}".format(type_id)

				if (last_modified_on_server < 1): last_modified_on_server = int(os.stat(file_path_name).st_mtime)
				self.response.set_last_modified(last_modified_on_server)

				icon_file = None

				try:
				#
					icon_file = CacheFile.load_resource(cache_url)

					if (not icon_file.is_up_to_date(last_modified_on_server)):
					#
						icon_file.delete()
						icon_file = None
					#
				#
				except NothingMatchedException: pass

				if (icon_file is None):
				#
					image = _Image()

					if (not image.open_url("file:///{0}".format(quote(file_path_name)))): raise TranslatableException("core_unknown_error")

					image.set_mimetype(mimetype)
					image.set_resize_mode(resize_mode)
					image.set_size(width, height)

					if (depth == 8): image.set_colormap(_Image.COLORMAP_PALETTE)
					elif (depth == 24): image.set_colormap(_Image.COLORMAP_RGB)
					elif (depth == 32): image.set_colormap(_Image.COLORMAP_RGBA)

					image.transform()

					icon_file = CacheFile()

					icon_file.set_data_attributes(time_cached = last_modified_on_server,
					                              resource = cache_url,
					                             )

					icon_file.write(image.read())
					icon_file.save()

					icon_file.seek(0)
				#

				self.response.set_content_dynamic(False)
				self.response.init(True)
				self.response.set_header("Content-Type", mimetype)

				streamer = FileLike()
				streamer.set_file(icon_file)
				streamer.set_size(icon_file.get_size())

				Streaming.handle(self.request, streamer, self.response)
			#
		#
	#
#

##j## EOF