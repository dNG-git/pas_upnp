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

# pylint: disable=import-error,no-name-in-module

from collections import OrderedDict
from platform import uname
import re

try: from urllib.parse import urljoin
except ImportError: from urlparse import urljoin

from dNG.data.binary import Binary
from dNG.data.xml_resource import XmlResource
from dNG.module.named_loader import NamedLoader
from dNG.net.http.client import Client as HttpClient
from dNG.runtime.value_exception import ValueException

from .identifier_mixin import IdentifierMixin
from .service_proxy import ServiceProxy
from .spec_mixin import SpecMixin
from .variable import Variable

class Service(IdentifierMixin, SpecMixin):
    """
The UPnP common service implementation.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
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

    def __init__(self):
        """
Constructor __init__(Service)

:since: v0.2.00
        """

        IdentifierMixin.__init__(self)
        SpecMixin.__init__(self)

        self.actions = None
        """
Service actions defined in the SCPD
        """
        self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
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

    def get_definition_variable(self, name):
        """
Returns the UPnP variable definition.

:param name: Variable name

:return: (dict) Variable definition
:since:  v0.2.00
        """

        if (self.variables is None or name not in self.variables): raise ValueException("'{0}' is not a defined SCPD variable".format(name))
        return self.variables[name]
    #

    def get_name(self):
        """
Returns the UPnP service name (URN without version).

:return: (str) Service name
:since:  v0.2.00
        """

        return self.name
    #

    def get_proxy(self):
        """
Returns a callable proxy object for UPnP actions and variables.

:return: (ServiceProxy) UPnP proxy
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_proxy()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (not self.is_initialized()): self.init_scpd()
        return ServiceProxy(self, self.actions, self.variables)
    #

    def get_service_id(self):
        """
Returns the UPnP serviceId value.

:return: (str) UPnP serviceId value
:since:  v0.2.00
        """

        return self.service_id['id']
    #

    def get_service_id_urn(self):
        """
Returns the UPnP serviceId value.

:return: (str) UPnP serviceId URN
:since:  v0.2.00
        """

        return self.service_id['urn']
    #

    def get_url_base(self):
        """
Returns the HTTP base URL.

:return: (str) HTTP base URL
:since:  v0.2.00
        """

        return self.url_base
    #

    def get_url_control(self):
        """
Returns the UPnP controlURL value.

:return: (str) SOAP endpoint URL
:since:  v0.2.00
        """

        return self.url_control
    #

    def get_url_event_control(self):
        """
Returns the UPnP eventSubURL value.

:return: (str) Event subscription endpoint; None if not set
:since:  v0.2.00
        """

        return self.url_event_control
    #

    def get_url_scpd(self):
        """
Returns the UPnP SCPDURL value.

:return: (str) SCPDURL value
:since:  v0.2.00
        """

        return self.url_scpd
    #

    def init_metadata_xml_tree(self, device_identifier, url_base, xml_resource):
        """
Initialize the service metadata from a UPnP description.

:param device_identifier: Parsed UPnP device identifier
:param url_base: HTTP base URL
:param xml_resource: UPnP description XML parser instance

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = True

        if (xml_resource.count_node("upnp:service") > 0): xml_resource.set_cached_node("upnp:service")
        else: _return = False

        if (_return):
            value = xml_resource.get_node_value("upnp:service upnp:serviceType")
            re_result = (None if (value is None) else Service.RE_USN_URN.match(value))

            if (re_result is None or re_result.group(2) != "service"): _return = False
            else:
                self.name = "{0}:service:{1}".format(re_result.group(1), re_result.group(3))
                urn = "{0}:{1}".format(self.name, re_result.group(4))

                self._set_identifier({ "device": device_identifier['device'],
                                       "bootid": device_identifier['bootid'],
                                       "configid": device_identifier['configid'],
                                       "uuid": device_identifier['uuid'],
                                       "class": "service",
                                       "usn": "uuid:{0}::{1}".format(device_identifier['uuid'], value),
                                       "urn": urn,
                                       "domain": re_result.group(1),
                                       "type": re_result.group(3),
                                       "version": re_result.group(4)
                                     })
            #
        #

        if (_return):
            value = xml_resource.get_node_value("upnp:service upnp:serviceId")
            re_result = (None if (value is None) else Service.RE_SERVICE_ID_URN.match(value))

            if (re_result is None or re_result.group(2) != "serviceId"): _return = False
            else: self.service_id = { "urn": value[4:], "domain": re_result.group(1), "id": re_result.group(3) }
        #

        if (_return):
            self.url_scpd = Binary.str(urljoin(url_base, xml_resource.get_node_value("upnp:service upnp:SCPDURL")))
            self.url_control = Binary.str(urljoin(url_base, xml_resource.get_node_value("upnp:service upnp:controlURL")))

            value = xml_resource.get_node_value("upnp:service upnp:eventSubURL")
            self.url_event_control = (None if (value.strip == "") else Binary.str(urljoin(url_base, value)))
        #

        return _return
    #

    def init_scpd(self):
        """
