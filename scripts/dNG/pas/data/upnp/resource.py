# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.Resource
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;upnp

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
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from collections import OrderedDict

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.data.xml_writer import XmlWriter
from dNG.pas.data.binary import Binary
from dNG.pas.data.text.l10n import L10n
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks

class Resource(object):
#
	"""
"Resource" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

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

		self.audio_channels = None
		"""
UPnP resource audio channels
		"""
		self.audio_sample_bits = None
		"""
UPnP resource audio bits per sample
		"""
		self.audio_sample_frequency = None
		"""
UPnP resource audio sample frequency
		"""
		self.bitrate = None
		"""
UPnP resource bitrate in byte/s
		"""
		self.client_user_agent = None
		"""
Client user agent
		"""
		self.color_depth = None
		"""
UPnP resource color depth
		"""
		self.content = None
		"""
UPnP resource content
		"""
		self.content_offset = 0
		"""
UPnP resource content
		"""
		self.content_limit = None
		"""
UPnP resource content
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
		self.length = None
		"""
UPnP resource length in seconds
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
		self.source = None
		"""
UPnP resource source or creator
		"""
		self.symlink_target_id = None
		"""
UPnP resource symlinked ID
		"""
		self.type = None
		"""
UPnP resource type
		"""
		self.type_name = None
		"""
UPnP resource type name
		"""
		self.update_id = 1
		"""
UPnP UpdateID value
		"""
		self.updatable = False
		"""
True if the resource is writable
		"""
	#

	def client_get_user_agent(self):
	#
		"""
Returns the UPnP client user agent requesting the resource.

