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

from dNG.pas.data.text.link import Link
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.upnp_exception import UpnpException
from dNG.pas.data.upnp.service import Service
from dNG.pas.data.upnp.variable import Variable
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.type_exception import TypeException

class AbstractService(Service):
#
	"""
An extended, abstract service implementation for server services.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
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

	def add_host_action(self, action, argument_variables = None, return_variable = None, result_variables = None):
	#
		"""
Adds the given host service action.

:param action: SOAP action
:param argument_variables: Argument variables definition
:param return_variable: Return variable definition
:param result_variables: Result variables definition

:since: v0.1.00
		"""

		if (action not in self.actions):
		#
			if (argument_variables == None): argument_variables = [ ]
			elif (type(argument_variables) != list): raise TypeException("Given argument variables definition is invalid")

			if (return_variable == None): return_variable = { }
			elif (type(return_variable) != dict): raise TypeException("Given return variables definition is invalid")

			if (result_variables == None): result_variables = [ ]
			elif (type(result_variables) != list): raise TypeException("Given result variables definition is invalid")

			self.actions[action] = { "argument_variables": argument_variables,
			                         "return_variable": return_variable,
			                         "result_variables": result_variables
			                       }
		#
	#

	def add_host_variable(self, name, definition):
	#
		"""
Adds the given host service variable.

:param name: Variable name
:param definition: Variable definition

:since: v0.1.00
		"""

		if (name not in self.variables):
		#
			if (type(definition) != dict): raise TypeException("Given variable definition is invalid")
			self.variables[name] = definition
		#
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
Returns the UPnP serviceId value.

:return: (str) UPnP serviceId value
:since:  v0.1.00
		"""

		return (self.service_id if (self.host_service) else Service.get_service_id(self))
	#

	def get_service_id_urn(self):
	#
		"""
Returns the UPnP serviceId value.

:return: (str) UPnP serviceId URN
:since:  v0.1.00
		"""

		return ("{0}:serviceId:{1}".format(self.upnp_domain, self.service_id) if (self.host_service) else Service.get_service_id_urn(self))
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

:return: (str) UPnP device UDN
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

	def get_urn(self):
	#
		"""
Returns the UPnP serviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return ("{0}:service:{1}:{2}".format(self.get_upnp_domain(), self.get_type(), self.get_version())
		        if (self.host_service) else
		        Service.get_urn(self)
		       )
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

	def get_xml(self):
	#
		"""
Returns the UPnP SCPD.

:return: (str) UPnP SCPD XML
:since:  v0.1.00
		"""

		xml_resource = self._get_xml(self._init_xml_resource())
		return xml_resource.export_cache(True)
	#

	def _get_xml(self, xml_resource):
	#
		"""
Returns the UPnP SCPD.

:param xml_resource: XML resource