Initialize actions from the SCPD URL.

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = False

        os_uname = uname()

        http_client = HttpClient(self.url_scpd, event_handler = self.log_handler)
        http_client.set_header("User-Agent", "{0}/{1} UPnP/2.0 pas.upnp/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
        http_response = http_client.request_get()

        if (http_response.is_readable()): _return = self.init_xml_scpd(Binary.str(http_response.read()))
        elif (self.log_handler is not None): self.log_handler.error(http_response.get_error_message(), context = "pas_upnp")

        return _return
    #

    def _init_xml_resource(self):
        """
Returns a XML parser with predefined XML namespaces.

:return: (object) XML parser
:since:  v0.2.00
        """

        _return = XmlResource(node_type = OrderedDict)
        _return.register_ns("scpd", "urn:schemas-upnp-org:service-1-0")
        return _return
    #

    def init_xml_scpd(self, xml_data):
        """
Initialize the list of service actions from a UPnP SCPD description.

:param xml_data: Received UPnP SCPD

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        # pylint: disable=broad-except

        _return = True

        try:
            self.actions = None
            self.variables = None

            xml_resource = self._init_xml_resource()

            if (xml_resource.xml_to_dict(xml_data) is None or xml_resource.count_node("scpd:scpd") < 1): _return = False
            else: xml_resource.set_cached_node("scpd:scpd")

            if (_return):
                spec_version = ( xml_resource.get_node_value("scpd:scpd scpd:specVersion scpd:major"),
                                 xml_resource.get_node_value("scpd:scpd scpd:specVersion scpd:minor")
                               )

                self._set_spec_version(spec_version)
            #

            variables_count = (xml_resource.count_node("scpd:scpd scpd:serviceStateTable scpd:stateVariable") if (_return) else 0)

            if (variables_count > 0):
                self.variables = { }
                xml_resource.set_cached_node("scpd:scpd scpd:serviceStateTable")

                for position in range(0, variables_count):
                    multicast_events = False
                    send_events = True
                    xml_base_path = "scpd:scpd scpd:serviceStateTable scpd:stateVariable#{0:d}".format(position)

                    xml_node_attributes = xml_resource.get_node_attributes(xml_base_path)
                    if (xml_node_attributes.get("sendEvents", "").lower() == "no"): send_events = False
                    if (xml_node_attributes.get("multicast", "").lower() == "yes"): multicast_events = True

                    name = xml_resource.get_node_value("{0} scpd:name".format(xml_base_path))

                    xml_node = xml_resource.get_node("{0} scpd:dataType".format(xml_base_path))
                    _type = Variable.get_native_type_from_xml(xml_resource, xml_node)

                    if (_type == False): raise ValueException("Invalid dataType definition found")

                    self.variables[name] = { "is_sending_events": send_events,
                                             "is_multicasting_events": multicast_events,
                                             "type": _type
                                           }

                    value = xml_resource.get_node_value("{0} scpd:defaultValue".format(xml_base_path))
                    if (value is not None): self.variables[name]['value'] = value

                    xml_allowed_value_node_path = "{0} scpd:allowedValueList scpd:allowedValue".format(xml_base_path)
                    allowed_values_count = xml_resource.count_node(xml_allowed_value_node_path)

                    if (allowed_values_count > 0):
                        self.variables[name]['values_allowed'] = [ ]
                        if (_type != str): raise ValueException("SCPD can only contain allowedValue elements if the dataType is set to 'string'")

                        for position_allowed in range(0, allowed_values_count):
                            value = xml_resource.get_node_value("{0}#{1:d}".format(xml_allowed_value_node_path, position_allowed))
                            if (value is not None and value not in self.variables[name]['values_allowed']): self.variables[name]['values_allowed'].append(value)
                        #
                    #

                    xml_allowed_value_range_node_path = "{0} scpd:allowedValueRange".format(xml_base_path)
                    xml_node = xml_resource.get_node(xml_allowed_value_range_node_path)

                    if (xml_node is not None):
                        if (allowed_values_count > 0): raise ValueException("SCPD can only contain one of allowedValueList and allowedValueRange")

                        self.variables[name]['values_min'] = xml_resource.get_node_value("{0} scpd:minimum".format(xml_allowed_value_range_node_path))
                        self.variables[name]['values_max'] = xml_resource.get_node_value("{0} scpd:maximum".format(xml_allowed_value_range_node_path))

                        value = xml_resource.get_node("{0} scpd:allowedValueRange scpd:step".format(xml_base_path))
                        if (value is not None): self.variables[name]['values_stepping'] = value
                    #
                #
            else: _return = False

            actions_count = (xml_resource.count_node("scpd:scpd scpd:actionList scpd:action") if (_return) else 0)

            if (actions_count > 0):
                self.actions = { }
                xml_resource.set_cached_node("scpd:scpd scpd:actionList")

                for position in range(0, actions_count):
                    xml_base_path = "scpd:scpd scpd:actionList scpd:action#{0:d}".format(position)
                    name = xml_resource.get_node_value("{0} scpd:name".format(xml_base_path))

                    action_arguments_count = xml_resource.count_node("{0} scpd:argumentList scpd:argument".format(xml_base_path))
                    self.actions[name] = { "argument_variables": [ ], "return_variable": None, "result_variables": [ ] }

                    if (action_arguments_count > 0):
                        for position_argument in range(0, action_arguments_count):
                            xml_argument_node_path = "{0} scpd:argumentList scpd:argument#{1:d}".format(xml_base_path, position_argument)

                            argument_name = xml_resource.get_node_value("{0} scpd:name".format(xml_argument_node_path))

                            value = xml_resource.get_node_value("{0} scpd:direction".format(xml_argument_node_path))
                            argument_type = ("argument_variables" if (value.strip().lower() == "in") else "result_variables")

                            value = xml_resource.get_node_value("{0} scpd:retval".format(xml_argument_node_path))
                            if (argument_type == "result_variables" and value is not None): argument_type = "return_variable"

                            value = xml_resource.get_node_value("{0} scpd:relatedStateVariable".format(xml_argument_node_path))

                            if (value not in self.variables): raise ValueException("SCPD can only contain arguments defined as an stateVariable")

                            if (argument_type == "return_variable"): self.actions[name]['return_variable'] = { "name": argument_name, "variable": value }
                            else: self.actions[name][argument_type].append({ "name": argument_name, "variable": value })
                        #
                    #
                #
            #
        except Exception as handled_exception:
            if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_upnp")
            _return = False
        #

        return _return
    #

    def is_action_supported(self, action_method):
        """
Returns true if the given UPnP action method is supported.

:param action_method: UPnP action method

:return: (bool) True if supported
:since:  v0.2.00
        """

        if (not self.is_initialized()): self.init_scpd()
        return (self.actions is not None and action_method in self.actions)
    #

    def is_initialized(self):
        """
Returns true if this service has been initialized.

:return: (bool) True if already initialized
:since:  v0.2.00
        """

        return (self.actions is not None or self.variables is not None)
    #

    def is_managed(self):
        """
True if the host manages the service.

:return: (bool) False if remote UPnP service
:since:  v0.2.00
        """

        return False
    #

    def request_soap_action(self, action, arguments):
        """
Request the given SOAP action with the given arguments from a remote UPnP
device.

:param action: SOAP action
:param arguments: SOAP action arguments

:return: (dict) SOAP action response
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.request_soap_action({1})- (#echo(__LINE__)#)", self, action, context = "pas_upnp")

        _return = None

        os_uname = uname()
        urn = "urn:{0}".format(self.get_urn())

        xml_resource = self._init_xml_resource()
        xml_resource.register_ns("s", "http://schemas.xmlsoap.org/soap/envelope/")
        xml_resource.register_ns("u", urn)
        xml_resource.set_parse_only(False)

        xml_resource.add_node("s:Envelope", attributes = { "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/", "encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })
        xml_resource.add_node("s:Envelope s:Body")

        xml_base_path = "s:Envelope s:Body u:{0}".format(action)

        xml_resource.add_node(xml_base_path, attributes = { "xmlns:u": urn })
        xml_resource.set_cached_node("s:Envelope s:Body")

        for argument in arguments: xml_resource.add_node("{0} {1}".format(xml_base_path, argument['name']), argument['value'])

        http_client = HttpClient(self.url_control, event_handler = self.log_handler)
        http_client.set_header("Content-Type", "text/xml; charset=UTF-8")
        http_client.set_header("SoapAction", "\"{0}#{1}\"".format(urn, action))
        http_client.set_header("User-Agent", "{0}/{1} UPnP/2.0 pas.upnp/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))

        post_data = "<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_resource.export_cache(True))
        http_response = http_client.request_post(post_data)
        xml_response_variables = None

        if (http_response.is_readable()):
            xml_resource.parse(Binary.str(http_response.read()))
            xml_response_variables = xml_resource.get_node("{0}Response".format(xml_base_path))
        elif (self.log_handler is not None): self.log_handler.error(http_response.get_error_message(), context = "pas_upnp")

        if (xml_response_variables is not None):
            _return = { }

            for key in xml_response_variables:
                _return[key] = xml_response_variables[key]['value']
            #
        #

        return _return
    #
#
