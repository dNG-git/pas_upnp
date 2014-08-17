# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from dNG.pas.data.http.translatable_error import TranslatableError

class UpnpException(TranslatableError):
#
	"""
"UpnpException" takes a UPnP error message and its error code for later
output.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
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

:since: v0.1.01
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
:since:  v0.1.01
		"""

		return self.upnp_code
	#
#

##j## EOF