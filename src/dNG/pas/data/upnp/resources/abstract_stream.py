# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.AbstractStream
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
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

	def metadata_add_didl_xml_node(self, xml_resource, xml_node_path, parent_id = None):
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

			if (res_protocol != None):
			#
				attributes = { "protocolInfo": res_protocol }
				if (size != None): attributes['size'] = size

				didl_fields_filtered = (len(didl_fields) > 0)

				for key in self.metadata:
				#
					if ((not didl_fields_filtered) or "res@{0}".format(key) in didl_fields): attributes[key] = self.metadata[key]
				#

				url = Binary.str(self.content_get(0))
				value = (url if (type(url) == str) else "")

				xml_resource.node_add(xml_node_path, value, attributes)
			#
		#
	#

	def set_metadata(self, **kwargs):
	#
		"""
Set metadata used for "metadata_add_didl_xml_node()".

:since: v0.1.00
		"""

		self.metadata.update(kwargs)
	#
#

##j## EOF