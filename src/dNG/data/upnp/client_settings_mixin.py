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

from .client_settings import ClientSettings

class ClientSettingsMixin(object):
#
	"""
"ClientSettingsMixin" implements methods to access UPnP client based
settings.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(ClientSettingsMixin)

:since: v0.2.00
		"""

		self.client_host = None
		"""
Client host
		"""
		self.client_settings = None
		"""
Cached client settings
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
:since:  v0.2.00
		"""

		if (self.client_settings is None):
		#
			self.client_settings = ClientSettings(self.client_user_agent, self.client_host)
		#

		return self.client_settings
	#

	def get_client_host(self):
	#
		"""
Returns the UPnP client host requesting the resource.

:return: (str) Client host if known; None otherwise
:since:  v0.2.00
		"""

		return self.client_host
	#

	def get_client_user_agent(self):
	#
		"""
Returns the UPnP client user agent requesting the resource.

:return: (str) Client user agent if known; None otherwise
:since:  v0.2.00
		"""

		return self.client_user_agent
	#

	def init_client_settings(self, user_agent, host):
	#
		"""
Initializes the UPnP client settings.

:param user_agent: Client user agent
:param host: Client host

:since: v0.2.00
		"""

		self.client_host = host
		self.client_settings = None
		self.client_user_agent = user_agent
	#

	def set_client_host(self, host):
	#
		"""
Sets the UPnP client host.

:param host: Client host

:since: v0.2.00
		"""

		self.client_host = host
		if (self.client_settings is not None): self.client_settings.set_host(host)
	#

	def set_client_settings(self, client_settings):
	#
		"""
Sets the UPnP client settings instance.

:param client_settings: Client settings instance

:since: v0.2.00
		"""

		self.client_settings = client_settings
	#

	def set_client_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.2.00
		"""

		self.client_settings = None
		self.client_user_agent = user_agent
	#
#

##j## EOF