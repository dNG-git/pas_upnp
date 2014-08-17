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

from os import path
import re

from dNG.pas.data.cached_json_file import CachedJsonFile
from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.plugins.hook import Hook

class Client(dict):
#
	"""
This class holds static methods to handle UPnP client settings.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __repr__(self):
	#
		"""
python.org: Called by the repr() built-in function and by string conversions
(reverse quotes) to compute the "official" string representation of an
object.

:return: (str) String representation
:since:  v0.1.00
		"""

		return object.__repr__(self)
	#

	def _load_user_agent_file(self, user_agent):
	#
		"""
Updates the client with the data loaded from the settings file for the given
user agent.

:param user_agent: HTTP or SSDP user agent value

:since: v0.1.00
		"""

		identifier = Client.get_user_agent_identifiers(user_agent)

		settings = Client.get_settings_file("{0}/upnp/user_agents/{1}.json".format(Settings.get("path_data"), identifier))

		if (type(settings) == dict): self.update(settings)
		else: LogLine.debug("#echo(__FILEPATH__)# -{0!r}._load_user_agent_file()- reporting: No client file for user agent '{1}' with identifier '{2}'", self, user_agent, identifier, context = "pas_upnp")
	#

	@staticmethod
	def get_settings_file(file_pathname):
	#
		"""
Returns the client settings from the given file or a client file specified
in it.

:param file_pathname: Settings file path

:return: (dict) UPnP client settings; None on error
:since:  v0.1.00
		"""

		_return = CachedJsonFile.read(path.normpath(file_pathname))

		if (type(_return) == dict and "client_file" in _return):
		#
			_return = CachedJsonFile.read(path.join(Settings.get("path_data"), "upnp", "user_agents", InputFilter.filter_file_path(_return['client_file'])))
		#

		return _return
	#

	@staticmethod
	def get_user_agent_identifiers(user_agent):
	#
		"""
Returns a UPnP client based on the given HTTP or SSDP user agent value.

:param user_agent: HTTP or SSDP user agent value

:return: (Client) UPnP client; None on error
:since:  v0.1.00
		"""

		_return = ""

		if (not Settings.is_defined("pas_upnp_client_replacement_list")): Settings.read_file("{0}/settings/pas_upnp.json".format(Settings.get("path_data")))
		replacement_list = Settings.get("pas_upnp_client_replacement_list", None)

		if (type(replacement_list) == dict):
		#
			replacement_list_keys = sorted(replacement_list.keys(), reverse=True)
			for upnp_value in replacement_list_keys: user_agent = user_agent.replace(upnp_value, replacement_list[upnp_value])
		#

		for re_result in re.finditer("([\\d\\w\\.]+/([0-9\\.]+(\\W|$))+)", user_agent):
		#
			if (_return != ""): _return += "_"
			_return += re.sub("\\W+", "_", re_result.group(1)).strip("_")
		#

		if (_return == ""): _return = re.sub("\\W+", "_", user_agent).lower()
		else: _return = _return.lower()

		return _return
	#

	@staticmethod
	def load_user_agent(user_agent):
	#
		"""
Returns a UPnP client based on the given HTTP or SSDP user agent value.

:param user_agent: HTTP or SSDP user agent value

:return: (Client) UPnP client; Empty one if unknown
:since:  v0.1.00
		"""

		# pylint: disable=protected-access

		_return = Client()

		if (type(user_agent) == str):
		#
			external_client = Hook.call("dNG.pas.upnp.Client.getUserAgent", user_agent = user_agent)

			if (external_client == None): _return._load_user_agent_file(user_agent)
			else: _return = external_client
		#

		return _return
	#
#

##j## EOF