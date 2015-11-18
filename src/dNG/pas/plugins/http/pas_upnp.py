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

# pylint: disable=unused-argument

import socket

try: from urllib.parse import unquote
except ImportError: from urllib import unquote

from dNG.pas.controller.abstract_http_request import AbstractHttpRequest
from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.upnp.client_settings import ClientSettings
from dNG.pas.plugins.hook import Hook
from dNG.pas.net.upnp.control_point import ControlPoint
from dNG.pas.runtime.value_exception import ValueException

def handle_upnp_device_request(request, virtual_config):
#
	"""
Handles a UPnP device related HTTP request.

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	if (not isinstance(request, AbstractHttpRequest)): raise TranslatableException("pas_http_core_400", 400)

	client_host = request.get_client_host()
	control_point = ControlPoint.get_instance()
	is_allowed = False
	is_valid = False

	if (client_host is None): is_allowed = True
	else:
	#
		ip_address_list = socket.getaddrinfo(client_host, request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
		is_allowed = (False if (len(ip_address_list) < 1) else control_point.is_ip_allowed(ip_address_list[0][4][0]))
	#

	device = control_point.get_device(virtual_config['identifier'])

	if (is_allowed and device is not None):
	#
		virtual_path = request.get_dsd("upnp_path")

		if (virtual_path is not None):
		#
			request_data = virtual_path.split("/", 1)
			request_data_length = len(request_data)

			if (request_data_length < 2 and request_data[0] in ( "", "desc" )): is_valid = True
			elif (request_data[1] in ( "", "control", "eventsub", "xml" )
			      and device.get_service(request_data[0]) is not None
			     ): is_valid = True
		#
	#

	if (not is_allowed):
	#
		LogLine.warning("pas.upnp.ControlPoint refused client '{0}'", client_host, context = "pas_upnp")

		_return = PredefinedHttpRequest()
		_return.set_output_handler("http_upnp")
		_return.set_module("output")
		_return.set_service("http")
		_return.set_action("error")
		_return.set_dsd("code", "403")
	#
	elif (not is_valid):
	#
		_return = PredefinedHttpRequest()
		_return.set_output_handler("http_upnp")
		_return.set_module("output")
		_return.set_service("http")
		_return.set_action("error")
		_return.set_dsd("code", "400")
	#
	else:
	#
		_return = HttpUpnpRequest()
		_return.set_request(request, control_point, device, request_data)
	#

	return _return
#

def handle_upnp_stream_request(request, virtual_config):
#
	"""
Handles a UPnP stream related HTTP request.

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	if (not isinstance(request, AbstractHttpRequest)): raise TranslatableException("pas_http_core_400", 400)

	user_agent = request.get_header("User-Agent")
	stream_path = request.get_dsd("upnp_path")

	client_settings = ClientSettings.load_user_agent(user_agent)

	if (client_settings.get("upnp_stream_path_use_filter", False)):
	#
		stream_path_filtered = Hook.call("dNG.pas.http.HttpUpnpRequest.filterStreamPath", path = stream_path, user_agent = user_agent)
		if (stream_path_filtered is not None): stream_path = stream_path_filtered
	#

	if (stream_path is not None): stream_path = unquote(stream_path)

	_return = PredefinedHttpRequest()
	_return.set_module("upnp")
	_return.set_service("stream")
	_return.set_action("resource")
	_return.set_dsd("urid", stream_path)

	return _return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.http.Server.onShutdown", on_shutdown)
	Hook.register("dNG.pas.http.Server.onStartup", on_startup)
	Hook.register("dNG.pas.http.Wsgi.onShutdown", on_shutdown)
	Hook.register("dNG.pas.http.Wsgi.onStartup", on_startup)
	Hook.register("dNG.pas.upnp.ControlPoint.onHostDeviceAdded", on_host_device_added)
#

def on_host_device_added(params, last_return = None):
#
	"""
Called for "dNG.pas.upnp.ControlPoint.onHostDeviceAdded"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	if ("identifier" not in params): raise ValueException("Missing required parameter")

	VirtualConfig.set_virtual_path("/upnp/{0}/".format(params['identifier']['uuid']),
	                               { "path": "upnp_path", "identifier": params['identifier'] },
	                               handle_upnp_device_request
	                              )
#

def on_shutdown(params, last_return = None):
#
	"""
Called for "dNG.pas.http.Server.onShutdown" and "dNG.pas.http.Wsgi.onShutdown"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.03
	"""

	VirtualConfig.unset_virtual_path("/upnp/image/")
	VirtualConfig.unset_virtual_path("/upnp/stream/")

	return last_return
#

def on_startup(params, last_return = None):
#
	"""
Called for "dNG.pas.http.Server.onStartup" and "dNG.pas.http.Wsgi.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	VirtualConfig.set_virtual_path("/upnp/image/", { "m": "upnp", "s": "image", "path_parameters": True })
	VirtualConfig.set_virtual_path("/upnp/stream/", { "path": "upnp_path" }, handle_upnp_stream_request)

	return last_return
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.http.Server.onShutdown", on_shutdown)
	Hook.unregister("dNG.pas.http.Server.onStartup", on_startup)
	Hook.unregister("dNG.pas.http.Wsgi.onShutdown", on_shutdown)
	Hook.unregister("dNG.pas.http.Wsgi.onStartup", on_startup)
	Hook.unregister("dNG.pas.upnp.ControlPoint.onHostDeviceAdded", on_host_device_added)
#

##j## EOF