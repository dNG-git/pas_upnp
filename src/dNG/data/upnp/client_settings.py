# -*- coding: utf-8 -*-

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

from os import path
import re

from dNG.data.binary import Binary
from dNG.data.cache.json_file_content import JsonFileContent
from dNG.data.logging.log_line import LogLine
from dNG.data.settings import Settings
from dNG.data.text.input_filter import InputFilter
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook
from dNG.runtime.thread_lock import ThreadLock

class ClientSettings(object):
    """
This class holds static methods to handle UPnP client settings.

@TODO: Add host protocolinfo specific code

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self, user_agent = None, host = None):
        """
Constructor __init__(ClientSettings)

:since: v0.2.00
        """

        self.host = host
        """
Client host
        """
        self.host_protocol_info_dict = None
        """
Client UPnP protocol info dictionary
        """
        self._lock = ThreadLock()
        """
Thread safety lock
        """
        self.user_agent = user_agent
        """
Client user agent
        """
        self.user_agent_file_dict = None
        """
User agent file specific dictionary
        """
    #

    def __contains__(self, item):
        """
python.org: Called to implement membership test operators.

:param item: Item to be looked up

:return: (bool) True if "__getitem__()" call will be successfully
:since:  v0.2.00
        """

        if (self.user_agent_file_dict is None): self._init_settings()
        if (item[:14] == "upnp_protocol_"): self._init_host_protocol_info()

        _return = (item in self.user_agent_file_dict)

        if (not _return
            and self.host_protocol_info_dict is not None
           ): _return = (item in self.host_protocol_info_dict)

        return _return
    #

    def __getitem__(self, key):
        """
python.org: Called to implement evaluation of self[key].

:param name: Attribute name

:return: (mixed) Attribute value
:since:  v0.2.00
        """

        if (self.user_agent_file_dict is None): self._init_settings()
        if (key[:14] == "upnp_protocol_"): self._init_host_protocol_info()

        _return = (None
                   if (self.host_protocol_info_dict is None) else
                   self.host_protocol_info_dict.get(key, None)
                  )

        if (_return is None): _return = self.user_agent_file_dict[key]

        return _return
    #

    def get(self, key, default = None):
        """
python.org: Return the value for key if key is in the dictionary, else
default.

:param key: Key
:param default: Default return value

:return: (mixed) Value
:since:  v0.2.00
        """

        _return = default

        try: _return = self[key]
        except KeyError: pass

        return _return
    #

    def get_host(self):
        """
Returns the UPnP client host requesting the resource.

:return: (str) Client host if known; None otherwise
:since:  v0.2.00
        """

        return self.host
    #

    def get_user_agent(self):
        """
Returns the UPnP client user agent requesting the resource.

:return: (str) Client user agent if known; None otherwise
:since:  v0.2.00
        """

        return self.user_agent
    #

    def _init_host_protocol_info(self):
        """
Initializes the client settings UPnP host based protocol info dictionary if
the UPnP host has been previously defined.

:since: v0.2.00
        """

        if (self.host is not None and self.host_protocol_info_dict is None):
            with self._lock:
                # Thread safety
                if (self.host_protocol_info_dict is None):
                    self.host_protocol_info_dict = { }

                    control_point = NamedLoader.get_singleton("dNG.net.upnp.ControlPoint")

                    connection_manager = None
                    device = control_point.get_rootdevice_for_host(self.host, "MediaRenderer")

                    if (device is not None): connection_manager = device.get_service("ConnectionManager")

                    if (connection_manager is not None and connection_manager.is_action_supported("GetProtocolInfo")):
                        connection_manager_proxy = connection_manager.get_proxy()

                        protocol_info = connection_manager_proxy.GetProtocolInfo()

                        supported_list = protocol_info.get("Source", "").split(",")
                        self.host_protocol_info_dict['upnp_protocol_source_supported_list'] = supported_list

                        supported_list = protocol_info.get("Sink", "").split(",")
                        self.host_protocol_info_dict['upnp_protocol_sink_supported_list'] = supported_list
                    #
                #
            #
        #
    #

    def _init_settings(self):
        """
Initializes the client settings user agent dictionary.

:since: v0.2.00
        """

        if (self.user_agent_file_dict is None):
            with self._lock:
                # Thread safety
                if (self.user_agent_file_dict is None):
                    self.user_agent_file_dict = ClientSettings.get_user_agent_settings(self.user_agent)
                #
            #
        #
    #

    def set_host(self, host):
        """
Sets the UPnP client host.

:param host: Client host

:since: v0.2.00
        """

        self.host = host
        self.host_protocol_info_dict = None
    #

    @staticmethod
    def get_user_agent_settings(user_agent):
        """
Returns the user agent specific client settings dictionary.

:param user_agent: User agent

:return: (dict) User agent specific client settings; None on error
:since:  v0.2.00
        """

        _return = { }

        settings = None
        user_agent = Binary.str(user_agent)

        if (type(user_agent) is str):
            settings = Hook.call("dNG.pas.upnp.Client.getUserAgentSettings", user_agent = user_agent)

            if (not isinstance(settings, dict)):
                identifier = ClientSettings.get_user_agent_identifiers(user_agent)
                settings_file_name = "{0}.json".format(identifier)

                settings = JsonFileContent.read(path.join(Settings.get("path_data"),
                                                          "upnp",
                                                          "user_agents",
                                                          settings_file_name
                                                         )
                                               )

                if (settings is None):
                    log_line = "pas.upnp.ClientSettings reporting: No client settings found for user agent '{0}' with identifier '{1}'"

                    if (Settings.get("pas_upnp_log_missing_user_agent", False)): LogLine.warning(log_line, user_agent, identifier, context = "pas_upnp")
                    else: LogLine.debug(log_line, user_agent, identifier, context = "pas_upnp")
                #
            #
        #

        if (settings is not None):
            if ("client_file" in settings):
                base_settings = JsonFileContent.read(path.join(Settings.get("path_data"),
                                                               "upnp",
                                                               "user_agents",
                                                               InputFilter.filter_file_path(settings['client_file'])
                                                              )
                                                    )

                if (type(base_settings) is dict): _return.update(base_settings)
                del(settings['client_file'])
            #

            _return.update(settings)
        #

        return _return
    #

    @staticmethod
    def get_user_agent_identifiers(user_agent):
        """
Returns a UPnP client based on the given HTTP or SSDP user agent value.

:param user_agent: HTTP or SSDP user agent value

:return: (object) UPnP client; None on error
:since:  v0.2.00
        """

        _return = ""

        if (not Settings.is_defined("pas_upnp_client_replacement_list")): Settings.read_file("{0}/settings/pas_upnp.json".format(Settings.get("path_data")))
        replacement_list = Settings.get("pas_upnp_client_replacement_list", None)

        if (type(replacement_list) is dict):
            replacement_list_keys = sorted(replacement_list.keys(), reverse = True)
            for upnp_value in replacement_list_keys: user_agent = user_agent.replace(upnp_value, replacement_list[upnp_value])
        #

        for re_result in re.finditer("([\\d\\w\\.]+/([0-9\\.]+(\\W|$))+)", user_agent):
            if (_return != ""): _return += "_"
            _return += re.sub("\\W+", "_", re_result.group(1)).strip("_")
        #

        if (_return == ""): _return = re.sub("\\W+", "_", user_agent).lower()
        else: _return = _return.lower()

        return _return
    #
#