:return: (object) UPnP SCPD XML resource
:since:  v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_xml()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		client = Client.load_user_agent(self.client_user_agent)
		if (not client.get("upnp_xml_cdata_encoded", False)): xml_resource.set_cdata_encoding(False)

		attributes = { "xmlns": "urn:schemas-upnp-org:service-1-0" }
		if (self.configid != None): attributes['configId'] = self.configid

		xml_resource.add_node("scpd", attributes = attributes)
		xml_resource.set_cached_node("scpd")

		client = Client.load_user_agent(self.client_user_agent)

		spec_version = (self.get_spec_version()
		                if (client.get("upnp_spec_versioning_supported", True)) else
		                ( 1, 0 )
		               )

		xml_resource.add_node("scpd specVersion major", str(spec_version[0]))
		xml_resource.add_node("scpd specVersion minor", str(spec_version[1]))

		if (len(self.actions) > 0):
		#
			position = 0

			for action_name in self.actions:
			#
				xml_base_path = "scpd actionList action#{0:d}".format(position)
				xml_resource.add_node(xml_base_path)
				xml_resource.set_cached_node(xml_base_path)

				action = self.actions[action_name]
				xml_resource.add_node("{0} name".format(xml_base_path), action_name)

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
					xml_resource.add_node("{0} argumentList argument#{1:d}".format(xml_base_path, position_variable))
					xml_resource.add_node("{0} argumentList argument#{1:d} name".format(xml_base_path, position_variable), variables[position_variable]['name'])
					xml_resource.add_node("{0} argumentList argument#{1:d} direction".format(xml_base_path, position_variable), variables[position_variable]['direction'])
					if ("retval" in variables[position_variable]): xml_resource.add_node("{0} argumentList argument#{1:d} retval".format(xml_base_path, position_variable))
					xml_resource.add_node("{0} argumentList argument#{1:d} relatedStateVariable".format(xml_base_path, position_variable), variables[position_variable]['variable'])
				#

				position += 1
			#

			position_variable = 0
			xml_resource.add_node("scpd serviceStateTable".format(xml_base_path))
			xml_resource.set_cached_node("scpd serviceStateTable".format(xml_base_path))

			for variable_name in self.variables:
			#
				variable = self.variables[variable_name]
				xml_base_path = "scpd serviceStateTable stateVariable#{0:d}".format(position_variable)

				attributes = { }
				if (not variable['is_sending_events']): attributes['sendEvents'] = "no"
				if (variable['is_multicasting_events']): attributes['multicast'] = "yes"

				xml_resource.add_node(xml_base_path, attributes = attributes)

				xml_resource.add_node("{0} name".format(xml_base_path), variable_name)
				xml_resource.add_node("{0} dataType".format(xml_base_path), variable['type'])
				if ("value" in variable): xml_resource.add_node("{0} defaultValue".format(xml_base_path), variable['value'])

				values_allowed_count = (len(variable['values_allowed']) if ("values_allowed" in variable) else 0)
				for position_values_allowed in range(0, values_allowed_count): xml_resource.add_node("{0} allowedValueList allowedValue#{1:d}".format(xml_base_path, position_values_allowed), variable['values_allowed'][position_values_allowed])

				if ("values_min" in variable): xml_resource.add_node("{0} allowedValueRange minimum".format(xml_base_path), variable['values_min'])
				if ("values_max" in variable): xml_resource.add_node("{0} allowedValueRange maximum".format(xml_base_path), variable['values_max'])
				if ("values_stepping" in variable): xml_resource.add_node("{0} allowedValueRange step".format(xml_base_path), variable['values_stepping'])

				position_variable += 1
			#
		#

		return xml_resource
	#

	def _handle_gena_registration(self, sid):
	#
		"""
Handles the registration of an UPnP device at GENA with the given SID.

:param sid: UPnP SID

:since: v0.1.03
		"""

		pass
	#

	def handle_soap_call(self, action, arguments_given = None):
	#
		"""
Executes the given SOAP action.

:param action: SOAP action called
:param arguments_given: SOAP arguments

:return: (list) Result argument list
:since:  v0.1.00
		"""

		# pylint: disable=broad-except,star-args

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_soap_call({1})- (#echo(__LINE__)#)", self, action, context = "pas_upnp")
		_return = UpnpException("pas_http_core_500")

		action_definition = None
		action_method = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", action).lower()
		arguments = { }
		if (arguments_given == None): arguments_given = [ ]
		is_request_valid = (action in self.actions)

		if (is_request_valid):
		#
			action_definition = self.actions[action]

			for argument in action_definition['argument_variables']:
			#
				if (argument['variable'] not in self.variables):
				#
					is_request_valid = False
					_return = UpnpException("pas_http_core_500")

					break
				#
				elif (argument['name'] in arguments_given): argument_given = arguments_given[argument['name']]
				elif ("value" in self.variables[argument['variable']]): argument_given = self.variables[argument['variable']]['value']
				else:
				#
					is_request_valid = False
					_return = UpnpException("pas_http_core_400", 402)

					break
				#

				if (is_request_valid):
				#
					argument_name = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", argument['name']).lower()
					arguments[argument_name] = Variable.get_native(Variable.get_native_type(self.variables[argument['variable']]), argument_given)
				#
			#
		#
		else: _return = UpnpException("pas_http_core_400", 401)

		result = None

		try:
		#
			if (is_request_valid):
			#
				result = (getattr(self, action_method)(**arguments)
				          if hasattr(self, action_method) else
				          Hook.call_one("dNG.pas.upnp.service.{0}.{1}".format(self.__class__.__name__, action_method), **arguments)
				         )
			#
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception, context = "pas_upnp")
			_return = UpnpException("pas_http_core_500")
		#

		if (isinstance(result, Exception)): _return = result
		elif (result != None):
		#
			return_values = ([ ] if (action_definition['return_variable'] == None) else [ action_definition['return_variable'] ])
			return_values += action_definition['result_variables']

			_return = [ ]
			_type = type(result)

			if (_type != dict and len(return_values) != 1): _return = UpnpException("pas_http_core_500")
			else:
			#
				for return_value in return_values:
				#
					return_value_name = AbstractService.RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", return_value['name']).lower()

					if (_type == dict): result_value = (result[return_value_name] if (return_value_name in result) else None)
					else: result_value = result

					if (return_value['variable'] not in self.variables or result_value == None):
					#
						_return = UpnpException("pas_http_core_500")
						break
					#
					else: _return.append({ "name": return_value['name'], "value": Variable.get_upnp_value(self.variables[return_value['variable']], result_value) })
				#
			#
		#

		return _return
	#

	def init_host(self, device, service_id, configid = None):
	#
		"""
Initializes a host service.

:param device: Host device this UPnP service is added to
:param service_id: Unique UPnP service ID
:param configid: UPnP configId for the host device

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.configid = configid
		self.host_service = True
		self.service_id = service_id
		self.udn = device.get_udn()

		self.url_base = "{0}{1}/".format(device.get_url_base(), Link.encode_query_value(service_id))
		self.url_control = "{0}control".format(self.url_base)
		self.url_event_control = "{0}eventsub".format(self.url_base)
		self.url_scpd = "{0}xml".format(self.url_base)

		self._init_host_actions(device)
		self._init_host_variables(device)

		Hook.call("dNG.pas.upnp.Service.initHost", device = device, service = self)
		Hook.register_weakref("dNG.pas.upnp.Gena.onRegistered", self._on_gena_registration)

		return ((len(self.actions) + len(self.variables)) > 0)
	#

	def _init_host_actions(self, device):
	#
		"""
Initializes the dict of host service actions.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		self.actions = { }
	#

	def _init_host_variables(self, device):
	#
		"""
Initializes the dict of host service variables.

:param device: Host device this UPnP service is added to

:since: v0.1.00
		"""

		self.variables = { }
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

	def _on_gena_registration(self, params, last_return = None):
	#
		"""
Called after an UPnP device registered for GENA.

:return: (mixed) Return value
:since:  v0.1.03
		"""

		if (self.host_service
		    and params.get("usn") == self.get_usn()
		    and "sid" in params
		   ): self._handle_gena_registration(params['sid'])

		return last_return
	#

	def remove_host_action(self, action):
	#
		"""
Removes the given host service action.

:param action: SOAP action

:since: v0.1.00
		"""

		if (action in self.actions): del(self.actions[action])
	#

	def remove_host_variable(self, name, definition):
	#
		"""
Removes the given host service variable.

:param name: Variable name

:since: v0.1.00
		"""

		if (name in self.variables): del(self.variables[name])
	#

	def set_client_user_agent(self, user_agent):
	#
		"""
Sets the UPnP client user agent.

:param user_agent: Client user agent

:since: v0.1.00
		"""

		self.client_user_agent = user_agent
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