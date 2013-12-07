# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.Service
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

from dNG.data.xml_writer import XmlWriter
from dNG.data.rfc.http import Http
from dNG.pas.data.binary import Binary
from dNG.pas.data.traced_exception import TracedException
from dNG.pas.module.named_loader import NamedLoader
from .service_proxy import ServiceProxy
from .variable import Variable

class Service(object):
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

	RE_CAMEL_CASE_SPLITTER = NamedLoader.RE_CAMEL_CASE_SPLITTER
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
Constructor __init__(Service)

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
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
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

		if (self.variables == None or name not in self.variables): raise ValueError("'{0}' is not a defined SCPD variable".format(name))
		return self.variables[name]
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

:return: (ServiceProxy) UPnP proxy
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Service.get_proxy()- (#echo(__LINE__)#)")

		if (self.actions == None and self.variables == None): self.init_scpd()
		return ServiceProxy(self, self.actions, self.variables)
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

:return: (str) UPnP service UDN
:since:  v0.1.00
		"""

		return self.identifier['uuid']
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP service specification domain.

:return: (str) UPnP service specification domain
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
Initialize the service metadata from a UPnP description.

:param device_identifier: Parsed UPnP device identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		xml_parser = self._init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:service") > 0): xml_parser.node_set_cache_path("upnp:service")
		else: _return = False

		if (_return):
		#
			value = xml_parser.node_get_value("upnp:service upnp:serviceType")
			re_result = (None if (value == None) else Service.RE_USN_URN.match(value))

			if (re_result == None or re_result.group(2) != "service"): _return = False
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
					"usn": "uuid:{0}::{1}".format(device_identifier['uuid'], value),
					"urn": urn,
					"domain": re_result.group(1),
					"type": re_result.group(3),
					"version": re_result.group(4)
				}
			#
		#

		if (_return):
		#
			value = xml_parser.node_get_value("upnp:service upnp:serviceId")
			re_result = (None if (value == None) else Service.RE_SERVICE_ID_URN.match(value))

			if (re_result == None or re_result.group(2) != "serviceId"): _return = False
			else: self.service_id = { "urn": value[4:], "domain": re_result.group(1), "id": re_result.group(3) }
		#

		if (_return):
		#
			self.url_scpd = Binary.str(urljoin(url_base, xml_parser.node_get_value("upnp:service upnp:SCPDURL")))
			self.url_control = Binary.str(urljoin(url_base, xml_parser.node_get_value("upnp:service upnp:controlURL")))

			value = xml_parser.node_get_value("upnp:service upnp:eventSubURL")
			self.url_event_control = (None if (value.strip == "") else Binary.str(urljoin(url_base, value)))
		#

		return _return
	#

	def init_scpd(self):
	#
		"""
Initialize actions from the SCPD URL.

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = False

		os_uname = uname()

		http_client = Http(self.url_scpd, event_handler = self.log_handler)
		http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
		http_response = http_client.request_get()

		if (not isinstance(http_response['body'], Exception)): _return = self.init_xml_scpd(Binary.str(http_response['body']))
		elif (self.log_handler != None): self.log_handler.error(http_response['body'])

		return _return
	#

	def _init_xml_parser(self):
	#
		"""
Returns a XML parser with predefined XML namespaces.

:return: (object) XML parser
:since:  v0.1.00
		"""

		_return = XmlWriter(node_type = OrderedDict)
		_return.ns_register("scpd", "urn:schemas-upnp-org:service-1-0")
		return _return
	#

	def init_xml_scpd(self, xml_data):
	#
		"""
Initialize the list of service actions from a UPnP SCPD description.

:param xml_data: Received UPnP SCPD

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		try:
		#
			self.actions = None
			self.variables = None
			xml_parser = self._init_xml_parser()

			if (xml_parser.xml2dict(xml_data) == None or xml_parser.node_count("scpd:scpd") < 1): _return = False
			else: xml_parser.node_set_cache_path("scpd:scpd")

			if (_return):
			#
				self.spec_major = int(xml_parser.node_get_value("scpd:scpd scpd:specVersion scpd:major"))
				self.spec_minor = int(xml_parser.node_get_value("scpd:scpd scpd:specVersion scpd:minor"))
			#

			variables_count = (xml_parser.node_count("scpd:scpd scpd:serviceStateTable scpd:stateVariable") if (_return) else 0)

			if (variables_count > 0):
			#
				self.variables = { }
				xml_parser.node_set_cache_path("scpd:scpd scpd:serviceStateTable")

				for position in range(0, variables_count):
				#
					multicast_events = False
					send_events = True
					xml_base_path = "scpd:scpd scpd:serviceStateTable scpd:stateVariable#{0:d}".format(position)

					xml_node_attributes = xml_parser.node_get_attributes(xml_base_path)
					if ("sendEvents" in xml_node_attributes and xml_node_attributes['sendEvents'].lower() == "no"): send_events = False
					if ("multicast" in xml_node_attributes and xml_node_attributes['multicast'].lower() == "yes"): multicast_events = True

					name = xml_parser.node_get_value("{0} scpd:name".format(xml_base_path))
					_type = Variable.get_native_type_from_xml(xml_parser, xml_parser.node_get("{0} scpd:dataType".format(xml_base_path)))

					if (_type == False): raise TracedException("Invalid dataType definition found")
					self.variables[name] = { "is_sending_events": send_events, "is_multicasting_events": multicast_events, "type": _type }

					value = xml_parser.node_get_value("{0} scpd:defaultValue".format(xml_base_path))
					if (value != None): self.variables[name]['value'] = value

					allowed_values_count = xml_parser.node_count("{0} scpd:allowedValueList scpd:allowedValue".format(xml_base_path))

					if (allowed_values_count > 0):
					#
						self.variables[name]['values_allowed'] = [ ]
						if (_type != str): raise TracedException("SCPD can only contain allowedValue elements if the dataType is set to 'string'")

						for position_allowed in range(0, allowed_values_count):
						#
							value = xml_parser.node_get_value("{0} scpd:allowedValueList scpd:allowedValue#{1:d}".format(xml_base_path, position_allowed))
							if (value != None and value not in self.variables[name]['values_allowed']): self.variables[name]['values_allowed'].append(value)
						#
					#

					xml_node = xml_parser.node_get("{0} scpd:allowedValueRange".format(xml_base_path))

					if (xml_node != None):
					#
						if (allowed_values_count > 0): raise TracedException("SCPD can only contain one of allowedValueList and allowedValueRange")

						self.variables[name]['values_min'] = xml_parser.node_get_value("{0} scpd:allowedValueRange scpd:minimum".format(xml_base_path))
						self.variables[name]['values_max'] = xml_parser.node_get_value("{0} scpd:allowedValueRange scpd:maximum".format(xml_base_path))

						value = xml_parser.node_get("{0} scpd:allowedValueRange scpd:step".format(xml_base_path))
						if (value != None): self.variables[name]['values_stepping'] = value
					#
				#
			#
			else: _return = False

			actions_count = (xml_parser.node_count("scpd:scpd scpd:actionList scpd:action") if (_return) else 0)

			if (actions_count > 0):
			#
				self.actions = { }
				xml_parser.node_set_cache_path("scpd:scpd scpd:actionList")

				for position in range(0, actions_count):
				#
					name = xml_parser.node_get_value("scpd:scpd scpd:actionList scpd:action#{0:d} scpd:name".format(position))

					action_arguments_count = xml_parser.node_count("scpd:scpd scpd:actionList scpd:action#{0:d} scpd:argumentList scpd:argument".format(position))
					self.actions[name] = { "argument_variables": [ ], "return_variable": None, "result_variables": [ ] }

					if (action_arguments_count > 0):
					#
						for position_argument in range(0, action_arguments_count):
						#
							xml_base_path = "scpd:scpd scpd:actionList scpd:action#{0:d} scpd:argumentList scpd:argument#{1:d}".format(position, position_argument)

							argument_name = xml_parser.node_get_value("{0} scpd:name".format(xml_base_path))

							value = xml_parser.node_get_value("{0} scpd:direction".format(xml_base_path))
							argument_type = ("argument_variables" if (value.strip().lower() == "in") else "result_variables")

							value = xml_parser.node_get_value("{0} scpd:retval".format(xml_base_path))
							if (argument_type == "result_variables" and value != None): argument_type = "return_variable"

							value = xml_parser.node_get_value("{0} scpd:relatedStateVariable".format(xml_base_path))

							if (value not in self.variables): raise TracedException("SCPD can only contain arguments defined as an stateVariable")

							if (argument_type == "return_variable"): self.actions[name]['return_variable'] = { "name": argument_name, "variable": value }
							else: self.actions[name][argument_type].append({ "name": argument_name, "variable": value })
						#
					#
				#
			#
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			_return = False
		#

		return _return
	#

	def is_initialized(self):
	#
		"""
"is_initialized()" returns true if it is initialized.

:return: (bool) True if already initialized
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
Request the given SOAP action with the given arguments from a remote UPnP
device.

:param action: SOAP action
:param arguments: SOAP action arguments

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Service.request_soap_action({0}, arguments)- (#echo(__LINE__)#)".format(action))

		_return = False

		os_uname = uname()
		urn = "urn:{0}".format(self.identifier['urn'])

		xml_parser = self._init_xml_parser()

		xml_parser.node_add("Envelope", attributes = { "xmlns": "http://schemas.xmlsoap.org/soap/envelope/", "encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
		xml_parser.node_add("Envelope Header")

		xml_parser.node_add("Envelope Body")
		xml_base_path = "Envelope Body {0}".format(action)

		xml_parser.node_add(xml_base_path, attributes = { "xmlns": urn })
		xml_parser.node_set_cache_path("Envelope Body")

		for argument in arguments: xml_parser.node_add("{0} {1}".format(xml_base_path, argument['name']), argument['value'])

		http_client = Http(self.url_control, event_handler = self.log_handler)
		http_client.set_header("Content-Type", "text/xml; charset=UTF-8")
		http_client.set_header("SoapAction", "{0}#{1}".format(urn, action))
		http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))

		http_response = http_client.request_post(xml_parser.cache_export(True))

		if (not isinstance(http_response['body'], Exception)): _return = xml_parser.xml2data(Binary.str(http_response['body']))
		elif (self.log_handler != None): self.log_handler.error(http_response['body'])

		if (_return == True):
		#
			pass
		#

		return _return
	#
#

##j## EOF