# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.service
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

from collections import OrderedDict
from os import uname
import re

try: from urllib.parse import urljoin
except ImportError: from urlparse import urljoin

from dNG.data.xml_writer import direct_xml_writer
from dNG.data.rfc.http import direct_http
from dNG.pas.data.binary import direct_binary
from dNG.pas.module.named_loader import direct_named_loader
from .service_proxy import direct_service_proxy
from .variable import direct_variable

class direct_service(object):
#
	"""
The UPnP common service implementation.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	RE_CAMEL_CASE_SPLITTER = re.compile("([a-z0-9]|[A-Z]+(?![A-Z]+$))([A-Z])")
	"""
CamelCase RegExp
	"""
	RE_SERVICE_ID_URN = re.compile("^urn:(.+):(.+):(.*)$", re.I)
	"""
serviceId URN RegExp
	"""
	RE_USN_URN = re.compile("^urn:(.+):(.+):(.*):(.*)$", re.I)
	"""
URN RegExp
	"""

	def __init__(self):
	#
		"""
Constructor __init__(direct_service)

:since: v0.1.00
		"""

		self.actions = None
		"""
Service actions defined in the SCPD
		"""
		self.identifier = None
		"""
Parsed UPnP identifier
		"""
		self.log_handler = direct_named_loader.get_singleton("dNG.pas.data.logging.log_handler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.name = None
		"""
UPnP service name
		"""
		self.service_id = None
		"""
UPnP serviceId value
		"""
		self.url_base = None
		"""
HTTP base URL
		"""
		self.url_control = None
		"""
UPnP controlURL value
		"""
		self.url_event_control = None
		"""
UPnP eventSubURL value
		"""
		self.url_scpd = None
		"""
UPnP SCPDURL value
		"""
		self.variables = None
		"""
Service variables defined in the SCPD
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(direct_service)

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.return_instance()
	#

	def get_configid(self):
	#
		"""
Returns the UPnP configId value.

:return: (int) UPnP configId
:since:  v0.1.00
		"""

		return self.configid
	#

	def get_definition_variable(self, name):
	#
		"""
Returns the UPnP variable definition.

:param name: Variable name

:return: (dict) Variable definition
:since:  v0.1.00
		"""

		if (self.variables != None and name in self.variables): return self.variables[name]
		else: raise ValueError("'{0}' is not a defined SCPD variable".format(name))
	#

	def get_name(self):
	#
		"""
Returns the UPnP service name (URN without version).

:return: (str) Service name
:since:  v0.1.00
		"""

		return self.name
	#

	def get_proxy(self):
	#
		"""
Return a callable proxy object for UPnP actions and variables.

:return: (direct_service_proxy) UPnP proxy
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpService.get_proxy()- (#echo(__LINE__)#)")

		if (self.actions == None and self.variables == None): self.init_scpd()
		return direct_service_proxy(self, self.actions, self.variables)
	#

	def get_service_id(self):
	#
		"""
Returns the UPnP serviceId value.

:return: (dict) Dict containing the URN, the specification domain and the ID
:since:  v0.1.00
		"""

		return self.service_id['id']
	#

	def get_service_id_urn(self):
	#
		"""
Returns the UPnP serviceId value.

:return: (dict) Dict containing the URN, the specification domain and the ID
:since:  v0.1.00
		"""

		return self.service_id['urn']
	#

	def get_type(self):
	#
		"""
Returns the UPnP service type.

:return: (str) Service type
:since:  v0.1.00
		"""

		return self.identifier['type']
	#

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP device UUID
:since:  v0.1.00
		"""

		return self.identifier['uuid']
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP service specification domain.

:return: (str) UPnP device specification domain
:since:  v0.1.00
		"""

		return self.identifier['domain']
	#

	def get_url_base(self):
	#
		"""
Returns the HTTP base URL.

:return: (str) HTTP base URL
:since:  v0.1.00
		"""

		return self.url_base
	#

	def get_url_control(self):
	#
		"""
