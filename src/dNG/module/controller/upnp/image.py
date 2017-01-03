# -*- coding: utf-8 -*-

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

# pylint: disable=import-error,no-name-in-module

try: from urllib.parse import quote
except ImportError: from urllib import quote

from dNG.data.http.streaming import Streaming
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.media.abstract_image import AbstractImage
from dNG.data.media.image_implementation import ImageImplementation
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.data.streamer.file_like import FileLike
from dNG.data.text.input_filter import InputFilter
from dNG.data.upnp.device import Device
from dNG.data.upnp.resource import Resource
from dNG.net.upnp.control_point import ControlPoint
from dNG.runtime.not_implemented_class import NotImplementedClass
from dNG.vfs.implementation import Implementation

from .dlna_headers_mixin import DlnaHeadersMixin
from .module import Module

class Image(Module, DlnaHeadersMixin):
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

    def execute_device_icon(self):
        """
Action for "device_icon"

:since: v0.2.00
        """

        usn = InputFilter.filter_control_chars(self.request.get_dsd("uusn", ""))
        mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
        width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
        height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
        depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))

        if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400", 400)

        upnp_control_point = ControlPoint.get_instance()

        if (usn != ""):
            device = upnp_control_point.get_device(Device.get_identifier(usn))
            if (device is None): raise TranslatableException("pas_http_core_400", 400)
            file_path_name = device.get_icon_file_path_name()

            if (file_path_name is not None):
                self._stream_transformed_vfs_url("file:///{0}".format(quote(file_path_name, "/")),
                                                 mimetype,
                                                 width,
                                                 height,
                                                 depth
                                                )
            #
        #
    #

    def execute_resource_thumbnail(self):
        """
Action for "resource_thumbnail"

:since: v0.2.00
        """

        rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))
        mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
        width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
        height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
        depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))

        if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400", 400)

        resource = Resource.load_cds_id(rid, self.get_client_settings())

        if (resource is not None and resource.is_supported("thumbnail_source_vfs_url")):
            Image._add_dlna_headers(self.request, self.response, resource)

            self._stream_transformed_vfs_url(resource.get_thumbnail_source_vfs_url(),
                                             mimetype,
                                             width,
                                             height,
                                             depth,
                                             AbstractImage.RESIZE_SCALED_CROP
                                            )
        #
    #

    def execute_transformed_resource(self):
        """
Action for "transformed_resource"

:since: v0.2.00
        """

        rid = InputFilter.filter_control_chars(self.request.get_dsd("urid", ""))
        mimetype = InputFilter.filter_control_chars(self.request.get_dsd("umimetype", ""))
        width = InputFilter.filter_int(self.request.get_dsd("uwidth", 0))
        height = InputFilter.filter_int(self.request.get_dsd("uheight", 0))
        depth = InputFilter.filter_int(self.request.get_dsd("udepth", 24))

        if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400", 400)

        resource = Resource.load_cds_id(rid, self.get_client_settings())

        if (resource is not None and resource.is_supported("thumbnail_source_vfs_url")):
            Image._add_dlna_headers(self.request, self.response, resource)

            self._stream_transformed_vfs_url(resource.get_thumbnail_source_vfs_url(),
                                             mimetype,
                                             width,
                                             height,
                                             depth,
                                             AbstractImage.RESIZE_SCALED_FIT
                                            )
        #
    #

    def _stream_transformed_vfs_url(self, source_vfs_url, mimetype, width, height, depth = 24, resize_mode = AbstractImage.RESIZE_SCALED_FIT):
        """
Creates and streams the transformed file.

:since: v0.2.00
        """

        if (source_vfs_url is None): raise TranslatableException("pas_http_core_500")

        image = ImageImplementation.get_instance()
        vfs_object = Implementation.load_vfs_url(source_vfs_url, True)

        if (isinstance(image, NotImplementedClass)
            or (not image.is_supported("transformation"))
           ): raise TranslatableException("core_unknown_error")

        if (width < 1 or height < 1): raise TranslatableException("pas_http_core_400", 400)

        self.response.set_header("X-Robots-Tag", "noindex")

        is_modified = True
        is_valid = vfs_object.is_valid()
        last_modified_on_server = int(vfs_object.get_time_updated())

        if (is_valid):
            if (self.request.get_header("If-Modified-Since") is not None):
                last_modified_on_client = RfcBasics.get_rfc7231_timestamp(self.request.get_header("If-Modified-Since").split(";")[0])

                if (last_modified_on_client > -1):
                    if (last_modified_on_server <= last_modified_on_client):
                        is_modified = False
                        self.response.set_content_dynamic(False)

                        self.response.init(True)
                        self.response.set_header("HTTP", "HTTP/2.0 304 Not Modified", True)
                        self.response.set_expires_relative(+63072000)
                        self.response.set_last_modified(last_modified_on_server)

                        self.response.set_raw_data("")
                    #
                #
            #
        #

        if (is_valid and is_modified):
            transformed_vfs_url = "x-media-transformed-image:///{0}?mimetype={1}&width={2:d}&height={3:d}&depth={4:d}&resize_mode={5:d}"

            transformed_vfs_url = transformed_vfs_url.format(quote(vfs_object.get_url(), "/"),
                                                             quote(mimetype, ""),
                                                             width,
                                                             height,
                                                             depth,
                                                             resize_mode
                                                            )

            self.response.set_last_modified(last_modified_on_server)

            transformed_file = Implementation.load_vfs_url(transformed_vfs_url)

            self.response.set_content_dynamic(False)
            self.response.init(True)
            self.response.set_header("Content-Type", mimetype)

            streamer = FileLike()
            streamer.set_file(transformed_file)

            Streaming.handle(self.request, streamer, self.response)
        #
    #
#
