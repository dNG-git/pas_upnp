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

class SpecMixin(object):
#
	"""
"SpecMixin" is used to provide the UPnP specVersion data.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(SpecMixin)

:since: v0.1.03
		"""

		self.spec_major = 2
		"""
UPnP specVersion major number
		"""
		self.spec_minor = 0
		"""
UPnP specVersion minor number
		"""
	#

	def get_spec_version(self):
	#
		"""
Returns the UPnP specVersion number.

:return: (tuple) UPnP Device Architecture version: Major and minor number
:since:  v0.1.03
		"""

		return ( self.spec_major, self.spec_minor )
	#

	def _set_spec_version(self, version):
	#
		"""
Sets the UPnP specVersion number.

:param version: (tuple) UPnP Device Architecture version

:since: v0.1.00
		"""

		if (type(version) == tuple and len(version) == 2):
		#
			self.spec_major = int(version[0])
			self.spec_minor = int(version[1])
		#
	#
#

##j## EOF