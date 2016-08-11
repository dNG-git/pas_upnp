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

from dNG.plugins.hook import Hook
from dNG.runtime.thread_lock import ThreadLock

class UpdateIdRegistry(object):
#
	"""
"UpdateIdRegistry" takes a UPnP error message and its error code for later
output.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	UPDATE_ID_MAX = 4294967295
	"""
Largest UpdateID number supported by UPnP v1.0
	"""

	_ids = { }
	"""
	"""
	_lock = ThreadLock()
	"""
	"""

	@staticmethod
	def get(_id):
	#
		"""
Returns the UPnP UpdateID for the ID given.

:param _id: Registry ID

:return: (int) UPnP UpdateID value
:since:  v0.2.00
		"""

		return UpdateIdRegistry._ids.get(_id, 1)
	#

	@staticmethod
	def set(_id, value, resource = None):
	#
		"""
Sets the UPnP UpdateID for the ID given.

:param _id: Registry ID
:param value: UPnP UpdateID value
:param resource: UPnP resource of the UpdateID if applicable

:since: v0.2.00
		"""

		if (value == "++"):
		#
			with UpdateIdRegistry._lock:
			#
				value = UpdateIdRegistry.get(_id) + 1
				if (value > UpdateIdRegistry.UPDATE_ID_MAX): value = 1

				UpdateIdRegistry._ids[_id] = value
			#
		#
		else:
		#
			if (value < 1): value = UpdateIdRegistry.UPDATE_ID_MAX
			elif (value > UpdateIdRegistry.UPDATE_ID_MAX): value = 1

			UpdateIdRegistry._ids[_id] = value
		#

		if (resource is not None): Hook.call("dNG.pas.upnp.Resource.onUpdateIdChanged", id = _id, resource = resource, value = value)
	#

	@staticmethod
	def unset(_id, resource = None):
	#
		"""
Unsets the UPnP UpdateID for the ID given.

:param _id: Registry ID
:param resource: UPnP resource of the UpdateID if applicable

:since: v0.2.00
		"""

		with UpdateIdRegistry._lock:
		#
			if (_id in UpdateIdRegistry._ids): del(UpdateIdRegistry._ids[_id])
		#

		if (resource is not None): Hook.call("dNG.pas.upnp.Resource.onUpdateIdChanged", id = _id, resource = resource, value = None)
	#
#

##j## EOF