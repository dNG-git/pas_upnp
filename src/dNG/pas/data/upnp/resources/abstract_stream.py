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

from os import path

try: from urllib.parse import unquote, urlsplit
except ImportError:
#
	from urllib import unquote
	from urlparse import urlsplit
#

from dNG.pas.data.binary import Binary
from dNG.pas.data.mime_type import MimeType
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.type_exception import TypeException

class AbstractStream(Resource):
#
	"""
"AbstractStream" represents a UPNP resource "res" entry with support to set
metadata from the corresponding parent.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractStream)

:since: v0.1.00
		"""

		Resource.__init__(self)

		self.metadata = { }
		"""
Dict of UPnP resource metadata
		"""

		self.supported_features['metadata'] = True
	#

	def _add_metadata_to_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
	#
		"""
Uses the given XML resource to add the DIDL metadata of this UPnP resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		if (self.get_type() & Resource.TYPE_CDS_RESOURCE == Resource.TYPE_CDS_RESOURCE):
		#
			attributes = None
			didl_fields = self.get_didl_fields()
			res_protocol = self.get_didl_res_protocol()
			size = self.get_size()

			attributes = { }

			if (res_protocol is not None): attributes['protocolInfo'] = res_protocol
			if (size is not None): attributes['size'] = size

			didl_fields_filtered = (len(didl_fields) > 0)

			for key in self.metadata:
			#
				if ((not didl_fields_filtered) or "res@{0}".format(key) in didl_fields): attributes[key] = self.metadata[key]
			#

			url = Binary.str(self.get_content(0))
			value = (url if (type(url) is str) else "")

			xml_resource.add_node(xml_node_path, value, attributes)
		#
	#

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		Resource.init_cds_id(self, _id, client_user_agent, deleted)

		_return = (self.resource_id is not None)
		if (_return): _return = self._init_cds_resource(deleted)

		return _return
	#

	def _init_cds_resource(self, deleted = False):
	#
		"""
Initialize a UPnP CDS resource instance.

:param _id: UPnP CDS ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.02
		"""

		_return = True

		url_elements = urlsplit(self.resource_id)

		streamer_class = (None
		                  if (url_elements.scheme == "") else
		                  "".join([ word.capitalize() for word in url_elements.scheme.split("-") ])
		                 )

		streamer = (None
		            if (streamer_class == "") else
		            NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(streamer_class), False)
		           )

		if (streamer is not None and streamer.is_url_supported(self.resource_id)):
		#
			self.name = path.basename(unquote(url_elements.path))
			self.type = AbstractStream.TYPE_CDS_RESOURCE

			if (self.mimetype is None):
			#
				mimetype = "application/octet-stream"

				path_ext = path.splitext(url_elements.path)[1]
				mimetype_definition = MimeType.get_instance().get(path_ext[1:])

				if (mimetype_definition is not None):
				#
					self.mimeclass = mimetype_definition['class']
					mimetype = mimetype_definition['type']
				#

				self.set_mimetype(mimetype)
			#

			is_opened = False

			if (self.size is None):
			#
				is_opened = streamer.open_url(self.resource_id)
				if (is_opened): self.size = streamer.get_size()
			#

			if (is_opened): streamer.close()
		#
		else: _return = False

		return _return
	#

	def set_metadata(self, **kwargs):
	#
		"""
Sets metadata used for "_add_metadata_to_didl_xml_node()".

:since: v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_metadata({1})- (#echo(__LINE__)#)", self, kwargs, context = "pas_upnp")
		self.metadata.update(kwargs)
	#

	def set_mimeclass(self, mimeclass):
	#
		"""
Sets the UPnP resource mime class.

:param mimeclass: UPnP resource mime class

:since: v0.1.01
		"""

		if (mimeclass is None): raise TypeException("Mime class given is invalid")

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimeclass({1})- (#echo(__LINE__)#)", self, mimeclass, context = "pas_upnp")
		self.mimeclass = mimeclass
	#

	def set_mimetype(self, mimetype):
	#
		"""
Sets the UPnP resource mime type.

:param mimetype: UPnP resource mime type

:since: v0.1.01
		"""

		if (mimetype is None): raise TypeException("Mime type given is invalid")

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimetype({1})- (#echo(__LINE__)#)", self, mimetype, context = "pas_upnp")
		self.mimetype = mimetype
	#

	def set_size(self, size):
	#
		"""
Sets the UPnP resource size.

:param size: (int) UPnP resource size

:since: v0.1.03
		"""

		if (size is None): raise TypeException("Size given is invalid")

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_size({1:d})- (#echo(__LINE__)#)", self, size, context = "pas_upnp")
		self.size = size
	#
#

##j## EOF