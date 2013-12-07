# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.resources.HttpBlockStream
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
from dNG.pas.data.text.url import Url
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def _content_init(self):
	#
		"""
Initializes the content of a container.

:return: (bool) True if successful
:since:  v0.1.00
		"""

		_return = False

		self.content = [ ]

		if (self.type != None):
		#
			self.content.append(Url(path = "/upnp/stream/{0}".format(quote(Binary.str(b64encode(Binary.utf8_bytes(self.id)))))).build_url(Url.TYPE_FULL, { }))
			_return = True
		#

		return _return
	#

	def init_cds_id(self, _id, client_user_agent = None, update_id = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: Initial UPnP resource update ID
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		Resource.init_cds_id(self, _id, client_user_agent, update_id, deleted)
		_return = (self.id != None)

		if (_return):
		#
			url_elements = urlsplit(self.id)

			streamer = (None if (url_elements.scheme == "") else NamedLoader.get_instance("dNG.pas.data.streamer.{0}".format(url_elements.scheme.capitalize()), False))

			if (streamer.url_supported(self.id)):
			#
				self.name = path.basename(unquote(url_elements.path))
				self.type = HttpBlockStream.TYPE_CDS_RESOURCE

				if (self.mimetype == None):
				#
					path_ext = path.splitext(url_elements.path)[1]
					mimetype_definition = MimeType.get_instance().get(path_ext[1:])

					if (mimetype_definition != None):
					#
						self.mimeclass = mimetype_definition['class']
						self.mimetype = mimetype_definition['type']
					#
				#

				if (self.mimetype != None): self.didl_res_protocol = "http-get:*:{0}:*".format(self.get_mimetype())
			#
			else: _return = False
		#

		return _return
	#

	@staticmethod
	def handle_http_request(params = None, last_return = None):
	#
		"""
Handles a valid HTTP task request.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		_return = last_return

		if (_return == None):
		#
			_return = PredefinedHttpRequest()
			_return.set_module("output")
			_return.set_service("throttled")
			_return.set_action("stream")
			_return.set_dsd("url", params['url'])
		#

		return _return
	#
#

##j## EOF