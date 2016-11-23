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

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
    from urllib import quote, unquote
    from urlparse import urlsplit
#

from dNG.data.binary import Binary
from dNG.module.named_loader import NamedLoader
from dNG.runtime.io_exception import IOException
from dNG.runtime.type_exception import TypeException

from .abstract import Abstract

class AbstractItemResource(Abstract):
    """
"AbstractItemResource" represents a UPnP resource "res" entry with support
to set metadata from the corresponding parent.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(AbstractItemResource)

:since: v0.2.00
        """

        Abstract.__init__(self)

        self.metadata = { }
        """
Dict of UPnP resource metadata
        """
        self.parent_resource = None
        """
UPnP parent resource instance
        """
        self.use_parent_resource_data = True
        """
True to use the UPnP resource data from the parent one if supported
        """
        self.use_parent_resource_metadata = True
        """
True to copy UPnP resource metadata from the parent resource if supported
        """
        self.vfs_url = None
        """
VFS URL to read data from
        """

        self.supported_features['metadata'] = True
        self.supported_features['stream_vfs_url'] = self._supports_stream_vfs_url

        self.virtual_resource = True
    #

    def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
        """
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
       item")

:since: v0.2.00
        """

        if (self.get_type() & AbstractItemResource.TYPE_CDS_RESOURCE == AbstractItemResource.TYPE_CDS_RESOURCE):
            attributes = { }
            didl_fields = self.get_didl_fields()
            res_protocol = self.get_didl_res_protocol()
            size = self.get_size()

            if (res_protocol is not None): attributes['protocolInfo'] = res_protocol
            if (size is not None): attributes['size'] = size

            didl_fields_filtered = (len(didl_fields) > 0)

            metadata = self.get_metadata()

            for key in metadata:
                if ((not didl_fields_filtered) or "res@{0}".format(key) in didl_fields): attributes[key] = metadata[key]
            #

            url = Binary.str(self.get_content(0))
            value = (url if (type(url) is str) else "")

            xml_resource.add_node(xml_node_path, value, attributes)
        #
    #

    def get_metadata(self, **kwargs):
        """
Sets additional metadata used for "_add_metadata_to_didl_xml_node()" of this
UPnP resource.

:since: v0.2.00
        """

        _return = { }

        if (self.use_parent_resource_data and self.use_parent_resource_metadata):
            self._init_parent_resource()

            if (self.parent_resource is not None
                and self.parent_resource.is_supported("upnp_resource_metadata")
               ): _return.update(self.parent_resource.get_upnp_resource_metadata())
        #

        _return.update(self.metadata)

        return _return
    #

    def get_mimeclass(self):
        """
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class
:since:  v0.2.00
        """

        return self._get_or_load_from_parent_resource("mimeclass")
    #

    def get_mimetype(self):
        """
Returns the UPnP resource mime type.

:return: (str) UPnP resource mime type
:since:  v0.2.00
        """

        return self._get_or_load_from_parent_resource("mimetype")
    #

    def get_name(self):
        """
Returns the UPnP resource name.

:return: (str) UPnP resource name
:since:  v0.2.00
        """

        return self._get_or_load_from_parent_resource("name")
    #

    def _get_or_load_from_parent_resource(self, name):
        """
Returns the given attribute value or loads it from the UPnP parent resource
if not defined.
        """

        _return = getattr(self, name, None)

        if (_return is None and self.use_parent_resource_data):
            self._init_parent_resource()

            py_getter_method = getattr(self.parent_resource, "get_{0}".format(name))
            _return = py_getter_method()
        #

        return _return
    #

    def get_size(self):
        """
Returns the UPnP resource size.

:return: (int) UPnP resource size; None if unknown
:since:  v0.2.00
        """

        return self._get_or_load_from_parent_resource("size")
    #

    def get_timestamp(self):
        """
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.2.00
        """

        return self._get_or_load_from_parent_resource("timestamp")
    #

    def get_stream_vfs_url(self):
        """
Returns the stream VFS URL.

:return: (str) Stream VFS URL
:since:  v0.2.00
        """

        self._init_stream_vfs_url()
        if (self.vfs_url is None): raise IOException("Stream VFS URL is not defined")

        return self.vfs_url
    #

    def init_cds_id(self, _id, client_user_agent = None, deleted = False):
        """
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
        """

        _return = Abstract.init_cds_id(self, _id, client_user_agent, deleted)

        if (_return and "://" in self.resource_id):
            url_elements = urlsplit(self.resource_id)

            item_resource_scheme = (NamedLoader.RE_CAMEL_CASE_SPLITTER
                                    .sub("\\1-\\2", self.__class__.__name__)
                                    .lower()
                                   )

            if (url_elements.scheme == item_resource_scheme):
                resource_id = unquote(url_elements.path[1:])

                self.set_parent_resource_id(resource_id)
            else:
                self.set_parent_resource_id(self.resource_id)

                self.resource_id = "{0}:///{1}".format(item_resource_scheme,
                                                       quote(self.resource_id, "/")
                                                      )
            #

            _return = True
        #

        if (_return):
            self.type = AbstractItemResource.TYPE_CDS_RESOURCE
        #

        return _return
    #

    def _init_parent_resource(self):
        """
Initialize the UPnP parent resource instance.

:since: v0.2.00
        """

        if (self.parent_resource is None
            and self.parent_resource_id is not None
           ):
            if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_parent_resource()- (#echo(__LINE__)#)", self, context = "pas_upnp")

            with self._lock:
                # Thread safety
                if (self.parent_resource is None):
                    self.parent_resource = AbstractItemResource.load_cds_id(self.get_parent_resource_id(), self.get_client_user_agent())

                    if (self.mimeclass is None): self.set_mimeclass(self.parent_resource.get_mimeclass())
                    if (self.mimetype is None): self.set_mimetype(self.parent_resource.get_mimetype())
                    if (self.size is None): self.set_size(self.parent_resource.get_size())
                #
            #
        #
    #

    def _init_stream_vfs_url(self):
        """
Initialize the stream VFS URL.

:since: v0.2.00
        """

        if (self.vfs_url is None):
            if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_stream_vfs_url()- (#echo(__LINE__)#)", self, context = "pas_upnp")

            self._init_parent_resource()

            if (self.parent_resource is not None
                and self.parent_resource.is_supported("vfs_url")
               ): self.vfs_url = self.parent_resource.get_vfs_url()
        #
    #

    def set_metadata(self, **kwargs):
        """
Sets additional metadata used for "_add_metadata_to_didl_xml_node()" of this
UPnP resource.

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_metadata({1})- (#echo(__LINE__)#)", self, kwargs, context = "pas_upnp")
        self.metadata.update(kwargs)
    #

    def set_mimeclass(self, mimeclass):
        """
Sets the UPnP resource mime class.

:param mimeclass: UPnP resource mime class

:since: v0.2.00
        """

        if (mimeclass is None): raise TypeException("Mime class given is invalid")

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimeclass({1})- (#echo(__LINE__)#)", self, mimeclass, context = "pas_upnp")
        self.mimeclass = mimeclass
    #

    def set_mimetype(self, mimetype):
        """
Sets the UPnP resource mime type.

:param mimetype: UPnP resource mime type

:since: v0.2.00
        """

        if (mimetype is None): raise TypeException("Mime type given is invalid")

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimetype({1})- (#echo(__LINE__)#)", self, mimetype, context = "pas_upnp")
        self.mimetype = mimetype
    #

    def set_size(self, size):
        """
Sets the UPnP resource size.

:param size: UPnP resource size

:since: v0.2.00
        """

        if (size is None): raise TypeException("Size given is invalid")

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_size({1:d})- (#echo(__LINE__)#)", self, size, context = "pas_upnp")
        self.size = size
    #

    def set_stream_vfs_url(self, vfs_url):
        """
Sets the stream VFS URL.

:param vfs_url: Stream VFS URL to use

:since: v0.2.00
        """

        if (vfs_url is None): raise TypeException("Stream VFS URL given is invalid")

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_stream_vfs_url({1})- (#echo(__LINE__)#)", self, vfs_url, context = "pas_upnp")
        self.vfs_url = vfs_url
    #

    def _supports_stream_vfs_url(self):
        """
Returns false if no stream VFS URL is supported.

:return: (bool) True if a stream VFS URL is supported
:since:  v0.2.00
        """

        self._init_stream_vfs_url()
        return (self.vfs_url is not None)
    #
#
