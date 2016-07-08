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

from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.plugins.hook import Hook

from .abstract import Abstract

class RootContainer(Abstract):
#
	"""
"RootContainer" represents the UPnP root container object.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def init_cds_id(self, _id, client_user_agent = None, deleted = False):
	#
		"""
Initialize a UPnP resource by CDS ID.

:param _id: UPnP CDS ID
:param client_user_agent: Client user agent
:param update_id: UPnP UpdateID value
:param deleted: True to include deleted resources

:return: (bool) Returns true if initialization was successful.
:since:  v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.init_cds_id({1})- (#echo(__LINE__)#)", self, _id, context = "pas_upnp")
		_return = Abstract.init_cds_id(self, _id, client_user_agent, deleted)

		if (_id == "0"):
		#
			self.name = L10n.get("pas_upnp_container_root")
			self.type = RootContainer.TYPE_CDS_CONTAINER

			search_segments = Hook.call("dNG.pas.upnp.Resource.getSearchSegments", id = _id)
			self.searchable = (type(search_segments) is list and len(search_segments) > 0)
		#
		else: _return = True

		return _return
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
				_return = Abstract._init_content(self)

				if (not _return):
				#
					if (self.resource_id == "0"):
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

	def get_search_capabilities(self):
	#
		"""
Returns the UPnP search capabilities.

:return: (str) UPnP search capabilities
:since:  v0.2.00
		"""

		didl_fields = Hook.call("dNG.pas.upnp.Resource.getSearchableDidlFields", client_user_agent = self.client_user_agent)
		if (type(didl_fields) != list or len(didl_fields) < 1): didl_fields = None

		if (didl_fields is None): _return = ""
		else: _return = ",".join(InputFilter.filter_unique_list(didl_fields))

		return _return
	#

	def get_sort_capabilities(self):
	#
		"""
Returns the UPnP sort capabilities.

:return: (str) UPnP sort capabilities
:since:  v0.2.00
		"""

		didl_fields = Hook.call("dNG.pas.upnp.Resource.getSortableDidlFields", client_user_agent = self.client_user_agent)
		if (type(didl_fields) != list or len(didl_fields) < 1): didl_fields = None

		if (didl_fields is None): _return = ""
		else: _return = ",".join(InputFilter.filter_unique_list(didl_fields))

		return _return
	#
#

##j## EOF