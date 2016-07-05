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

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.binary import Binary
from dNG.pas.data.supports_mixin import SupportsMixin
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.thread_lock import ThreadLock
from dNG.pas.runtime.value_exception import ValueException
from .client_user_agent_mixin import ClientUserAgentMixin
from .update_id_registry import UpdateIdRegistry

_TOP_LEVEL_OBJECTS = ( "container", "item" )

class Resource(ClientUserAgentMixin, SupportsMixin):
#
	"""
"Resource" represents an UPnP container, item or resource object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	TYPE_CDS_CONTAINER = 1
	"""
UPnP CDS container type
	"""
	TYPE_CDS_CONTAINER_AUDIO = 8
	"""
UPnP CDS audio container type
	"""
	TYPE_CDS_CONTAINER_IMAGE = 16
	"""
UPnP CDS image container type
	"""
	TYPE_CDS_CONTAINER_VIDEO = 32
	"""
UPnP CDS video container type
	"""
	TYPE_CDS_ITEM = 2
	"""
UPnP CDS item type
	"""
	TYPE_CDS_ITEM_AUDIO = 64
	"""
UPnP CDS audio item type
	"""
	TYPE_CDS_ITEM_IMAGE = 128
	"""
UPnP CDS image item type
	"""
	TYPE_CDS_ITEM_VIDEO = 256
	"""
UPnP CDS video item type
	"""
	TYPE_CDS_RESOURCE = 4
	"""
UPnP CDS item type
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Resource)

:since: v0.1.01
		"""

		ClientUserAgentMixin.__init__(self)
		SupportsMixin.__init__(self)

		self.content = None
		"""
UPnP resource content cache
		"""
		self.content_limit = None
		"""
UPnP resource content limit
		"""
		self.content_offset = 0
		"""
UPnP resource content offset
		"""
		self.deleted = False
		"""
True if underlying resource has been deleted
		"""
		self.didl_fields = None
		"""
UPnP resource DIDL fields to be returned
		"""
		self.didl_res_protocol = None
		"""
UPnP resource DIDL protocolInfo value
		"""
		self._lock = ThreadLock()
		"""
