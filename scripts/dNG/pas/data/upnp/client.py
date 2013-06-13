# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.Client
"""
"""n// NOTE
----------------------------------------------------------------------------
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
----------------------------------------------------------------------------
NOTE_END //n"""

from os import path
import re

from dNG.data.file import File
from dNG.data.json_parser import JsonParser
from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks

class Client(dict):
#
	"""
The UPnP client identified.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def get_json_file(file_pathname):
	#
		"""
Return the json content from the given file.

:param file_pathname: Settings file path

:access: protected
:return: (mixed) JSON content; None on error
:since:  v0.1.00
		"""

		var_return = None

		cache_instance = NamedLoader.get_singleton("dNG.pas.data.Cache", False)

		try:
		#
			json = (None if (cache_instance == None) else cache_instance.get_file(file_pathname))

			if (json == None):
			#
				file_object = File()

				if (file_object.open(file_pathname, True, "r")):
				#
					json = file_object.read()
					file_object.close()

					json = json.replace("\r", "")
					if (cache_instance != None): cache_instance.set_file(file_pathname, json)
				#
			#

			if (json != None):
			#
				json_parser = JsonParser()
				var_return = json_parser.json2data(json)
			#
		#
		except Exception as handled_exception: LogLine.error(handled_exception)

		if (cache_instance != None): cache_instance.return_instance()
		return var_return
	#

	@staticmethod
	def get_settings_file(file_pathname):
	#
		"""
Return the client settings from the given file or a client file specified in
it.

:param file_pathname: Settings file path

:return: (dict) UPnP client settings; None on error
:since:  v0.1.00
		"""

		var_return = Client.get_json_file(path.normpath(file_pathname))
		if (type(var_return) == dict and "client_file" in var_return): var_return = Client.get_json_file(path.normpath("{0}/upnp/{1}".format(Settings.get("path_data"), InputFilter.filter_file_path(var_return['client_file']))))
		return var_return
	#

	@staticmethod
	def get_user_agent_identifiers(user_agent):
	#
		"""
Return a UPnP client based on the given HTTP or SSDP user agent value.

:param user_agent: HTTP or SSDP user agent value

:return: (Client) UPnP client; None on error
:since:  v0.1.00
		"""

		var_return = ""

		replacement_list = Settings.get("pas_upnp_client_replacement_list", None)

		if (type(replacement_list) == dict):
		#
			for upnp_value in replacement_list: user_agent = user_agent.replace(upnp_value, replacement_list[upnp_value])
		#

		for re_result in re.finditer("([\d\w\.]+\W[0-9\.]+)", user_agent):
		#
			if (var_return != ""): var_return += "_"
			var_return += re.sub("\W+", "_", re_result.group(1))
		#

		if (var_return == ""): var_return = re.sub("\W+", "_", var_return).lower()
		else: var_return = var_return.lower()

		return var_return
	#

	@staticmethod
	def load_user_agent(user_agent):
	#
		"""
Return a UPnP client based on the given HTTP or SSDP user agent value.

:param user_agent: HTTP or SSDP user agent value

:return: (Client) UPnP client; None on error
:since:  v0.1.00
		"""

		if (type(user_agent) == str):
		#
			var_return = Hooks.call("dNG.pas.upnp.client.user_agent_get", user_agent = user_agent)

			if (var_return == None):
			#
				identifier = Client.get_user_agent_identifiers(user_agent)
				LogLine.debug("pas.upnp client requested user agent with identifier '{0}'".format(identifier))

				settings = Client.get_settings_file("{0}/upnp/user_agents/{1}.json".format(Settings.get("path_data"), identifier))

				if (type(settings) == dict):
				#
					var_return = Client()
					var_return.update(settings)
				#
			#
		#
		else: var_return = None

		return var_return
	#
#

##j## EOF