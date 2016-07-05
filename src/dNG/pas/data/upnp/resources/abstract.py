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

from dNG.data.rfc.basics import Basics
from dNG.data.xml_resource import XmlResource
from dNG.pas.data.binary import Binary
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.data.upnp.update_id_registry import UpdateIdRegistry
from dNG.pas.data.upnp.variable import Variable
from dNG.pas.data.upnp.xml_rewrite_parser import XmlRewriteParser
from dNG.pas.data.upnp.search.criteria_parser import CriteriaParser
from dNG.pas.data.upnp.search.resources import Resources as SearchResources
from dNG.pas.plugins.hook import Hook

class Abstract(Resource):
#
	"""
"Abstract" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	def __init__(self):
	#
		"""
Constructor __init__(Abstract)

:since: v0.2.00
		"""

		Resource.__init__(self)

		self.virtual_resource = False
		"""
True if the resource is a virtual one
		"""

		self.supported_features['search_content'] = self._supports_search_content
		self.supported_features['vfs_url'] = self._supports_vfs_url
	#

	def add_content(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.2.00
		"""

		_return = Resource.add_content(self, resource)

		if (_return
		    and (not self.virtual_resource)
		    and resource.get_type() & Abstract.TYPE_CDS_RESOURCE != Abstract.TYPE_CDS_RESOURCE
		   ): self.set_update_id("++")

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

		is_resource_container = (resource_type & Abstract.TYPE_CDS_CONTAINER == Abstract.TYPE_CDS_CONTAINER)
		is_resource_item = (resource_type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM)
		is_resource_updatable = self.get_updatable()

		if (parent_id is None): parent_id = self.get_parent_resource_id()

		if (is_resource_container):
		#
			attributes = { "id": self.get_resource_id(),
			               "restricted": (Variable.BOOL_FALSE if (is_resource_updatable) else Variable.BOOL_TRUE),
			               "searchable": (Variable.BOOL_TRUE if (self.get_searchable()) else Variable.BOOL_FALSE)
			             }

			if (parent_id is not None): attributes['parentID'] = parent_id

			didl_fields = self.get_didl_fields()
			if (len(didl_fields) < 1 or "@childCount" in didl_fields): attributes['childCount'] = self.get_total()
		#
		elif (is_resource_item):
		#
			attributes = { "id": self.get_resource_id(),
			               "restricted": (Variable.BOOL_FALSE if (is_resource_updatable) else Variable.BOOL_TRUE)
			             }

			if (parent_id is not None): attributes['parentID'] = parent_id
		#
		elif (resource_type & Abstract.TYPE_CDS_RESOURCE == Abstract.TYPE_CDS_RESOURCE):
		#
			res_protocol = self.get_didl_res_protocol()
			size = self.get_size()

			if (res_protocol is not None):
			#
				attributes = { "protocolInfo": res_protocol }
				if (size is not None): attributes['size'] = size

				url = Binary.str(self.get_content(0))
				if (type(url) is str): value = url
			#
		#

		if (attributes is not None):
		#
			xml_resource.add_node(xml_node_path, value, attributes)

			if (is_resource_container or is_resource_item):
			#
				type_name = self.get_type_name()
				type_attributes = (None if (type_name is None) else { "name": type_name })

				xml_resource.add_node("{0} dc:title".format(xml_node_path), self.get_name())
				xml_resource.add_node("{0} upnp:class".format(xml_node_path), self.get_type_class(), type_attributes)

				update_id_node_path = ("{0} upnp:containerUpdateID"
				                       if (is_resource_container) else
				                       "{0} upnp:objectUpdateID"
				                      )

				xml_resource.add_node(update_id_node_path.format(xml_node_path), self.get_update_id())

				timestamp = self.get_timestamp()

				if (timestamp > -1):
				#
					xml_resource.add_node("{0} dc:date".format(xml_node_path), Basics.get_iso8601_datetime(timestamp))
				#

				xml_resource.add_node("{0} upnp:writeStatus".format(xml_node_path),
				                      ("WRITABLE" if (is_resource_updatable) else "NOT_WRITABLE")
				                     )

				if (is_resource_item):
				#
					Abstract._append_content_didl_xml_nodes(xml_resource,
					                                        xml_node_path,
					                                        self.get_content_list(),
					                                        self.get_resource_id()
					                                       )
				#
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
		    and (resource_type & Abstract.TYPE_CDS_CONTAINER == Abstract.TYPE_CDS_CONTAINER
		         or resource_type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM
		        )
		    and "upnp:writeStatus" not in didl_fields
		   ): xml_resource.remove_node("{0} upnp:writeStatus".format(xml_node_path))
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

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_content_didl_xml()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		xml_resource = self._init_xml_resource()
		xml_resource.add_node("DIDL-Lite", attributes = self.__class__._get_didl_xmlns_attributes())

		content_count = Abstract._append_content_didl_xml_nodes(xml_resource,
		                                                        "DIDL-Lite",
		                                                        self.get_content_list(),
		                                                        self.get_resource_id()
		                                                       )

		_return = { "result": xml_resource.export_cache(True),
		            "number_returned": content_count,
		            "total_matches": self.get_total(),
		            "update_id": UpdateIdRegistry.get("upnp://ContentDirectory-0/system_update_id")
		          }

		return _return
	#

	def _get_custom_didl_fields(self, didl_fields):
	#
		"""
Returns the user agent specific DIDL fields requested.

:return: (list) DIDL fields list; None if not filtered
:since:  v0.2.00
		"""

		_return = (None
		           if (self.client_user_agent is None) else
		           Hook.call("dNG.pas.upnp.Resource.getDidlFields",
		                     didl_fields = didl_fields,
		                     client_user_agent = self.client_user_agent
		                    )
		          )

		return (didl_fields if (_return is None) else _return)
	#

	def _get_custom_didl_res_protocol(self, didl_res_protocol):
	#
		"""
Returns a user agent specific DIDL protcolInfo value.

:return: (str) DIDL protocolInfo value; None if undefined
:since:  v0.2.00
		"""

		_return = (None
		           if (self.client_user_agent is None) else
		           Hook.call("dNG.pas.upnp.Resource.getDidlResProtocol",
		                     didl_res_protocol = didl_res_protocol,
		                     client_user_agent = self.client_user_agent
		                    )
		          )

		return (didl_res_protocol if (_return is None) else _return)
	#

	def _get_custom_mimetype(self, mimetype):
	#
		"""
Returns a user agent specific UPnP resource mime type.

:return: (str) UPnP resource mime type; None if not defined
:since:  v0.2.00
		"""

		_return = (None
		           if (self.client_user_agent is None) else
		           Hook.call("dNG.pas.upnp.Resource.getMimetype",
		                     mimetype = mimetype,
		                     client_user_agent = self.client_user_agent
		                    )
		          )

		if (_return is None): _return = mimetype

		client_settings = self.get_client_settings()
		client_mimetypes = client_settings.get("upnp_custom_mimetypes")
		if (isinstance(client_mimetypes, dict) and _return in client_mimetypes): _return = client_mimetypes[_return]

		return _return
	#

	def _get_custom_type(self, _type):
	#
		"""
Returns a user agent specific UPnP resource type.

:return: (str) UPnP resource type; None if not defined
:since:  v0.2.00
		"""

		_return = (None
		           if (self.client_user_agent is None) else
		           Hook.call("dNG.pas.upnp.Resource.getType",
		                     _type = _type,
		                     client_user_agent = self.client_user_agent
		                    )
		          )

		return (_type if (_return is None) else _return)
	#

	def _get_custom_type_class(self, type_class):
	#
		"""
Returns a user agent specific UPnP resource type class.

:return: (str) UPnP resource type class; None if not defined
:since:  v0.2.00
		"""

		_return = (None
		           if (self.client_user_agent is None) else
		           Hook.call("dNG.pas.upnp.Resource.getTypeClass",
		                     type_class = type_class,
		                     client_user_agent = self.client_user_agent
		                    )
		          )

		return (type_class if (_return is None) else _return)
	#

	def get_didl_fields(self):
	#
		"""
Returns the DIDL fields requested.

:return: (list) DIDL fields list
:since:  v0.2.00
		"""

		return self._get_custom_didl_fields(Resource.get_didl_fields(self))
	#

	def get_didl_res_protocol(self):
	#
		"""
Returns the DIDL protcolInfo value.

:return: (str) DIDL protocolInfo value; None if undefined
:since:  v0.2.00
		"""

		return self._get_custom_didl_res_protocol(Resource.get_didl_res_protocol(self))
	#

	def get_metadata_didl_xml(self):
	#
		"""
Returns an UPnP DIDL result of generated XML for this UPnP resource.

:return: (dict) Result dict containting the same keys as
         "get_content_didl_xml()"
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_metadata_didl_xml()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = None

		if (self.type is not None):
		#
			xml_resource = self._init_xml_resource()
			xml_resource.add_node("DIDL-Lite", attributes = self.__class__._get_didl_xmlns_attributes())

			if (self.type & Abstract.TYPE_CDS_CONTAINER == Abstract.TYPE_CDS_CONTAINER):
			#
				xml_node_path = "DIDL-Lite container"
			#
			elif (self.type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM):
			#
				xml_node_path = "DIDL-Lite item"
			#
			else: xml_node_path = None

			if (xml_node_path is not None):
			#
				self._add_metadata_to_didl_xml_node(xml_resource, xml_node_path)
				self._rewrite_metadata_of_didl_xml_node(xml_resource, xml_node_path)
				self._filter_metadata_of_didl_xml_node(xml_resource, xml_node_path)
			#

			_return = { "result": xml_resource.export_cache(True),
			            "number_returned": 1,
			            "total_matches": 1,
			            "update_id": UpdateIdRegistry.get("upnp://ContentDirectory-0/system_update_id")
			          }
		#

		return _return
	#

	def get_mimetype(self):
	#
		"""
