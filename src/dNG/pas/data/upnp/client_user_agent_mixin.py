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

from .client_settings import ClientSettings

class ClientUserAgentMixin(object):
#
	"""
"ClientUserAgentMixin" implements methods to access the user agent of the
UPnP client.

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
Constructor __init__(ClientUserAgentMixin)

:since: v0.1.03
		"""

		self.client_user_agent = None
		"""
Client user agent
		"""
	#

	def get_client_settings(self):
	#
		"""
Returns the UPnP client settings instance for the client user agent.

:return: (object) UPnP client settings
:since:  v0.1.03
		"""

		return (ClientSettings()
		        if (self.client_user_agent is None) else
		        ClientSettings.load_user_agent(self.client_user_agent)
		       )
	#

	def get_client_user_agent(self):
	#
		"""
Returns the UPnP client user agent requesting the resource.

:return: (str) Client user agent if known; None otherwise
:since:  v0.1.03
		"""

		return self.client_user_agent
	#

	def set_client_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.1.03
		"""

		self.client_user_agent = user_agent
	#
#

##j## EOF