:return: (str) Client user agent if known; None otherwise
:since:  v0.1.00
		"""

		return self.client_user_agent
	#

	def client_set_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.1.00
		"""

		self.client_user_agent = user_agent
	#

	def content_add(self, resource):
	#
		"""
Add the given resource to the content list.

:param resource: UPnP resource

:since:  v0.1.01
		"""

		if (self.content == None): self.content_init()

		if (resource.get_type() != None):
		#
			self.content.append(resource)
			self.set_update_id("++")
		#
	#

	def content_append_didl_xml_nodes(self, xml_writer, xml_base_path):
	#
		"""
Returns an embedded device.

:since: v0.1.01
		"""

		if (self.content == None): self.content_init()

		content_containers = 0
		content_items = 0
		content_resources = 0

		for resource in self.content:
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

			if (xml_node_path != None): self.metadata_add_didl_xml_node(xml_writer, xml_node_path, resource)
		#

		return content_containers + content_items + content_resources
	#

	def content_get(self, position):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		if (self.content == None): self.content_init()

		if (self.content != None and position >= 0 and len(self.content) > position): return self.content[position]
		else: return None
	#

	def content_get_didl_xml(self):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		var_return = None

		if (self.type != None and self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			xml_writer = self.init_xml_parser()
			xml_writer.node_add("DIDL-Lite", attributes = { "xmlns": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/", "xmlns:dc": "http://purl.org/dc/elements/1.1/", "xmlns:upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/" })

			content_count = self.content_append_didl_xml_nodes(xml_writer, "DIDL-Lite")

			var_return = {
				"result": xml_writer.cache_export(True),
				"number_returned": content_count,
				"total_matches": self.get_total(),
				"update_id": self.update_id
			}
		#

		return var_return
	#

	def content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.01
		"""

		self.content = [ ]

		if (self.id == "0"):
		#
			Hooks.call("dNG.pas.upnp.resource.get_root_containers", container = self)
			if (self.content_limit != None): self.content = self.content[self.content_offset:self.content_offset + self.content_limit]

			return True
		#
		else: return False
	#

	def content_set_offset(self, content_offset):
	#
		"""
Sets the UPnP resource content offset.

:param content_offset: UPnP resource content offset

:since: v0.1.01
		"""

		self.content_offset = content_offset
	#

	def content_set_limit(self, content_limit):
	#
		"""
Sets the UPnP resource content offset.

:param content_offset: UPnP resource content limit

:since: v0.1.01
		"""

		self.content_limit = content_limit
	#

	def get_didl_fields(self):
	#
		"""
Returns the DIDL fields requested.

:return: (list) DIDL fields list; None if not filtered
:since:  v0.1.01
		"""

		return self.didl_fields
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

	def get_id(self):
	#
		"""
Returns the UPnP resource ID.

:return: (str) UPnP resource ID
:since:  v0.1.01
		"""

		return self.id
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
Returns if the UPnP resource can be changed.

:return: (bool) True if the content can be changed.
:since:  v0.1.01
		"""

		return self.searchable
	#

	def get_total(self):
	#
		"""
Returns the content resources total.

:return: (int) Content resources total
:since:  v0.1.01
		"""

		if (self.content == None): self.content_init()
		return len(self.content)
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
:since:  v0.1.01
		"""

		var_return = None

		if (self.type != None):
		#
			if (self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): var_return = "object.container"
			elif (self.type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): var_return = "object.item"
		#

		return var_return
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

	def init(self, data):
	#
		"""
Add the given device to the list of embedded devices.

:param device: UPnP device

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		var_return = False

		if ("id" in data and "name" in data and "type" in data):
		#
			if (data['id'] == "0"): raise ValueError("Special UPnP resource ID '0' is not supported", 1)
			self.id = data['id']
			self.name = data['name']
			self.type = data['type']

			if ("parent_id" in data): self.parent_id = data['parent_id']
			if ("searchable" in data): self.searchable = data['searchable']
			if ("source" in data): self.parent_id = data['source']
			if ("symlink_target_id" in data): self.parent_id = data['symlink_target_id']
			if ("type_name" in data): self.type_name = data['type_name']
			if ("update_id" in data): self.update_id = data['update_id']
			if ("updatable" in data): self.parent_id = data['updatable']

			var_return = True
		#

		return var_return
	#

	def init_cds_id(self, var_id, client_user_agent = None, update_id = None):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param var_id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.01
		"""

		var_return = False

		self.id = var_id
		if (client_user_agent != None): self.client_user_agent = client_user_agent
		if (update_id != None): self.update_id = update_id

		if (var_id == "0"):
		#
			self.name = L10n.get("pas_upnp_container_root")
			self.parent_id = "-1"
			self.type = Resource.TYPE_CDS_CONTAINER

			var_return = True
		#

		return var_return
	#

	def init_xml_parser(self):
	#
		"""
Returns a XML parser with predefined XML namespaces.

:access: protected
:return: (object) XML parser
:since:  v0.1.01
		"""

		"""
There are known broken clients defining XML namespaces without the trailing
slash. We define both notations just in case.
		"""

		var_return = XmlWriter(node_type = OrderedDict)
		var_return.ns_register("dc", "http://purl.org/dc/elements/1.1")
		var_return.ns_register("dc", "http://purl.org/dc/elements/1.1/")
		var_return.ns_register("didl", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite")
		var_return.ns_register("didl", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/")
		var_return.ns_register("upnp", "urn:schemas-upnp-org:metadata-1-0/upnp")
		var_return.ns_register("upnp", "urn:schemas-upnp-org:metadata-1-0/upnp/")
		return var_return
	#

	def metadata_add_didl_xml_node(self, xml_writer, xml_node_path, resource):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		attributes = None
		resource_type = resource.get_type()
		resource_updatable = resource.get_updatable()
		value = ""

		if (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER):
		#
			attributes = {
				"id": resource.get_id(),
				"parentID": self.id,
				"restricted": ("0" if (resource_updatable) else "1")
			}

			if (self.didl_fields == None or "childCount" in self.didl_fields): attributes['childCount'] = str(resource.get_total())
			#	"searchable": ("0" if (resource.get_searchable()) else "1")
		#
		elif (resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM):
		#
			attributes = {
				"id": resource.get_id(),
				"parentID": self.id,
				"restricted": ("0" if (resource_updatable) else "1")
			}
		#
		elif (resource_type & Resource.TYPE_CDS_RESOURCE == Resource.TYPE_CDS_RESOURCE):
		#
			res_protocol = resource.get_didl_res_protocol()

			if (res_protocol != None):
			#
				attributes = {
					"protocolInfo": res_protocol
				}

				if (self.size != None): attributes['size'] = self.size

				url = Binary.str(resource.content_get(0))
				if (type(url) == str): value = url
			#
		#

		if (attributes != None):
		#
			xml_writer.node_add(xml_node_path, value, attributes)

			if (resource_type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER or resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM):
			#
				xml_writer.node_add("{0} dc:title".format(xml_node_path), resource.get_name())
				xml_writer.node_add("{0} upnp:class".format(xml_node_path), resource.get_type_class())
				if (self.didl_fields == None or "upnp:writeStatus" in self.didl_fields): xml_writer.node_add("{0} upnp:writeStatus".format(xml_node_path), ("WRITABLE" if (resource_updatable) else "NOT_WRITABLE"))

				if (resource_type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): resource.content_append_didl_xml_nodes(xml_writer, xml_node_path)
			#
		#
	#

	def metadata_get_didl_xml(self):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.01
		"""

		var_return = None

		if (self.type != None):
		#
			xml_writer = self.init_xml_parser()
			xml_writer.node_add("DIDL-Lite", attributes = { "xmlns": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/", "xmlns:dc": "http://purl.org/dc/elements/1.1/", "xmlns:upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/" })

			if (self.type & Resource.TYPE_CDS_CONTAINER == Resource.TYPE_CDS_CONTAINER): xml_node_path = "DIDL-Lite container"
			elif (self.type & Resource.TYPE_CDS_ITEM == Resource.TYPE_CDS_ITEM): xml_node_path = "DIDL-Lite item"
			else: xml_node_path = None

			if (xml_node_path != None): self.metadata_add_didl_xml_node(xml_writer, xml_node_path, self)

			var_return = {
				"result": xml_writer.cache_export(True),
				"number_returned": 1,
				"total_matches": 1,
				"update_id": self.update_id
			}
		#

		return var_return
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

	def set_update_id(self, update_id):
	#
		"""
Sets the UPnP resource update ID or increments it.

:param update_id: UPnP resource update ID or "++" to increment id

:since: v0.1.01
		"""

		if (update_id == "++"): self.update_id += 1
		elif (type(update_id) == int): self.update_id = update_id

		#Gena.update_value("")
	#

	@staticmethod
	def load_cds_id(var_id, client_user_agent = None, cds = None):
	#
		"""
Load a UPnP resource by CDS ID.

:param var_id: UPnP CDS ID
:param client_user_agent: Client user agent
:param cds: UPnP CDS

:return: (object) Resource object; None on error
:since:  v0.1.01
		"""

		var_return = None

		if (var_id == "0" and cds != None):
		#
			var_return = Resource()
			var_return.init_cds_id(var_id, client_user_agent, cds.get_system_update_id())
		#
		elif ("://" in var_id):
		#
			url_elements = urlsplit(var_id)

			if (url_elements.scheme != ""):
			#
				resource = NamedLoader.get_instance("dNG.pas.data.upnp.resources.{0}".format("".join([word.capitalize() for word in url_elements.scheme.split("-")])), False)
				if (isinstance(resource, Resource) and resource.init_cds_id(var_id)): var_return = resource
			#
		#

		return var_return
	#
#

##j## EOF