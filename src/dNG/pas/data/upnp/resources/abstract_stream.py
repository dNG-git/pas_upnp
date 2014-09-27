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

from dNG.pas.data.binary import Binary
from dNG.pas.data.upnp.resource import Resource

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

			if (res_protocol != None): attributes['protocolInfo'] = res_protocol
			if (size != None): attributes['size'] = size

			didl_fields_filtered = (len(didl_fields) > 0)

			for key in self.metadata:
			#
				if ((not didl_fields_filtered) or "res@{0}".format(key) in didl_fields): attributes[key] = self.metadata[key]
			#

			url = Binary.str(self.get_content(0))
			value = (url if (type(url) == str) else "")

			xml_resource.add_node(xml_node_path, value, attributes)
		#
	#

	def set_metadata(self, **kwargs):
	#
		"""
Sets metadata used for "_add_metadata_to_didl_xml_node()".

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_metadata({1})- (#echo(__LINE__)#)", self, kwargs, context = "pas_upnp")
		self.metadata.update(kwargs)
	#

	def set_mimeclass(self, mimeclass):
	#
		"""
Sets the UPnP resource mime class.

:param mimeclass: UPnP resource mime class

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimeclass({1})- (#echo(__LINE__)#)", self, mimeclass, context = "pas_upnp")
		self.mimeclass = mimeclass
	#

	def set_mimetype(self, mimetype):
	#
		"""
Sets the UPnP resource mime type.

:param mimetype: UPnP resource mime type

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mimetype({1})- (#echo(__LINE__)#)", self, mimetype, context = "pas_upnp")
		self.mimetype = mimetype
	#

	def set_size(self, size):
	#
		"""
Sets the UPnP resource size.

:param size: (int) UPnP resource size

:since: v0.1.03
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_size({1:d})- (#echo(__LINE__)#)", self, size, context = "pas_upnp")
		self.size = size
	#
#

##j## EOF