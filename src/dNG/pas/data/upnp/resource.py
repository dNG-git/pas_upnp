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

from collections import OrderedDict
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.data.rfc.basics import Basics
from dNG.data.xml_resource import XmlResource
from dNG.pas.data.binary import Binary
from dNG.pas.data.supports_mixin import SupportsMixin
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.upnp.update_id_registry import UpdateIdRegistry
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.thread_lock import ThreadLock
from dNG.pas.runtime.value_exception import ValueException
from .client import Client
from .variable import Variable
from .xml_rewrite_parser import XmlRewriteParser

_TOP_LEVEL_OBJECTS = [ "container", "item" ]

class Resource(SupportsMixin):
#
	"""
"Resource" represents an UPnP directory, file or virtual object.

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
	TYPE_CDS_ITEM = 2
	"""
UPnP CDS item type
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

		SupportsMixin.__init__(self)

		self.client_user_agent = None
		"""
Client user agent
		"""
		self.content = None
		"""
UPnP resource content cache
		"""
		self.content_offset = 0
		"""
UPnP resource content offset
		"""
		self.content_limit = None
		"""
UPnP resource content limit
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
		self.id = None
		"""
UPnP resource ID
		"""
		self._lock = ThreadLock()
		"""
Thread safety lock
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
		self.parent_id = None
		"""
UPnP resource parent ID
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

		self.supported_features['search_content'] = self._supports_search_content
	#

	def add_content(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		_return = False

		if (isinstance(resource, Resource) and resource.get_type() != None):
		#
			with self._lock:
			#
				self._init_content()

				self.content.append(resource)
				self.set_update_id("++")

				_return = True
			#
		#

		return _return
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

		attributes = None
		resource_type = self.get_type()
		value = ""

		is_resource_container = (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER)
		is_resource_item = (resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM)
		is_resource_searchable = self.get_searchable()
		is_resource_updatable = self.get_updatable()

		if (parent_id == None): parent_id = self.get_parent_id()

		if (is_resource_container):
		#
			attributes = { "id": self.get_id(),
			               "parentID": parent_id,
			               "restricted": (Variable.BOOL_FALSE if (is_resource_updatable) else Variable.BOOL_TRUE),
			               "searchable": (Variable.BOOL_FALSE if (is_resource_searchable) else Variable.BOOL_TRUE)
			             }

			didl_fields = self.get_didl_fields()
			if (len(didl_fields) < 1 or "@childCount" in didl_fields): attributes['childCount'] = str(self.get_total())
		#
		elif (is_resource_item):
		#
			attributes = { "id": self.get_id(),
			               "parentID": parent_id,
			               "restricted": (Variable.BOOL_FALSE if (is_resource_updatable) else Variable.BOOL_TRUE)
			             }
		#
		elif (resource_type & Resource.TYPE_CDS_RESOURCE == Resource.TYPE_CDS_RESOURCE):
		#
			res_protocol = self.get_didl_res_protocol()
			size = self.get_size()

			if (res_protocol != None):
			#
				attributes = { "protocolInfo": res_protocol }
				if (size != None): attributes['size'] = size

				url = Binary.str(self.get_content(0))
				if (type(url) == str): value = url
			#
		#

		if (attributes != None):
		#
			xml_resource.add_node(xml_node_path, value, attributes)

			if (is_resource_container or is_resource_item):
			#
				type_name = self.get_type_name()
				type_attributes = (None if (type_name == None) else { "name": type_name })

				xml_resource.add_node("{0} dc:title".format(xml_node_path), self.get_name())
				xml_resource.add_node("{0} upnp:class".format(xml_node_path), self.get_type_class(), type_attributes)

				update_id_node_path = ("{0} upnp:containerUpdateID"
				                       if (is_resource_container) else
				                       "{0} upnp:objectUpdateID"
				                      )

				xml_resource.add_node(update_id_node_path.format(xml_node_path), self.get_update_id())

				if (is_resource_container and is_resource_searchable):
				#
					xml_resource.add_node("{0} upnp:searchClass".format(xml_node_path),
					                      "object.item",
					                      { "includeDerived": Variable.BOOL_TRUE }
					                     )
				#

				timestamp = self.get_timestamp()
				if (timestamp > -1): xml_resource.add_node("{0} dc:date".format(xml_node_path), Basics.get_iso8601_datetime(timestamp))
				xml_resource.add_node("{0} upnp:writeStatus".format(xml_node_path), ("WRITABLE" if (is_resource_updatable) else "NOT_WRITABLE"))

				if (is_resource_item): Resource._append_content_didl_xml_nodes(xml_resource, xml_node_path, self.get_content_list(), self.get_id())
			#
		#
	#

	def _filter_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to remove DIDL metadata not requested by the
client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		didl_fields = self.get_didl_fields()
		resource_type = self.get_type()

		if (len(didl_fields) > 0
		    and (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER
		         or resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM
		        )
		    and "upnp:writeStatus" not in didl_fields
		   ): xml_resource.remove_node("{0} upnp:writeStatus".format(xml_node_path))
	#

	def flush_content_cache(self):
	#
		"""
