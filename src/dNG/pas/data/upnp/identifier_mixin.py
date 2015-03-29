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

import re

from dNG.pas.data.binary import Binary

class IdentifierMixin(object):
#
	"""
"IdentifierMixin" implements methods to get UPnP identifier values.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	RE_USN_URN = re.compile("^urn:(.+):(.+):(.*):(.*)$", re.I)
	"""
URN RegExp
	"""

	def __init__(self):
	#
		"""
Constructor __init__(IdentifierMixin)

:since: v0.1.03
		"""

		self.identifier = None
		"""
Parsed UPnP identifier
		"""
	#

	def _get_identifier(self):
	#
		"""
Returns the UPnP USN string.

:return: (dict) Parsed UPnP identifier; None if not set
:since:  v0.1.03
		"""

		return self.identifier
	#

	def get_type(self):
	#
		"""
Returns the UPnP service type.

:return: (str) Service type
:since:  v0.1.03
		"""

		return self.identifier['type']
	#

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP service UDN
:since:  v0.1.03
		"""

		return self.identifier['uuid']
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP service specification domain.

:return: (str) UPnP service specification domain
:since:  v0.1.03
		"""

		return self.identifier['domain']
	#

	def get_urn(self):
	#
		"""
Returns the UPnP serviceType value.

:return: (str) UPnP URN
:since:  v0.1.03
		"""

		return self.identifier['urn']
	#

	def get_usn(self):
	#
		"""
Returns the UPnP USN value.

:return: (str) UPnP USN
:since:  v0.1.03
		"""

		return "uuid:{0}::urn:{1}".format(self.get_udn(), self.get_urn())
	#

	def get_version(self):
	#
		"""
Returns the UPnP device type version.

:return: (str) Device type version; None if undefined
:since:  v0.1.03
		"""

		return self.identifier.get("version")
	#

	def _set_identifier(self, identifier):
	#
		"""
Sets the UPnP USN identifier.

:param identifier: Parsed UPnP identifier

:since: v0.1.03
		"""

		self.identifier = identifier
	#

	@staticmethod
	def get_identifier(usn, bootid = None, configid = None):
	#
		"""
Parses the given UPnP USN string.

:param usn: UPnP USN
:param bootid: UPnP bootId (bootid.upnp.org) if any
:param configid: UPnP configId (configid.upnp.org) if any

:return: (dict) Parsed UPnP identifier; None on error
:since:  v0.1.03
		"""

		usn = Binary.str(usn)

		if (type(usn) == str):
		#
			usn_data = usn.split("::", 1)
			device_id = usn_data[0].lower().replace("-", "")
		#
		else: device_id = ""

		if (device_id.startswith("uuid:")):
		#
			device_id = device_id[5:]

			_return = { "device": device_id,
			            "bootid": None,
			            "configid": None,
			            "uuid": usn_data[0][5:],
			            "class": "unknown",
			            "usn": usn
			          }

			if (bootid is not None and configid is not None):
			#
				_return['bootid'] = bootid
				_return['configid'] = configid
			#

			re_result = (IdentifierMixin.RE_USN_URN.match(usn_data[1]) if (len(usn_data) > 1) else None)

			if (re_result is not None):
			#
				_return['urn'] = usn_data[1][4:]

				_return['domain'] = re_result.group(1)
				_return['class'] = re_result.group(2)
				_return['type'] = re_result.group(3)
				_return['version'] = re_result.group(4)
			#
			elif (usn[-17:].lower() == "::upnp:rootdevice"): _return['class'] = "rootdevice"
		#
		else: _return = None

		return _return
	#
#

##j## EOF