Thread safety lock
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.mimeclass = None
		"""
UPnP resource mime class
		"""
		self.mimetype = None
		"""
UPnP resource mime type
		"""
		self.name = None
		"""
UPnP resource name
		"""
		self.parent_resource_id = None
		"""
UPnP resource parent ID
		"""
		self.resource_id = None
		"""
UPnP resource ID
		"""
		self.searchable = False
		"""
True if the UPnP resource provides the search method
		"""
		self.size = None
		"""
UPnP resource size in bytes
		"""
		self.sort_criteria = [ ]
		"""
UPnP resource sort criteria requested
		"""
		self.source = None
		"""
UPnP resource source or creator
		"""
		self.symlink_target_id = None
		"""
UPnP resource symlinked ID
		"""
		self.timestamp = -1
		"""
UPnP resource's timestamp
		"""
		self.type = None
		"""
UPnP resource type
		"""
		self.type_name = None
		"""
UPnP resource type name
		"""
		self.updatable = False
		"""
True if the resource is writable
		"""

		self.supported_features['vfs_url'] = self._supports_vfs_url
	#

	def add_content(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		if (isinstance(resource, Resource) and resource.get_type() is not None):
		#
			with self._lock:
			#
				if (self.content is None): self._init_content()

				if (self.content is not None):
				#
					self.content.append(resource)
					_return = True
				#
			#
		#

		return _return
	#

	def flush_content_cache(self):
	#
		"""
Flushes the content cache.

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.flush_content_cache()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		with self._lock: self.content = None
	#

	def get_content(self, position):
	#
		"""
Returns the UPnP content resource at the given position.

:param position: Position of the UPnP content resource to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_content({1:d})- (#echo(__LINE__)#)", self, position, context = "pas_upnp")

		position -= self.content_offset
		self._init_content()

		return (self.content[position]
		        if (position >= 0 and self.content is not None and len(self.content) > position) else
		        None
		       )
	#

	def get_content_list(self):
	#
		"""
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_content_list()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = [ ]

		self._init_content()

		if (self.content is not None):
		#
			_return = (self.content
			           if (self.content_limit is None) else
			           self.content[self.content_offset:self.content_offset + self.content_limit]
			          )
		#

		return _return
	#

	def get_content_list_of_type(self, _type = None):
	#
		"""
Returns the UPnP content resources of the given type or all ones between
offset and limit.

:param _type: UPnP resource type to be returned

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		if (_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): _return = None
		elif (_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): _return = None
		else: _return = self.get_content_list()

		if (_return is None):
		#
			if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_content_list_of_type()- (#echo(__LINE__)#)", self, context = "pas_upnp")
			_return = [ ]

			for entry in self.get_content_list():
			#
				if (entry.get_type() & _type == _type): _return.append(entry)
			#
		#

		return _return
	#

	def get_didl_fields(self):
	#
		"""
Returns the DIDL fields list.

:return: (list) DIDL fields list
:since:  v0.1.01
		"""

		# global: _TOP_LEVEL_OBJECTS

		didl_fields = self.didl_fields
		_return = [ ]

		if (didl_fields is not None):
		#
			for didl_field in didl_fields:
			#
				didl_field_elements = didl_field.split("@", 1)

				if (len(didl_field_elements) > 1
				    and didl_field_elements[0] in _TOP_LEVEL_OBJECTS
				   ): _return.append("@{0}".format(didl_field_elements[1]))
				else: _return.append(didl_field)
			#
		#

		return _return
	#

	def get_didl_res_protocol(self):
	#
		"""
Returns the DIDL protcolInfo value.

:return: (str) DIDL protocolInfo value; None if undefined
:since:  v0.1.01
		"""

		return self.didl_res_protocol
	#

	def get_mimeclass(self):
	#
		"""
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class
:since:  v0.1.01
		"""

		return ("unknown" if (self.mimeclass is None) else self.mimeclass)
	#

	def get_mimetype(self):
	#
		"""
Returns the UPnP resource mime type.

:return: (str) UPnP resource mime type
:since:  v0.1.01
		"""

		return ("application/octet-stream" if (self.mimetype is None) else self.mimetype)
	#

	def get_name(self):
	#
		"""
Returns the UPnP resource name.

:return: (str) UPnP resource name
:since:  v0.1.01
		"""

		return self.name
	#

	def get_parent_resource_id(self):
	#
		"""
Returns the UPnP resource parent ID.

:return: (str) UPnP resource parent ID; None if empty
:since:  v0.1.01
		"""

		return self.parent_resource_id
	#

	def get_resource_id(self):
	#
		"""
Returns the UPnP resource ID.

:return: (str) UPnP resource ID
:since:  v0.1.01
		"""

		return self.resource_id
	#

	def get_searchable(self):
	#
		"""
Returns if the UPnP resource supports searching.

:return: (bool) True if the content supports searching.
:since:  v0.1.01
		"""

		return self.searchable
	#

	def get_size(self):
	#
		"""
Returns the UPnP resource size.

:return: (int) UPnP resource size; None if unknown
:since:  v0.1.01
		"""

		return self.size
	#

	def get_total(self):
	#
		"""
Returns the number of UPnP content resources.

:return: (int) Number of UPnP content resources
:since:  v0.1.01
		"""

		self._init_content()
		return (0 if (self.content is None) else len(self.content))
	#

	def get_timestamp(self):
	#
		"""
Returns the resource's timestamp if any.

:return: (int) UPnP resource's timestamp of creation or last update
:since:  v0.1.01
		"""

		return self.timestamp
	#

	def get_type(self):
	#
		"""
Returns the UPnP resource type.

:return: (str) UPnP resource type; None if empty
:since:  v0.1.01
		"""

		return self.type
	#

	def get_type_class(self):
	#
		"""
Returns the UPnP resource type class.

:return: (str) UPnP resource type class; None if unknown
:since:  v0.1.00
		"""

		is_cds1_container_supported = False
		is_cds1_object_supported = False
		_type = self.get_type()
		type_class = None

		if (_type is not None):
		#
			client_settings = self.get_client_settings()
			is_cds1_container_supported = client_settings.get("upnp_didl_cds1_container_classes_supported", True)
			is_cds1_object_supported = client_settings.get("upnp_didl_cds1_object_classes_supported", True)
		#

		if (is_cds1_container_supported):
		#
			if (_type & Resource.TYPE_CDS_CONTAINER_AUDIO == Resource.TYPE_CDS_CONTAINER_AUDIO):
			#
				type_class = "object.container.genre.musicGenre"
			#
			elif (_type & Resource.TYPE_CDS_CONTAINER_IMAGE == Resource.TYPE_CDS_CONTAINER_IMAGE):
			#
				type_class = "object.container.album.photoAlbum"
			#
			elif (_type & Resource.TYPE_CDS_CONTAINER_VIDEO == Resource.TYPE_CDS_CONTAINER_VIDEO):
			#
				type_class = "object.container.genre.movieGenre"
			#
		#

		if (is_cds1_object_supported):
		#
			if (_type & Resource.TYPE_CDS_ITEM_AUDIO == Resource.TYPE_CDS_ITEM_AUDIO):
			#
				type_class = "object.item.audioItem.musicTrack"
			#
			elif (_type & Resource.TYPE_CDS_ITEM_IMAGE == Resource.TYPE_CDS_ITEM_IMAGE):
			#
				type_class = "object.item.imageItem.photo"
			#
			elif (_type & Resource.TYPE_CDS_ITEM_VIDEO == Resource.TYPE_CDS_ITEM_VIDEO):
			#
				type_class = "object.item.videoItem.movie"
			#
		#

		if (type_class is None):
		#
			if (self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
			#
				type_class = "object.container"
			#
			elif (self.type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM):
			#
				type_class = "object.item"
			#
		#

		return type_class
	#

	def get_type_name(self):
	#
		"""
Returns the UPnP resource type class name.

:return: (str) UPnP resource type class name; None if unknown
:since:  v0.1.01
		"""

		return self.type_name
	#

	def get_updatable(self):
	#
		"""
Returns if the UPnP resource can be changed.

:return: (bool) True if the content can be changed.
:since:  v0.1.01
		"""

		return self.updatable
	#

	def get_update_id(self):
	#
		"""
Returns the UPnP UpdateID value.

:return: (int) UPnP UpdateID value
:since:  v0.1.02
		"""

		return UpdateIdRegistry.get(self.get_resource_id())
	#

	def get_vfs_url(self):
	#
		"""
Returns the VFS URL of this instance.

:return: (str) UPnP resource VFS URL; None if undefined
:since:  v0.1.00
		"""

		return self.get_resource_id()
	#

	def init(self, data):
	#
		"""
Initializes a new resource with the data given.

:param data: UPnP resource data

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.init()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		is_id_defined = ("id" in data)

		if ((self.resource_id is not None or is_id_defined)
		    and "name" in data
		    and "type" in data
		   ):
		#
			if (is_id_defined):
			#
				if (data['id'] == "0"): raise ValueException("Special UPnP resource ID '0' is not supported")
				self.resource_id = data['id']
			#

			self.name = data['name']
			self.type = data['type']

			if ("parent_id" in data): self.parent_resource_id = data['parent_id']
			if ("searchable" in data): self.searchable = data['searchable']
			if ("source" in data): self.source = data['source']
			if ("symlink_target_id" in data): self.symlink_target_id = data['symlink_target_id']
			if ("type_name" in data): self.type_name = data['type_name']
			if ("update_id" in data): self.set_update_id(data['update_id'])
			if ("updatable" in data): self.updatable = data['updatable']

			_return = True
		#

		return _return
	#

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: UPnP UpdateID value
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.init_cds_id({1})- (#echo(__LINE__)#)", self, _id, context = "pas_upnp")
		_return = True

		if (client_user_agent is not None): self.client_user_agent = client_user_agent

		if (_id is None): _return = False
		else: self.resource_id = _id

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		if (self.content is None):
		# Thread safety
			with self._lock:
			#
				if (self.content is None): self.content = [ ]
			#
		#

		return True
	#

	def remove_content(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.remove_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		if (isinstance(resource, Resource) and resource.get_type() is not None):
		#
			with self._lock:
			#
				if (self.content is None): self._init_content()

				if (self.content is not None):
				#
					if (resource in self.content):
					#
						self.content.remove(resource)
						_return = True
					#
				#
			#
		#

		return _return
	#

	def set_content_limit(self, content_limit):
	#
		"""
Sets the UPnP resource content limit.

:param content_limit: Resource content limit

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_content_limit({1:d})- (#echo(__LINE__)#)", self, content_limit, context = "pas_upnp")

		self.flush_content_cache()
		self.content_limit = content_limit
	#

	def set_content_offset(self, content_offset):
	#
		"""
Sets the UPnP resource content offset.

:param content_offset: Resource content offset

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_content_offset({1:d})- (#echo(__LINE__)#)", self, content_offset, context = "pas_upnp")

		self.flush_content_cache()
		self.content_offset = content_offset
	#

	def set_didl_fields(self, fields):
	#
		"""
Sets the DIDL fields to be returned.

:param fields: DIDL fields list

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_didl_fields()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		if (type(fields) is list): self.didl_fields = fields
	#

	def set_parent_resource_id(self, _id):
	#
		"""
Sets the UPnP resource parent ID.

:param _id: UPnP resource parent ID

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_parent_resource_id()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		self.parent_resource_id = _id
	#

	def set_sort_criteria(self, sort_criteria):
	#
		"""
Sets the UPnP sort criteria.

:param sort_criteria: UPnP sort criteria

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_sort_criteria()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		if (type(sort_criteria) is list): self.sort_criteria = sort_criteria
		else:
		#
			sort_criteria = Binary.str(sort_criteria)
			self.sort_criteria = (sort_criteria.split(",") if (type(sort_criteria) is str and len(sort_criteria) > 0) else [ ])
		#
	#

	def set_update_id(self, update_id):
	#
		"""
Sets the UPnP UpdateID value or increments it.

:param update_id: UPnP UpdateID value or "++" to increment it; "--" for deletion

:since: v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_update_id()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		if (update_id == "--"): UpdateIdRegistry.unset(self.get_resource_id())
		else: UpdateIdRegistry.set(self.get_resource_id(), update_id, self)
	#

	def _supports_vfs_url(self):
	#
		"""
Returns false if the UPnP resource can not provide a supported VFS URL.

:return: (bool) True if UPnP resource can provide a supported VFS URL.
:since:  v0.2.00
		"""

		return (self.get_type() & Resource.TYPE_CDS_RESOURCE == Resource.TYPE_CDS_RESOURCE)
	#

	@staticmethod
	def load_cds_id(_id, client_user_agent = None, cds = None, deleted = False):
	#
		"""
Load a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS
:param deleted: True to include deleted resources

:return: (object) Resource object; None on error
:since:  v0.1.01
		"""

		_return = None

		if (_id == "0" and cds is not None):
		#
			_return = NamedLoader.get_instance("dNG.pas.data.upnp.resources.RootContainer")
			_return.init_cds_id(_id, client_user_agent, deleted)
		#
		elif (_id is not None and "://" in _id):
		#
			url_elements = urlsplit(_id)

			if (url_elements.scheme != ""):
			#
				resource_class_name = "".join([ word.capitalize() for word in url_elements.scheme.split("-") ])
				resource = NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}".format(resource_class_name), False)

				if (isinstance(resource, Resource) and resource.init_cds_id(_id, client_user_agent, deleted)): _return = resource
			#
		#

		return _return
	#
#

##j## EOF