Flushes the content cache.

:since: v0.1.01
		"""

		with self._lock: self.content = None
	#

	def get_client_user_agent(self):
	#
		"""
Returns the UPnP client user agent requesting the resource.

:return: (str) Client user agent if known; None otherwise
:since:  v0.1.00
		"""

		return self.client_user_agent
	#

	def get_content(self, position):
	#
		"""
Returns the UPnP content resource at the given position.

:param position: Position of the UPnP content resource to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.1.01
		"""

		position -= self.content_offset
		self._init_content()

		return (self.content[position] if (position >= 0 and self.content != None and len(self.content) > position) else None)
	#

	def get_content_list(self):
	#
		"""
Returns the UPnP content resources between offset and limit.

:return: (list) List of UPnP resources
:since:  v0.1.01
		"""

		_return = [ ]

		self._init_content()
		if (self.content != None): _return = (self.content if (self.content_limit == None) else self.content[self.content_offset:self.content_offset + self.content_limit])

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

		if (_return == None):
		#
			_return = [ ]

			for entry in self.get_content_list():
			#
				if (entry.get_type() == _type): _return.append(entry)
			#
		#

		return _return
	#

	def get_content_didl_xml(self):
	#
		"""
Returns an UPnP DIDL result of generated XML for all contained UPnP content
resources.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		_return = None

		if (self.type != None and self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			xml_resource = self._init_xml_resource()
			xml_resource.add_node("DIDL-Lite", attributes = Resource._get_didl_xmlns_attributes())

			content_count = Resource._append_content_didl_xml_nodes(xml_resource, "DIDL-Lite", self.get_content_list(), self.get_id())

			_return = { "result": xml_resource.export_cache(True),
			            "number_returned": content_count,
			            "total_matches": self.get_total(),
			            "update_id": self.get_update_id()
			          }
		#

		return _return
	#

	def _get_custom_didl_fields(self, didl_fields):
	#
		"""
Returns the user agent specific DIDL fields requested.

:return: (list) DIDL fields list; None if not filtered
:since:  v0.1.01
		"""

		_return = (None if (self.client_user_agent == None) else Hook.call("dNG.pas.upnp.Resource.getDidlFields", didl_fields = didl_fields, client_user_agent = self.client_user_agent))
		return (didl_fields if (_return == None) else _return)
	#

	def _get_custom_didl_res_protocol(self, didl_res_protocol):
	#
		"""
Returns a user agent specific DIDL protcolInfo value.

:return: (str) DIDL protocolInfo value; None if undefined
:since:  v0.1.01
		"""

		_return = (None if (self.client_user_agent == None) else Hook.call("dNG.pas.upnp.Resource.getDidlResProtocol", didl_res_protocol = didl_res_protocol, client_user_agent = self.client_user_agent))
		return (didl_res_protocol if (_return == None) else _return)
	#

	def _get_custom_mimetype(self, mimetype):
	#
		"""
Returns a user agent specific UPnP resource mime type.

:return: (str) UPnP resource mime type; None if not defined
:since:  v0.1.01
		"""

		_return = (None if (self.client_user_agent == None) else Hook.call("dNG.pas.upnp.Resource.getMimetype", mimetype = mimetype, client_user_agent = self.client_user_agent))
		if (_return == None): _return = mimetype

		client = Client.load_user_agent(self.client_user_agent)
		client_mimetypes = client.get("upnp_custom_mimetypes")
		if (isinstance(client_mimetypes, dict) and _return in client_mimetypes): _return = client_mimetypes[_return]

		return _return
	#

	def _get_custom_type(self, _type):
	#
		"""
Returns a user agent specific UPnP resource type.

:return: (str) UPnP resource type; None if not defined
:since:  v0.1.01
		"""

		_return = (None if (self.client_user_agent == None) else Hook.call("dNG.pas.upnp.Resource.getType", _type = _type, client_user_agent = self.client_user_agent))
		return (_type if (_return == None) else _return)
	#

	def _get_custom_type_class(self, type_class):
	#
		"""
Returns a user agent specific UPnP resource type class.

:return: (str) UPnP resource type class; None if not defined
:since:  v0.1.01
		"""

		_return = (None if (self.client_user_agent == None) else Hook.call("dNG.pas.upnp.Resource.getTypeClass", type_class = type_class, client_user_agent = self.client_user_agent))
		return (type_class if (_return == None) else _return)
	#

	def get_didl_fields(self):
	#
		"""
Returns the DIDL fields requested.

:return: (list) DIDL fields list
:since:  v0.1.01
		"""

		# global: _TOP_LEVEL_OBJECTS

		didl_fields = self._get_custom_didl_fields(self.didl_fields)
		_return = [ ]

		if (didl_fields != None):
		#
			for didl_field in didl_fields:
			#
				didl_field_elements = didl_field.split("@", 1)

				if (len(didl_field_elements) > 1 and didl_field_elements[0] in _TOP_LEVEL_OBJECTS): _return.append("@{0}".format(didl_field_elements[1]))
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

		return self._get_custom_didl_res_protocol(self.didl_res_protocol)
	#

	def get_id(self):
	#
		"""
Returns the UPnP resource ID.

:return: (str) UPnP resource ID
:since:  v0.1.01
		"""

		return self.id
	#

	def get_metadata_didl_xml(self):
	#
		"""
Returns an UPnP DIDL result of generated XML for this UPnP resource.

:return: (dict) Result dict containting the same keys as
         "get_content_didl_xml()"
:since:  v0.1.01
		"""

		_return = None

		if (self.type != None):
		#
			xml_resource = self._init_xml_resource()
			xml_resource.add_node("DIDL-Lite", attributes = Resource._get_didl_xmlns_attributes())

			if (self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): xml_node_path = "DIDL-Lite container"
			elif (self.type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): xml_node_path = "DIDL-Lite item"
			else: xml_node_path = None

			if (xml_node_path != None):
			#
				self._add_metadata_to_didl_xml_node(xml_resource, xml_node_path)
				self._rewrite_metadata_of_didl_xml_node(xml_resource, xml_node_path)
				self._filter_metadata_of_didl_xml_node(xml_resource, xml_node_path)
			#

			_return = { "result": xml_resource.export_cache(True),
			            "number_returned": 1,
			            "total_matches": 1,
			            "update_id": self.get_update_id()
			          }
		#

		return _return
	#

	def get_mimeclass(self):
	#
		"""
Returns the UPnP resource mime class.

:return: (str) UPnP resource mime class
:since:  v0.1.01
		"""

		return ("unknown" if (self.mimeclass == None) else self.mimeclass)
	#

	def get_mimetype(self):
	#
		"""
Returns the UPnP resource mime type.

:return: (str) UPnP resource mime type
:since:  v0.1.01
		"""

		return ("application/octet-stream" if (self.mimetype == None) else self._get_custom_mimetype(self.mimetype))
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

	def get_parent_id(self):
	#
		"""
Returns the UPnP resource parent ID.

:return: (str) UPnP resource parent ID; None if empty
:since:  v0.1.01
		"""

		return self.parent_id
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

	def get_search_capabilities(self):
	#
		"""
Returns the UPnP search capabilities.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		didl_fields = Hook.call("dNG.pas.upnp.Resource.getSearchableDidlFields", client_user_agent = self.client_user_agent)
		if (type(didl_fields) != list or len(didl_fields) < 1): didl_fields = None

		if (didl_fields == None): _return = ""
		else: _return = ",".join(InputFilter.filter_unique_list(didl_fields))

		return _return
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

	def get_sort_capabilities(self):
	#
		"""
Returns the UPnP sort capabilities.

:return: (int) UPnP SystemUpdateID value
:since:  v0.1.00
		"""

		didl_fields = Hook.call("dNG.pas.upnp.Resource.getSortableDidlFields", client_user_agent = self.client_user_agent)
		if (type(didl_fields) != list or len(didl_fields) < 1): didl_fields = None

		if (didl_fields == None): _return = ""
		else: _return = ",".join(InputFilter.filter_unique_list(didl_fields))

		return _return
	#

	def _get_stream_resource(self):
	#
		"""
Returns the UPnP stream resource.

:return: (object) UPnP stream resource; None if not streamable
:since:  v0.1.01
		"""

		mimeclass = self.get_mimeclass()
		mimetype = self.get_mimetype()

		_return = (None if (mimetype == None) else NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Stream".format("".join([word.capitalize() for word in re.split("[\\W_]+", mimetype)])), False))
		if (_return == None): _return = NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}Stream".format("".join([word.capitalize() for word in re.split("[\\W_]+", mimeclass)])), False)
		if (_return == None): _return = NamedLoader.get_instance("dNG.pas.data.upnp.resources.HttpBlockStream", False)

		return _return
	#

	def get_total(self):
	#
		"""
Returns the number of UPnP content resources.

:return: (int) Number of UPnP content resources
:since:  v0.1.01
		"""

		self._init_content()
		return len(self.content)
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

		return self._get_custom_type(self.type)
	#

	def get_type_class(self):
	#
		"""
Returns the UPnP resource type class.

:return: (str) UPnP resource type class; None if unknown
:since:  v0.1.01
		"""

		if (self.type == None): _return = None
		else:
		#
			if (self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): _return = "object.container"
			elif (self.type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): _return = "object.item"

			_return = self._get_custom_type_class(_return)
		#

		return _return
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

		return UpdateIdRegistry.get(self.get_id())
	#

	def init(self, data):
	#
		"""
Initializes a new resource with the data given.

:param data: UPnP resource data

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		_return = False

		if ("id" in data and "name" in data and "type" in data):
		#
			if (data['id'] == "0"): raise ValueException("Special UPnP resource ID '0' is not supported")
			self.id = data['id']
			self.name = data['name']
			self.type = data['type']

			if ("parent_id" in data): self.parent_id = data['parent_id']
			if ("searchable" in data): self.searchable = data['searchable']
			if ("source" in data): self.parent_id = data['source']
			if ("symlink_target_id" in data): self.parent_id = data['symlink_target_id']
			if ("type_name" in data): self.type_name = data['type_name']
			if ("update_id" in data): self.set_update_id(data['update_id'])
			if ("updatable" in data): self.parent_id = data['updatable']

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

		_return = False

		self.id = _id
		if (client_user_agent != None): self.client_user_agent = client_user_agent

		if (_id == "0"):
		#
			self.name = L10n.get("pas_upnp_container_root")
			self.parent_id = "-1"
			self.type = Resource.TYPE_CDS_CONTAINER

			search_callbacks = Hook.call("dNG.pas.upnp.Resource.getSearchCallbacks")
			self.searchable = (search_callbacks != None and len(search_callbacks) > 0)

			_return = True
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.01
		"""

		_return = False

		if (self.content == None):
		# Thread safety
			with self._lock:
			#
				if (self.content == None):
				#
					self.content = [ ]

					if (self.id == "0"):
					#
						Hook.call("dNG.pas.upnp.Resource.getRootResourceClientContent", container = self)
						if (len(self.content) == 0): Hook.call("dNG.pas.upnp.Resource.getRootResourceContent", container = self)
						_return = True
					#
				#
			#
		#

		return _return
	#

	def _init_xml_resource(self):
	#
		"""
Returns a XML parser with predefined XML namespaces.

:return: (object) XML parser
:since:  v0.1.01
		"""

		"""
There are known broken clients defining XML namespaces without the trailing
slash. We define both notations just in case.
		"""

		_return = XmlResource(node_type = OrderedDict)
		_return.register_ns("dc", "http://purl.org/dc/elements/1.1/")
		_return.register_ns("dc", "http://purl.org/dc/elements/1.1")
		_return.register_ns("didl", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/")
		_return.register_ns("didl", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite")
		_return.register_ns("upnp", "urn:schemas-upnp-org:metadata-1-0/upnp/")
		_return.register_ns("upnp", "urn:schemas-upnp-org:metadata-1-0/upnp")

		return _return
	#

	def is_filesystem_resource(self):
	#
		"""
Returns true if the resource is represented in the filesystem.

:return: (bool) True if filesystem resource
:since:  v0.1.01
		"""

		return False
	#

	def remove_content(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.1.01
		"""

		_return = False

		if (self.content != None):
		# Thread safety
			with self._lock:
			#
				if (self.content != None):
				#
					if (resource in self.content):
					#
						self.content.remove(resource)
						self.set_update_id("++")

						_return = True
					#
				#
			#
		#

		return _return
	#

	def _rewrite_metadata_of_didl_xml_node(self, xml_resource, xml_node_path):
	#
		"""
Uses the given XML resource to manipulate DIDL metadata for the client.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      item")

:since:  v0.1.01
		"""

		resource_type = self.get_type()
		title_format = None

		if (resource_type != None):
		#
			client = Client.load_user_agent(self.client_user_agent)

			title_format_resource_name = "upnp_didl_title_{0}_format".format(NamedLoader.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", self.__class__.__name__).lower())

			if (title_format_resource_name in client): title_format = client.get(title_format_resource_name)
			elif (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): title_format = client.get("upnp_didl_title_default_container_format")
			elif (resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): title_format = client.get("upnp_didl_title_default_item_format")

			if (title_format == None): title_format = client.get("upnp_didl_title_default_format")
		#

		if (title_format != None):
		#
			title = XmlRewriteParser().render(title_format, xml_resource, xml_node_path)
			xml_resource.change_node_value("{0} dc:title".format(xml_node_path), title)
		#
	#

	def search_content(self, search_criteria):
	#
		"""
Returns all contained UPnP content resources matching the given UPnP search
criteria.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		_return = [ ]

		return _return
	#

	def search_content_didl_xml(self, search_criteria):
	#
		"""
Returns an UPnP DIDL result of generated XML for all UPnP content resources
matching the given UPnP search criteria.

:return: (dict) Result dict containting "result" as generated XML,
         "number_returned" as the number of DIDL nodes, "total_matches" of
         all DIDL nodes and the current UPnP update ID.
:since:  v0.1.01
		"""

		_return = None

		if (self.type != None and self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			xml_resource = self._init_xml_resource()
			xml_resource.add_node("DIDL-Lite", attributes = Resource._get_didl_xmlns_attributes())

			content_matched = self.search_content(search_criteria)
			content_matched_count = len(content_matched)

			content_count = (Resource._append_content_didl_xml_nodes(xml_resource, "DIDL-Lite", content_matched, self.get_id()) if (content_matched_count > 0) else 0)

			_return = { "result": xml_resource.export_cache(True),
			            "number_returned": content_count,
			            "total_matches": content_matched_count,
			            "update_id": self.get_update_id()
			          }
		#

		return _return
	#

	def set_client_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.1.00
		"""

		self.client_user_agent = user_agent
	#

	def set_content_offset(self, content_offset):
	#
		"""
Sets the UPnP resource content offset.

:param content_offset: UPnP resource content offset

:since: v0.1.01
		"""

		self.content_offset = content_offset
	#

	def set_content_limit(self, content_limit):
	#
		"""
Sets the UPnP resource content limit.

:param content_limit: UPnP resource content limit

:since: v0.1.01
		"""

		self.content_limit = content_limit
	#

	def set_didl_fields(self, fields):
	#
		"""
Sets the DIDL fields to be returned.

:param fields: DIDL fields list

:since: v0.1.01
		"""

		if (type(fields) == list): self.didl_fields = fields
	#

	def set_parent_id(self, _id):
	#
		"""
Sets the UPnP resource parent ID.

:param _id: UPnP resource parent ID

:since: v0.1.01
		"""

		self.parent_id = _id
	#

	def set_sort_criteria(self, sort_criteria):
	#
		"""
Sets the DIDL fields to be returned.

:param fields: DIDL fields list

:since: v0.1.01
		"""

		if (type(sort_criteria) == list): self.sort_criteria = sort_criteria
		else:
		#
			sort_criteria = Binary.str(sort_criteria)
			self.sort_criteria = (sort_criteria.split(",") if (type(sort_criteria) == str and len(sort_criteria) > 0) else [ ])
		#
	#

	def set_update_id(self, update_id):
	#
		"""
Sets the UPnP UpdateID value or increments it.

:param update_id: UPnP UpdateID value or "++" to increment it; "--" for deletion

:since: v0.1.01
		"""

		if (update_id == "--"): UpdateIdRegistry.unset(self.get_id())
		else: UpdateIdRegistry.set(self.get_id(), update_id)
	#

	def _supports_search_content(self):
	#
		"""
Returns false if the resource content can't be searched for.

:return: (bool) True if resource content is searchable.
:since:  v0.1.00
		"""

		return (True if (self.id == "0" and self.get_searchable() and len(self.get_search_capabilities()) > 0) else False)
	#

	@staticmethod
	def _append_content_didl_xml_nodes(xml_resource, xml_base_path, content, parent_id = None):
	#
		"""
Uses the given XML resource to add DIDL nodes for the content of the UPnP
resource.

:param xml_resource: XML resource
:param xml_base_path: UPnP resource XML base path (e.g. "DIDL-Lite
                      container")

:return: (int) Number of DIDL nodes added
:since:  v0.1.01
		"""

		# pylint: disable=protected-access

		content_containers = 0
		content_items = 0
		content_resources = 0

		for resource in content:
		#
			resource_type = resource.get_type()

			if (resource_type == None): xml_node_path = None
			elif (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
			#
				xml_node_path = "{0} container#{1:d}".format(xml_base_path, content_containers)
				content_containers += 1
			#
			elif (resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM):
			#
				xml_node_path = "{0} item#{1:d}".format(xml_base_path, content_items)
				content_items += 1
			#
			elif (resource_type & Resource.TYPE_CDS_RESOURCE == Resource.TYPE_CDS_RESOURCE):
			#
				xml_node_path = "{0} res#{1:d}".format(xml_base_path, content_resources)
				content_resources += 1
			#
			else: xml_node_path = None

			if (xml_node_path != None):
			#
				resource._add_metadata_to_didl_xml_node(xml_resource, xml_node_path, parent_id)
				resource._rewrite_metadata_of_didl_xml_node(xml_resource, xml_node_path)
				resource._filter_metadata_of_didl_xml_node(xml_resource, xml_node_path)
			#
		#

		return content_containers + content_items + content_resources
	#

	@staticmethod
	def _get_didl_xmlns_attributes():
	#
		"""
Returns a dictionary with all DIDL-Lite XML NS attributes.

:return: (dict) DIDL-Lite XML NS attributes
:since:  v0.1.03
		"""

		return { "xmlns": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/",
		         "xmlns:dc": "http://purl.org/dc/elements/1.1/",
		         "xmlns:upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/",
		         "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
		         "xsi:schemaLocation": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/ http://www.upnp.org/schemas/av/didl-lite.xsd urn:schemas-upnp-org:metadata-1-0/upnp/ http://www.upnp.org/schemas/av/upnp.xsd"
		       }
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

		if (_id == "0" and cds != None):
		#
			_return = Resource()
			_return.init_cds_id(_id, client_user_agent, deleted)
		#
		elif (_id != None and "://" in _id):
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