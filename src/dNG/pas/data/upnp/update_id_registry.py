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

class UpdateIdRegistry(object):
#
	"""
"UpdateIdRegistry" takes a UPnP error message and its error code for later
output.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def get(_id):
	#
		"""
Returns the UPnP error code.

:return: (int) UPnP error code
:since:  v0.1.01
		"""

		return 1
	#

	@staticmethod
	def set(_id, value):
	#
		"""
Returns the UPnP error code.

:return: (int) UPnP error code
:since:  v0.1.01
		"""

		pass
	#

	@staticmethod
	def register(callback):
	#
		"""
Returns the UPnP error code.

:return: (int) UPnP error code
:since:  v0.1.01
		"""

		pass
	#

	@staticmethod
	def unregister(callback):
	#
		"""
Returns the UPnP error code.

:return: (int) UPnP error code
:since:  v0.1.01
		"""

		pass
	#
#

##j## EOF