Returns the UPnP resource mime type.

:return: (str) UPnP resource mime type
:since:  v0.2.00
		"""

		return self._get_custom_mimetype(Resource.get_mimetype(self))
	#

	def get_type(self):
	#
		"""
Returns the UPnP resource type.

:return: (str) UPnP resource type; None if empty
:since:  v0.2.00
		"""

		return self._get_custom_type(Resource.get_type(self))
	#

	def get_type_class(self):
	#
		"""
Returns the UPnP resource type class.

:return: (str) UPnP resource type class; None if unknown
:since:  v0.2.00
		"""

		return self._get_custom_type_class(Resource.get_type_class(self))
	#

	def get_vfs_url(self):
	#
		"""
Returns the VFS URL of this instance.

:return: (str) UPnP resource VFS URL; None if undefined
:since:  v0.2.00
		"""

		return (Resource.get_vfs_url(self) if (self._supports_vfs_url()) else None)
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		if (self.content is None):
		# Thread safety
			with self._lock:
			#
				Resource._init_content(self)
				_type = self.get_type()

				if (_type is not None and
				    _type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM
				   ):
				#
					Hook.call("dNG.pas.upnp.Resource.getItemResourceClientContent", item = self)
					if (len(self.content) == 0): Hook.call("dNG.pas.upnp.Resource.getItemResourceContent", item = self)

					_return = True
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

	def remove_content(self, resource):
	#
		"""
