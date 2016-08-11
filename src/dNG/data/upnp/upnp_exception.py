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

from dNG.data.http.translatable_error import TranslatableError

class UpnpException(TranslatableError):
#
	"""
"UpnpException" takes a UPnP error message and its error code for later
output.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, l10n_id, upnp_code = 501, value = None, _exception = None):
	#
		"""
Constructor __init__(UpnpException)

:param l10n_id: L10n translatable key (prefixed with "errors_")
:param upnp_code: UPnP error code
:param value: Exception message value
:param _exception: Inner exception

:since: v0.2.00
		"""

		TranslatableError.__init__(self, l10n_id, 500, value, _exception)

		self.upnp_code = upnp_code
		"""
UPnP error code
		"""
	#

	def get_upnp_code(self):
	#
		"""
Returns the UPnP error code.

:return: (int) UPnP error code
:since:  v0.2.00
		"""

		return self.upnp_code
	#
#

##j## EOF