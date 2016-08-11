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

from dNG.data.text.link import Link

from .abstract_item_resource import AbstractItemResource

class AbstractItemHttpResource(AbstractItemResource):
#
	"""
"AbstractItemHttpResource" represents a HTTP streamable UPnP resource "res"
entry.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		self.content = [ ]

		if (self.type is not None):
		#
			link_parameters = { "__virtual__": "/upnp/stream/{0}".format(quote(self.get_resource_id(), "/")) }
			self.content.append(Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, link_parameters))

			_return = True
		#

		return _return
	#

	def set_mimetype(self, mimetype):
	#
		"""
Sets the UPnP resource mime type.

:param mimetype: UPnP resource mime type

:since: v0.2.00
		"""

		AbstractItemResource.set_mimetype(self, mimetype)
		if (self.didl_res_protocol is None): self.didl_res_protocol = "http-get:*:{0}:*".format(self.get_mimetype())
	#
#

##j## EOF