# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.services.abstract_service
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

from dNG.pas.data.text.url import Url
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.service import Service
from dNG.pas.data.upnp.variable import Variable

class AbstractService(Service):
#
	"""
An extended, abstract service implementation for server services.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractService)

:since: v0.1.00
		"""

		Service.__init__(self)

		self.client_user_agent = None
		"""
Client user agent
		"""
		self.configid = None
		"""
UPnP configId value
		"""
		self.host_service = False
		"""
UPnP service is managed by host
		"""
		self.spec_major = None
		"""
UPnP specVersion major number
		"""
		self.spec_minor = None
		"""
UPnP specVersion minor number
		"""
		self.type = None
		"""
UPnP service type
		"""
		self.udn = None
		"""
UPnP UDN value
		"""
		self.upnp_domain = None
		"""
UPnP service specification domain
		"""
		self.version = None
		"""
UPnP service type version
		"""
	#

	def client_set_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param configid: Client user agent

:since: v0.1.00
		"""

		self.client_user_agent = user_agent
	#

	def get_name(self):
	#
		"""
Returns the UPnP service name (URN without version).

:return: (str) Service name
:since:  v0.1.00
		"""

		return ("{0}:service:{1}".format(self.upnp_domain, self.type) if (self.host_service) else Service.get_name(self))
	#

	def get_service_id(self):
	#
		"""
Returns the UPnP service ID.

:return: (dict) UPnP service ID
:since:  v0.1.00
		"""

		return (self.service_id if (self.host_service) else Service.get_service_id(self))
	#

	def get_service_id_urn(self):
	#
		"""
Returns the UPnP serviceId value.

:return: (dict) UPnP serviceId URN
:since:  v0.1.00
		"""

		return ("{0}:serviceId:{1}".format(self.upnp_domain, self.service_id) if (self.host_service) else Service.get_service_id_urn(self))
	#

	def get_spec_version(self):
	#
		"""
Returns the UPnP specVersion number.

:return: (tuple) UPnP Device Architecture version: Major and minor number
:since:  v0.1.00
		"""

		return ( self.spec_major, self.spec_minor )
	#

	def get_type(self):
	#
		"""
Returns the UPnP service type.

:return: (str) Service type
:since:  v0.1.00
		"""

		return (self.type if (self.host_service) else Service.get_type(self))
	#

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP device UUID
:since:  v0.1.00
		"""

		return (self.udn if (self.host_service) else Service.get_udn(self))
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP service specification domain.

:return: (str) UPnP device UUID
:since:  v0.1.00
		"""

		return (self.upnp_domain if (self.host_service) else Service.get_upnp_domain(self))
	#

	def _get_unique_list(self, _list):
	#
		"""
Returns a list where each entry is unique.

:return: (list) Unique list of entries given
:since:  v0.1.01
		"""

		_return = [ ]

		for value in _list:
		#
			if (value not in _return): _return.append(value)
		#

		return _return
	#

	def get_urn(self):
	#
		"""
Returns the UPnP serviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return ("{0}:service:{1}:{2}".format(self.upnp_domain, self.type, self.version) if (self.host_service) else Service.get_urn(self))
	#

	def get_version(self):
	#
		"""
Returns the UPnP service type version.

:return: (str) Service type version
:since:  v0.1.00
		"""

		return (self.version if (self.host_service) else Service.get_version(self))
	#

	def get_xml(self, flush = True):
	#
		"""
Returns the UPnP SCPD.

:param flush: True to flush the XML parser instance and return the string
              representation.

:return: (str) Device description XML
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Service.get_xml(flush)- (#echo(__LINE__)#)")

		_return = self._init_xml_parser()

		client = Client.load_user_agent(self.client_user_agent)
		if (client != None and (not client.get("upnp_xml_cdata_encoded", True))): _return.define_cdata_encoding(False)

		attributes = { "xmlns": "urn:schemas-upnp-org:service-1-0" }
		if (self.configid != None): attributes['configId'] = self.configid

		_return.node_add("scpd", attributes = attributes)
		_return.node_set_cache_path("scpd")

		spec_version = self.get_spec_version()
		_return.node_add("scpd specVersion major", str(spec_version[0]))
		_return.node_add("scpd specVersion minor", str(spec_version[1]))

		if (len(self.actions) > 0):
		#
			position = 0

			for action_name in self.actions:
			#
				xml_base_path = "scpd actionList action#{0:d}".format(position)
				_return.node_add(xml_base_path)
				_return.node_set_cache_path(xml_base_path)

				action = self.actions[action_name]
				_return.node_add("{0} name".format(xml_base_path), action_name)

				variables = [ ]

				for variable in action['argument_variables']:
				#
					variable = variable.copy()
					variable['direction'] = "in"
					variables.append(variable)
				#

				if (action['return_variable'] != None):
				#
					variable = action['return_variable'].copy()
					variable['direction'] = "out"
					variable['retval'] = True
					variables.append(variable)
				#

				for variable in action['result_variables']:
				#
					variable = variable.copy()
					variable['direction'] = "out"
					variables.append(variable)
				#

				variables_count = len(variables)

				for position_variable in range(0, variables_count):
				#
					_return.node_add("{0} argumentList argument#{1:d}".format(xml_base_path, position_variable))
					_return.node_add("{0} argumentList argument#{1:d} name".format(xml_base_path, position_variable), variables[position_variable]['name'])
					_return.node_add("{0} argumentList argument#{1:d} direction".format(xml_base_path, position_variable), variables[position_variable]['direction'])
					if ("retval" in variables[position_variable]): _return.node_add("{0} argumentList argument#{1:d} retval".format(xml_base_path, position_variable))
					_return.node_add("{0} argumentList argument#{1:d} relatedStateVariable".format(xml_base_path, position_variable), variables[position_variable]['variable'])
				#

				position += 1
			#

			position_variable = 0
			_return.node_add("scpd serviceStateTable".format(xml_base_path))
			_return.node_set_cache_path("scpd serviceStateTable".format(xml_base_path))

			for variable_name in self.variables:
			#
				variable = self.variables[variable_name]
				xml_base_path = "scpd serviceStateTable stateVariable#{0:d}".format(position_variable)

				attributes = { }
				if (not variable['is_sending_events']): attributes['sendEvents'] = "no"
				if (variable['is_multicasting_events']): attributes['multicast'] = "yes"

				_return.node_add(xml_base_path, attributes = attributes)

				_return.node_add("{0} name".format(xml_base_path), variable_name)
				_return.node_add("{0} dataType".format(xml_base_path), variable['type'])
				if ("value" in variable): _return.node_add("{0} defaultValue".format(xml_base_path), variable['value'])

				values_allowed_count = (len(variable['values_allowed']) if ("values_allowed" in variable) else 0)
				for position_values_allowed in range(0, values_allowed_count): _return.node_add("{0} allowedValueList allowedValue#{1:d}".format(xml_base_path, position_values_allowed), variable['values_allowed'][position_values_allowed])

				if ("values_min" in variable): _return.node_add("{0} allowedValueRange minimum".format(xml_base_path), variable['values_min'])
				if ("values_max" in variable): _return.node_add("{0} allowedValueRange maximum".format(xml_base_path), variable['values_max'])
				if ("values_stepping" in variable): _return.node_add("{0} allowedValueRange step".format(xml_base_path), variable['values_stepping'])

				position_variable += 1
			#
		#

		return (_return.cache_export(True) if (flush) else _return)
	#

	def handle_soap_call(self, action, arguments_given = [ ]):
	#
		"""
