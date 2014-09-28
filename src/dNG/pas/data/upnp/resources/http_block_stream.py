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

from base64 import b64encode
from os import path

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
#
	from urllib import quote, unquote
	from urlparse import urlsplit
#

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.binary import Binary
from dNG.pas.data.mime_type import MimeType
from dNG.pas.data.text.link import Link
from dNG.pas.data.upnp.resource import Resource
from dNG.pas.module.named_loader import NamedLoader
from .abstract_stream import AbstractStream

class HttpBlockStream(AbstractStream):
#
	"""
"Resource" represents an UPnP directory, file or virtual object.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		Resource.init_cds_id(self, _id, client_user_agent, deleted)
		_return = (self.id != None)

		if (_return):
		#
			url_elements = urlsplit(self.id)

			streamer_class = (None
			                  if (url_elements.scheme == "") else
			                  "".join([ word.capitalize() for word in url_elements.scheme.split("-") ])
			                 )

			streamer = (None
			            if (streamer_class == "") else
			            NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(streamer_class), False)
			           )

			if (streamer != None and streamer.is_url_supported(self.id)):
			#
				self.name = path.basename(unquote(url_elements.path))
				self.type = HttpBlockStream.TYPE_CDS_RESOURCE

				mimetype = None

				if (self.mimetype == None):
				#
					path_ext = path.splitext(url_elements.path)[1]
					mimetype_definition = MimeType.get_instance().get(path_ext[1:])

					if (mimetype_definition != None):
					#
						self.mimeclass = mimetype_definition['class']
						mimetype = mimetype_definition['type']
					#
				#

				if (mimetype != None): self.set_mimetype(mimetype)
			#
			else: _return = False
		#

		return _return
	#

	def _init_content(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init_content()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		self.content = [ ]

		if (self.type != None):
		#
			_id = self.get_parent_id()
			if (_id == None): _id = self.get_id()

			parameters = { "__virtual__": "/upnp/stream/{0}".format(quote(Binary.str(b64encode(Binary.utf8_bytes(_id))))) }
			self.content.append(Link.get_preferred("upnp").build_url(Link.TYPE_VIRTUAL_PATH, parameters))

			_return = True
		#

		return _return
	#

	def set_mimetype(self, mimetype):
	#
		"""
Sets the UPnP resource mime type.

:param mimetype: UPnP resource mime type

:since: v0.1.01
		"""

		AbstractStream.set_mimetype(self, mimetype)
		if (self.didl_res_protocol == None): self.didl_res_protocol = "http-get:*:{0}:*".format(self.get_mimetype())
	#
#

##j## EOF