Returns the UPnP controlURL value.

:return: (str) SOAP endpoint URL
:since:  v0.1.00
		"""

		return self.url_control
	#

	def get_url_event_control(self):
	#
		"""
Returns the UPnP eventSubURL value.

:return: (str) Event subscription endpoint; None if not set
:since:  v0.1.00
		"""

		return self.url_event_control
	#

	def get_url_scpd(self):
	#
		"""
Returns the UPnP SCPDURL value.

:return: (str) SCPDURL value
:since:  v0.1.00
		"""

		return self.url_scpd
	#

	def get_urn(self):
	#
		"""
Returns the UPnP serviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return self.identifier['urn']
	#

	def get_version(self):
	#
		"""
Returns the UPnP service type version.

:return: (str) Service type version
:since:  v0.1.00
		"""

		return self.identifier['version']
	#

	def init_metadata_xml_tree(self, device_identifier, url_base, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param device_identifier: Parsed UPnP device identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		xml_parser = self.init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:service") > 0): xml_parser.node_set_cache_path("upnp:service")
		else: var_return = False

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:service upnp:serviceType")
			re_result = (None if (xml_node == False) else direct_service.RE_USN_URN.match(xml_node['value']))

			if (re_result == None or re_result.group(2) != "service"): var_return = False
			else:
			#
				self.name = "{0}:service:{1}".format(re_result.group(1), re_result.group(3))
				urn = "{0}:{1}".format(self.name, re_result.group(4))

				self.identifier = {
					"device": device_identifier['device'],
					"bootid": device_identifier['bootid'],
					"configid": device_identifier['configid'],
					"uuid": device_identifier['uuid'],
					"class": "service",
					"usn": "uuid:{0}::{1}".format(device_identifier['uuid'], xml_node['value']),
					"urn": urn,
					"domain": re_result.group(1),
					"type": re_result.group(3),
					"version": re_result.group(4)
				}
			#
		#

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:service upnp:serviceId")
			re_result = (None if (xml_node == False) else direct_service.RE_SERVICE_ID_URN.match(xml_node['value']))

			if (re_result == None or re_result.group(2) != "serviceId"): var_return = False
			else: self.service_id = { "urn": xml_node['value'][4:], "domain": re_result.group(1), "id": re_result.group(3) }
		#

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:service upnp:SCPDURL")
			self.url_scpd = direct_binary.str(urljoin(url_base, xml_node['value']))

			xml_node = xml_parser.node_get("upnp:service upnp:controlURL")
			self.url_control = direct_binary.str(urljoin(url_base, xml_node['value']))

			xml_node = xml_parser.node_get("upnp:service upnp:eventSubURL")
			self.url_event_control = (None if (xml_node['value'].strip == "") else direct_binary.str(urljoin(url_base, xml_node['value'])))
		#

		return var_return
	#

	def init_scpd(self):
	#
		"""
Initialize actions from the SCPD URL.

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = False

		os_uname = uname()

		http_client = direct_http(self.url_scpd, event_handler = self.log_handler)
		http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
		http_response = http_client.request_get()

		if (not isinstance(http_response['body'], Exception)): var_return = self.init_xml_scpd(direct_binary.str(http_response['body']))
		elif (self.log_handler != None): self.log_handler.error(http_response['body'])

		return var_return
	#

	def init_xml_parser(self):
	#
		"""
Returns a XML parser with predefined XML namespaces.

:access: protected
:return: (object) XML parser
:since:  v0.1.00
		"""

		var_return = direct_xml_writer(node_type = OrderedDict)
		var_return.ns_register("scpd", "urn:schemas-upnp-org:service-1-0")
		return var_return
	#

	def init_xml_scpd(self, xml_data):
	#
		"""
Initialize actions from a SCPD.

:param xml_data: Received UPnP SCPD

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		try:
		#
			self.actions = None
			self.variables = None
			xml_parser = self.init_xml_parser()

			if (xml_parser.xml2dict(xml_data) != False and xml_parser.node_count("scpd:scpd") > 0): xml_parser.node_set_cache_path("scpd:scpd")
			else: var_return = False

			if (var_return):
			#
				xml_node = xml_parser.node_get("scpd:scpd scpd:specVersion scpd:major")
				self.spec_major = int(xml_node['value'])

				xml_node = xml_parser.node_get("scpd:scpd scpd:specVersion scpd:minor")
				self.spec_minor = int(xml_node['value'])
			#

			variables_count = (xml_parser.node_count("scpd:scpd scpd:serviceStateTable scpd:stateVariable") if (var_return) else 0)

			if (variables_count > 0):
			#
				self.variables = { }
				xml_parser.node_set_cache_path("scpd:scpd scpd:serviceStateTable")

				for position in range(0, variables_count):
				#
					multicast_events = False
					send_events = True
					xml_base_path = "scpd:scpd scpd:serviceStateTable scpd:stateVariable#{0:d}".format(position)

					xml_node = xml_parser.node_get(xml_base_path, False)

					if ("attributes" in xml_node['xml.item']):
					#
						if ("sendEvents" in xml_node['xml.item']['attributes'] and xml_node['xml.item']['attributes']['sendEvents'].lower() == "no"): send_events = False
						if ("multicast" in xml_node['xml.item']['attributes'] and xml_node['xml.item']['attributes']['multicast'].lower() == "yes"): multicast_events = True
					#

					xml_node = xml_parser.node_get("{0} scpd:name".format(xml_base_path))
					name = xml_node['value']

					xml_node = xml_parser.node_get("{0} scpd:dataType".format(xml_base_path))
					var_type = direct_variable.get_native_type_from_xml(xml_parser, xml_node)

					if (var_type == False): raise ValueError("Invalid dataType definition found")
					else: self.variables[name] = { "is_sending_events": send_events, "is_multicasting_events": multicast_events, "type": var_type }

					xml_node = xml_parser.node_get("{0} scpd:defaultValue".format(xml_base_path))
					if (xml_node != False): self.variables[name]['value'] = xml_node['value']

					allowed_values_count = xml_parser.node_count("{0} scpd:allowedValueList scpd:allowedValue".format(xml_base_path))

					if (allowed_values_count > 0):
					#
						self.variables[name]['values_allowed'] = [ ]
						if (var_type != str): raise ValueError("SCPD can only contain allowedValue elements if the dataType is set to 'string'")

						for position_allowed in range(0, allowed_values_count):
						#
							xml_node = xml_parser.node_get("{0} scpd:allowedValueList scpd:allowedValue#{1:d}".format(xml_base_path, position_allowed))
							if (xml_node != False and xml_node['value'] not in self.variables[name]['values_allowed']): self.variables[name]['values_allowed'].append(xml_node['value'])
						#
					#

					xml_node = xml_parser.node_get("{0} scpd:allowedValueRange".format(xml_base_path))

					if (xml_node != False):
					#
						if (allowed_values_count > 0): raise ValueError("SCPD can only contain one of allowedValueList and allowedValueRange")

						xml_node = xml_parser.node_get("{0} scpd:allowedValueRange scpd:minimum".format(xml_base_path))
						self.variables[name]['values_min'] = xml_node['value']

						xml_node = xml_parser.node_get("{0} scpd:allowedValueRange scpd:maximum".format(xml_base_path))
						self.variables[name]['values_max'] = xml_node['value']

						xml_node = xml_parser.node_get("{0} scpd:allowedValueRange scpd:step".format(xml_base_path))
						if (xml_node != False): self.variables[name]['values_stepping'] = xml_node['value']
					#
				#
			#
			else: var_return = False

			actions_count = (xml_parser.node_count("scpd:scpd scpd:actionList scpd:action") if (var_return) else 0)

			if (actions_count > 0):
			#
				self.actions = { }
				xml_parser.node_set_cache_path("scpd:scpd scpd:actionList")

				for position in range(0, actions_count):
				#
					xml_node = xml_parser.node_get("scpd:scpd scpd:actionList scpd:action#{0:d} scpd:name".format(position))
					name = xml_node['value']

					action_arguments_count = xml_parser.node_count("scpd:scpd scpd:actionList scpd:action#{0:d} scpd:argumentList scpd:argument".format(position))
					self.actions[name] = { "argument_variables": [ ], "return_variable": None, "result_variables": [ ] }

					if (action_arguments_count > 0):
					#
						for position_argument in range(0, action_arguments_count):
						#
							xml_base_path = "scpd:scpd scpd:actionList scpd:action#{0:d} scpd:argumentList scpd:argument#{1:d}".format(position, position_argument)

							xml_node = xml_parser.node_get("{0} scpd:name".format(xml_base_path))
							argument_name = xml_node['value']

							xml_node = xml_parser.node_get("{0} scpd:direction".format(xml_base_path))
							argument_type = ("argument_variables" if (xml_node['value'].strip().lower() == "in") else "result_variables")

							xml_node = xml_parser.node_get("{0} scpd:retval".format(xml_base_path))
							if (argument_type == "result_variables" and xml_node != False): argument_type = "return_variable"

							xml_node = xml_parser.node_get("{0} scpd:relatedStateVariable".format(xml_base_path))

							if (xml_node['value'] in self.variables):
							#
								if (argument_type == "return_variable"): self.actions[name]['return_variable'] = { "name": argument_name, "variable": xml_node['value'] }
								else: self.actions[name][argument_type].append({ "name": argument_name, "variable": xml_node['value'] })
							#
							else: raise ValueError("SCPD can only contain arguments defined as an stateVariable")
						#
					#
				#
			#
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			import traceback
			traceback.print_exc()
			var_return = False
		#

		return var_return
	#

	def is_initialized(self):
	#
		"""
"is_initialized()" returns .

:access: protected
:return: (object) XML parser
:since:  v0.1.00
		"""

		return (False if (self.actions == None and self.variables == None) else True)
	#

	def is_managed(self):
	#
		"""
True if the host manages the service.

:return: (bool) False if remote UPnP service
:since:  v0.1.00
		"""

		return False
	#

	def request_soap_action(self, action, arguments):
	#
		"""
Initialize actions from the SCPD URL.

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpService.request_soap_action({0}, arguments)- (#echo(__LINE__)#)".format(action))

		var_return = False

		os_uname = uname()
		urn = "urn:{0}".format(self.identifier['urn'])

		xml_parser = self.init_xml_parser()

		xml_parser.node_add("Envelope", attributes = { "xmlns": "http://schemas.xmlsoap.org/soap/envelope/", "encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
		xml_parser.node_add("Envelope Header")

		xml_parser.node_add("Envelope Body")
		xml_base_path = "Envelope Body {0}".format(action)

		xml_parser.node_add(xml_base_path, attributes = { "xmlns": urn })
		xml_parser.node_set_cache_path("Envelope Body")

		for argument in arguments: xml_parser.node_add("{0} {1}".format(xml_base_path, argument['name']), argument['value'])

		http_client = direct_http(self.url_control, event_handler = self.log_handler)
		http_client.set_header("Content-Type", "text/xml; charset=UTF-8")
		http_client.set_header("SoapAction", "{0}#{1}".format(urn, action))
		http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))

		http_response = http_client.request_post(xml_parser.cache_export(True))

		if (not isinstance(http_response['body'], Exception)): var_return = xml_parser.xml2data(direct_binary.str(http_response['body']))
		elif (self.log_handler != None): self.log_handler.error(http_response['body'])

		if (var_return == True):
		#
			pass
		#

		return var_return
	#
#

##j## EOF