Executes the given SOAP action.

:return: (list) Result list
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Service.handle_soap_call({0}, arguments_given)- (#echo(__LINE__)#)".format(action))
		_return = UpnpException("pas_http_error_500")

		action_method = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", action).lower()
		arguments = { }
		is_valid = (action in self.actions and hasattr(self, action_method))

		if (is_valid):
		#
			action = self.actions[action]

			for argument in action['argument_variables']:
			#
				if (argument['variable'] not in self.variables):
				#
					is_valid = False
					_return = UpnpException("pas_http_error_500")

					break
				#
				elif (argument['name'] in arguments_given): argument_given = arguments_given[argument['name']]
				elif ("value" in self.variables[argument['variable']]): argument_given = self.variables[argument['variable']]['value']
				else:
				#
					is_valid = False
					_return = UpnpException("pas_http_error_400", 402)

					break
				#

				if (is_valid):
				#
					argument_name = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", argument['name']).lower()
					arguments[argument_name] = Variable.get_native(Variable.get_native_type(self.variables[argument['variable']]), argument_given)
				#
			#
		#
		else: _return = UpnpException("pas_http_error_400", 401)

		result = None

		try:
		#
			if (is_valid): result = getattr(self, action_method)(**arguments)
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			_return = UpnpException("pas_http_error_500")
		#

		if (isinstance(result, Exception)): _return = result
		elif (result != None):
		#
			return_values = ([ ] if (action['return_variable'] == None) else [ action['return_variable'] ])
			return_values += action['result_variables']
			_return = [ ]
			_type = type(result)

			if (_type != dict and len(return_values) != 1): _return = UpnpException("pas_http_error_500")
			else:
			#
				for return_value in return_values:
				#
					return_value_name = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", return_value['name']).lower()

					if (_type == dict): result_value = (result[return_value_name] if (return_value_name in result) else None)
					else: result_value = result

					if (return_value['variable'] not in self.variables or result_value == None):
					#
						_return = UpnpException("pas_http_error_500")
						break
					#
					else: _return.append({ "name": return_value['name'], "value": Variable.get_upnp_value(self.variables[return_value['variable']], result_value) })
				#
			#
		#

		return _return
	#

	def init_service(self, device, service_id, configid = None):
	#
		"""
Initialize a host service.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.actions = { }
		self.configid = configid
		self.host_service = True
		self.variables = { }
		self.udn = device.get_udn()

		self.url_base = "{0}{1}/".format(device.get_url_base(), Url.escape(service_id))
		self.url_control = "{0}control".format(self.url_base)
		self.url_event_control = "{0}eventsub".format(self.url_base)
		self.url_scpd = "{0}xml".format(self.url_base)

		return False
	#

	def is_managed(self):
	#
		"""
True if the host manages the service.

:return: (bool) False if remote UPnP service
:since:  v0.1.00
		"""

		return self.host_service
	#

	def set_configid(self, configid):
	#
		"""
Sets the UPnP configId value.

:param configid: Current UPnP configId

:since: v0.1.00
		"""

		self.configid = configid
	#
#

##j## EOF