Removes the given resource from the content list.

:param resource: UPnP resource

:return: (bool) True on success
:since:  v0.2.00
		"""

		_return = Resource.remove_content(self, resource)

		if (_return
		    and (not self.virtual_resource)
		    and resource.get_type() & Abstract.TYPE_CDS_RESOURCE != Abstract.TYPE_CDS_RESOURCE
		   ): self.set_update_id("++")

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

		if (resource_type is not None):
		#
			client_settings = self.get_client_settings()

			title_format_resource_class_name = NamedLoader.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", self.__class__.__name__)
			title_format_resource_name = "upnp_didl_title_{0}_format".format(title_format_resource_class_name.lower())

			if (title_format_resource_name in client_settings): title_format = client_settings.get(title_format_resource_name)
			elif (resource_type & Abstract.TYPE_CDS_CONTAINER == Abstract.TYPE_CDS_CONTAINER):
			#
				title_format = client_settings.get("upnp_didl_title_default_container_format")
			#
			elif (resource_type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM):
			#
				title_format = client_settings.get("upnp_didl_title_default_item_format")
			#

			if (title_format is None): title_format = client_settings.get("upnp_didl_title_default_format")
		#

		if (title_format is not None):
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

:return: (object) UPnP content resources instance found
:since:  v0.1.01
		"""

		_return = None

		_type = self.get_type()

		if (_type is not None and _type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			search_criteria_parser = CriteriaParser()
			search_criteria_definition = search_criteria_parser.parse(search_criteria)

			_return = SearchResources()
			if (self.client_user_agent is not None): _return.set_client_user_agent(self.client_user_agent)
			_return.set_root_resource(self)

			_return.set_criteria_definition(search_criteria_definition)
			_return.set_sort_criteria(self.sort_criteria)

			_return.set_offset(self.content_offset)
			if (self.content_limit is not None): _return.set_limit(self.content_limit)
		#

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

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.search_content_didl_xml()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = None

		xml_resource = self._init_xml_resource()
		xml_resource.add_node("DIDL-Lite", attributes = self.__class__._get_didl_xmlns_attributes())

		content_count = 0
		content_matched_count = 0
		search_resources_task = self.search_content(search_criteria)

		if (search_resources_task is not None):
		#
			content_matched_count = search_resources_task.get_count()

			if (content_matched_count > 0):
			#
				content_matched = search_resources_task.get_list()

				content_count = Abstract._append_content_didl_xml_nodes(xml_resource,
				                                                        "DIDL-Lite",
				                                                        content_matched
				                                                       )
			#
		#

		_return = { "result": xml_resource.export_cache(True),
		            "number_returned": content_count,
		            "total_matches": content_matched_count,
		            "update_id": UpdateIdRegistry.get("upnp://ContentDirectory-0/system_update_id")
		          }
		#

		return _return
	#

	def _supports_search_content(self):
	#
		"""
Returns false if the resource content can't be searched for.

:return: (bool) True if resource content is searchable.
:since:  v0.2.00
		"""

		return (self.resource_id == "0" and self.get_searchable() and len(self.get_search_capabilities()) > 0)
	#

	def _supports_vfs_url(self):
	#
		"""
Returns false if the UPnP resource can not provide a supported VFS URL.

:return: (bool) True if UPnP resource can provide a supported VFS URL.
:since:  v0.2.00
		"""

		return (not self.virtual_resource)
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

			if (resource_type is None): xml_node_path = None
			elif (resource_type & Abstract.TYPE_CDS_CONTAINER == Abstract.TYPE_CDS_CONTAINER):
			#
				xml_node_path = "{0} container#{1:d}".format(xml_base_path, content_containers)
				content_containers += 1
			#
			elif (resource_type & Abstract.TYPE_CDS_ITEM == Abstract.TYPE_CDS_ITEM):
			#
				xml_node_path = "{0} item#{1:d}".format(xml_base_path, content_items)
				content_items += 1
			#
			elif (resource_type & Abstract.TYPE_CDS_RESOURCE == Abstract.TYPE_CDS_RESOURCE):
			#
				xml_node_path = "{0} res#{1:d}".format(xml_base_path, content_resources)
				content_resources += 1
			#
			else: xml_node_path = None

			if (xml_node_path is not None):
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
#

##j## EOF