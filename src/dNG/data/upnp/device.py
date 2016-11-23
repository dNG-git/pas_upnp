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

from dNG.data.logging.log_line import LogLine
from dNG.data.xml_resource import XmlResource
from dNG.module.named_loader import NamedLoader
from dNG.runtime.io_exception import IOException
from dNG.runtime.value_exception import ValueException

from .identifier_mixin import IdentifierMixin
from .service import Service
from .spec_mixin import SpecMixin

class Device(IdentifierMixin, SpecMixin):
    """
The UPnP Basic:1 device implementation.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(Device)

:since: v0.2.00
        """

        IdentifierMixin.__init__(self)
        SpecMixin.__init__(self)

        self.configid = None
        """
UPnP configId value
        """
        self.device_model = None
        """
UPnP modelName value
        """
        self.device_model_desc = None
        """
UPnP modelDescription value
        """
        self.device_model_upc = None
        """
UPnP UPC value
        """
        self.device_model_url = None
        """
UPnP modelURL value
        """
        self.device_model_version = None
        """
UPnP serialNumber value
        """
        self.device_serial_number = None
        """
UPnP modelNumber value
        """
        self.embedded_devices = { }
        """
UPnP embedded devices
        """
        self.manufacturer = None
        """
UPnP manufacturer value
        """
        self.manufacturer_url = None
        """
UPnP manufacturerURL value
        """
        self.name = None
        """
UPnP friendlyName value
        """
        self.presentation_url = None
        """
UPnP presentationURL value
        """
        self.services = { }
        """
UPnP services
        """
        self.url_base = None
        """
HTTP base URL
        """
    #

    def add_embedded_device(self, device):
        """
Add the given device to the list of embedded devices.

:param device: UPnP device

:since: v0.2.00
        """

        if (not isinstance(device, Device)): raise ValueException("Given object is not a supported UPnP device")
        self.embedded_devices[device.get_udn().lower()] = device
    #

    def add_service(self, service):
        """
Add the given service to the list of services.

:param service: UPnP service

:since: v0.2.00
        """

        if (not isinstance(service, Service)): raise ValueException("Given object is not a supported UPnP service")
        self.services[service.get_service_id().lower()] = service
    #

    def get_configid(self):
        """
Returns the UPnP configId value.

:return: (int) UPnP configId
:since:  v0.2.00
        """

        return self.configid
    #

    def get_device_model(self):
        """
Returns the UPnP modelName value.

:return: (str) Model name; None if not set
:since:  v0.2.00
        """

        return self.device_model
    #

    def get_device_model_desc(self):
        """
Returns the UPnP modelDescription value.

:return: (str) Model description; None if not set
:since:  v0.2.00
        """

        return self.device_model_desc
    #

    def get_device_model_upc(self):
        """
Returns the UPnP UPC value.

:return: (str) UPC code; None if not set
:since:  v0.2.00
        """

        return self.device_model_upc
    #

    def get_device_model_url(self):
        """
Returns the UPnP modelURL value.

:return: (str) Device model URL; None if not set
:since:  v0.2.00
        """

        return self.device_model_url
    #

    def get_device_model_version(self):
        """
Returns the UPnP modelNumber value.

:return: (str) Device model version; None if not set
:since:  v0.2.00
        """

        return self.device_model_version
    #

    def get_device_serial_number(self):
        """
Returns the UPnP serialNumber value.

:return: (str) Device serial number; None if not set
:since:  v0.2.00
        """

        return self.device_serial_number
    #

    def get_embedded_device(self, uuid):
        """
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.2.00
        """

        _return = None

        uuid = uuid.lower()

        if (uuid in self.embedded_devices): _return = self.embedded_devices[uuid]
        else:
            for device in self.embedded_devices:
                _return = self.embedded_devices[device].get_embedded_device(uuid)
                if (_return is not None): break
            #
        #

        if (_return is not None and _return.is_managed()): _return.set_configid(self.configid)

        return _return
    #

    def get_embedded_device_uuids(self):
        """
Returns a list of embedded device UUIDs.

:return: (object) Embedded device UUIDs
:since:  v0.2.00
        """

        return self.embedded_devices.keys()
    #

    def get_manufacturer(self):
        """
Returns the UPnP manufacturer value.

:return: (str) Manufacturer
:since:  v0.2.00
        """

        return self.manufacturer
    #

    def get_manufacturer_url(self):
        """
Returns the UPnP manufacturerURL value.

:return: (str) Manufacturer URL; None if not set
:since:  v0.2.00
        """

        return self.manufacturer_url
    #

    def get_name(self):
        """
Returns the UPnP friendlyName value.

:return: (str) Network name
:since:  v0.2.00
        """

        return self.name
    #

    def get_presentation_url(self):
        """
Returns the UPnP presentationURL value.

:return: (str) Presentation URL; None if not set
:since:  v0.2.00
        """

        return self.presentation_url
    #

    def get_service(self, _id):
        """
Returns a UPnP service for the given UPnP service ID.

:param _id: UPnP serviceId value

:return: (object) UPnP service; None if unknown
:since:  v0.2.00
        """

        _return = None

        _id = _id.lower()

        if (_id in self.services):
            _return = self.services[_id]

            if (not _return.is_initialized()):
                if (not _return.init_scpd()): raise IOException("Failed to initialize service {0}".format(_return.get_service_id_urn()))
                if (_return.is_managed()): _return.set_configid(self.configid)
            #
        #

        return _return
    #

    def get_service_ids(self):
        """
Returns a list of all UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.2.00
        """

        return self.services.keys()
    #

    def get_unique_service_type_ids(self):
        """
Returns a list of unique (serviceType differs) UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.2.00
        """

        _return = { }

        for service_id in self.services:
            urn = self.services[service_id].get_service_id_urn()
            if (self.get_type() == self.services[service_id].get_service_id() or urn not in _return): _return[urn] = service_id
        #

        return self.services.keys()
    #

    def get_url_base(self):
        """
Returns the HTTP base URL.

:return: (str) HTTP base URL
:since:  v0.2.00
        """

        return self.url_base
    #

    def _init_device_xml_tree(self, xml_tree):
        """
Initialize the device from a UPnP description.

:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = True

        xml_resource = self._init_xml_resource()

        if (xml_resource.set(xml_tree, True) != False
            and xml_resource.count_node("upnp:device") > 0
           ): xml_resource.set_cached_node("upnp:device")
        else: _return = False

        if (_return):
            self.name = xml_resource.get_node_value("upnp:device upnp:friendlyName")
            self.manufacturer = xml_resource.get_node_value("upnp:device upnp:manufacturer")
            self.manufacturer_url = xml_resource.get_node_value("upnp:device upnp:manufacturerURL")
            self.device_model_desc = xml_resource.get_node_value("upnp:device upnp:modelDescription")
            self.device_model = xml_resource.get_node_value("upnp:device upnp:modelName")
            self.device_model_version = xml_resource.get_node_value("upnp:device upnp:modelNumber")
            self.device_model_url = xml_resource.get_node_value("upnp:device upnp:modelURL")
            self.device_serial_number = xml_resource.get_node_value("upnp:device upnp:serialNumber")
            self.device_model_upc = xml_resource.get_node_value("upnp:device upnp:UPC")
            self.presentation_url = xml_resource.get_node_value("upnp:device upnp:presentationURL")
        #

        return _return
    #

    def _init_embedded_device_list_xml_tree(self, identifier, xml_tree):
        """
Initialize the list of embedded devices from a UPnP description.

:param identifier: Parsed UPnP identifier
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = True

        xml_resource = self._init_xml_resource()

        if (xml_resource.set(xml_tree, True) != False
            and xml_resource.count_node("upnp:deviceList") > 0
           ): xml_resource.set_cached_node("upnp:deviceList")
        else: _return = False

        devices_count = xml_resource.count_node("upnp:deviceList upnp:device")

        if (devices_count > 0):
            for position in range(0, devices_count):
                usn = xml_resource.get_node_value("upnp:deviceList upnp:device#{0:d} upnp:UDN".format(position))

                if (usn is not None):
                    value = xml_resource.get_node_value("upnp:deviceList upnp:device#{0:d} upnp:deviceType".format(position))
                    usn = (None if (value is None) else "{0}::{1}".format(usn, value))
                #

                if (usn is not None):
                    embedded_identifier = Device.get_identifier(usn, identifier['bootid'], identifier['configid'])

                    embedded_device = NamedLoader.get_instance("dNG.data.upnp.devices.{0}".format(embedded_identifier['type']), False)
                    if (embedded_device is None): embedded_device = Device()

                    embedded_xml_data = { "device": xml_resource.get_node("upnp:deviceList upnp:device#{0:d}".format(position), False) }

                    if (embedded_device.init_embedded_device_xml_tree(embedded_identifier,
                                                                      self.url_base, embedded_xml_data
                                                                     )
                       ): self.add_embedded_device(embedded_device)
                #
            #
        #

        return _return
    #

    def init_embedded_device_xml_tree(self, identifier, url_base, xml_tree):
        """
Initialize the embedded device from a UPnP description.

:param identifier: Parsed UPnP identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = True

        xml_resource = self._init_xml_resource()

        if (xml_resource.set(xml_tree, True) != False
            and xml_resource.count_node("upnp:device") > 0
           ): xml_resource.set_cached_node("upnp:device")
        else: _return = False

        if (_return):
            value = xml_resource.get_node_value("upnp:device upnp:deviceType")
            if (value is None or identifier['urn'] != value[4:]): _return = False
        #

        if (_return):
            value = xml_resource.get_node_value("upnp:device upnp:UDN")
            if (value is None or identifier['uuid'] != value[5:]): _return = False
        #

        if (_return): _return = self._init_device_xml_tree(xml_tree)

        if (_return and xml_resource.count_node("upnp:device upnp:deviceList upnp:device") > 0):
            xml_data = { "deviceList": xml_resource.get_node("upnp:device upnp:deviceList", False) }
            _return = self._init_embedded_device_list_xml_tree(identifier, xml_data)
        #

        if (_return):
            self._set_identifier(identifier)
            self.url_base = url_base

            xml_node = xml_resource.get_node("upnp:device upnp:serviceList", False)

            if (xml_node is not None
                and "xml.item" in xml_node
               ): _return = self._init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
        #

        return _return
    #

    def _init_services_xml_tree(self, xml_tree):
        """
Initialize the list of services from a UPnP description.

:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        _return = True

        xml_resource = self._init_xml_resource()

        if (xml_resource.set(xml_tree, True) != False and xml_resource.count_node("upnp:serviceList") > 0): xml_resource.set_cached_node("upnp:serviceList")
        else: _return = False

        services_count = (xml_resource.count_node("upnp:serviceList upnp:service") if (_return) else 0)

        if (services_count > 0):
            xml_resource.set_cached_node("upnp:serviceList")

            for position in range(0, services_count):
                service = Service()
                xml_node = xml_resource.get_node("upnp:serviceList upnp:service#{0:d}".format(position), False)

                if (xml_node is not None
                    and "xml.item" in xml_node
                   ):
                    service_xml_resource = self._init_xml_resource()

                    if (service_xml_resource.set({ xml_node['xml.item']['tag']: xml_node }, True) != False
                        and service.init_metadata_xml_tree(self._get_identifier(),
                                                           self.url_base,
                                                           service_xml_resource
                                                          )
                       ): self.add_service(service)
                #
            #
        #

        return _return
    #

    def init_xml_desc(self, usn_data, xml_data):
        """
Initialize the device structure from a UPnP description.

:param usn_data: Received USN data
:param xml_data: Received UPnP description

:return: (bool) True if parsed successfully
:since:  v0.2.00
        """

        # pylint: disable=broad-except

        _return = True

        try:
            xml_resource = self._init_xml_resource()

            if (xml_resource.xml_to_dict(xml_data) is None or xml_resource.count_node("upnp:root") < 1): _return = False
            else: xml_resource.set_cached_node("upnp:root")

            if (_return):
                xml_node_attributes = xml_resource.get_node_attributes("upnp:root")

                if ("configid" in xml_node_attributes):
                    if (usn_data['configid'] == xml_node_attributes['configid']): self.configid = usn_data['configid']
                    else: _return = False
                #
            #

            if (_return and usn_data['class'] == "rootdevice"):
                if (xml_resource.count_node("upnp:root upnp:device") < 1): _return = False
                elif ("urn" in usn_data):
                    value = xml_resource.get_node_value("upnp:root upnp:device upnp:deviceType")
                    if (value is None or usn_data['urn'] != value[4:]): _return = False
                #
            #

            if (_return and usn_data['class'] == "rootdevice"):
                value = xml_resource.get_node_value("upnp:root upnp:device upnp:UDN")
                if (value is None or usn_data['uuid'] != value[5:]): _return = False
            #

            if (_return):
                spec_version = ( xml_resource.get_node_value("upnp:root upnp:specVersion upnp:major"),
                                 xml_resource.get_node_value("upnp:root upnp:specVersion upnp:minor")
                               )

                self._set_spec_version(spec_version)

                value = xml_resource.get_node_value("upnp:root upnp:URLBase")
                self.url_base = (usn_data['url_base'] if (value is None) else value)

                xml_data = { "device": xml_resource.get_node("upnp:root upnp:device", False) }
                _return = self._init_device_xml_tree(xml_data)
            #

            if (_return and xml_resource.count_node("upnp:root upnp:device upnp:deviceList upnp:device") > 0):
                xml_data = { "deviceList": xml_resource.get_node("upnp:root upnp:device upnp:deviceList", False) }
                _return = self._init_embedded_device_list_xml_tree(usn_data, xml_data)
            #
        except Exception as handled_exception:
            LogLine.error(handled_exception, context = "pas_upnp")
            _return = False
        #

        if (_return):
            self._set_identifier(Device.get_identifier(usn_data['usn'], usn_data['bootid'], usn_data['configid']))

            xml_node = xml_resource.get_node("upnp:root upnp:device upnp:serviceList", False)
            if (xml_node is not None and "xml.item" in xml_node): _return = self._init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
        #

        return _return
    #

    def _init_xml_resource(self):
        """
Returns a XML parser with predefined XML namespaces.

:return: (object) XML parser
:since:  v0.2.00
        """

        _return = XmlResource()
        _return.register_ns("dlna", "urn:schemas-dlna-org:device-1-0")
        _return.register_ns("upnp", "urn:schemas-upnp-org:device-1-0")
        return _return
    #

    def is_managed(self):
        """
True if the host manages the device.

:return: (bool) False if remote UPnP device
:since:  v0.2.00
        """

        return False
    #

    def remove_embedded_device(self, device):
        """
Remove the given device from the list of embedded devices.

:param device: UPnP device

:since: v0.2.00
        """

        if (not isinstance(device, Device)): raise ValueException("Given object is not a supported UPnP device")

        device = device.get_udn().lower()
        if (device in self.embedded_devices): del(self.embedded_devices[device])
    #

    def remove_service(self, service):
        """
Remove the given service from the list of services.

:param service: UPnP service

:since: v0.2.00
        """

        if (not isinstance(service, Service)): raise ValueException("Given object is not a supported UPnP service")

        service = service.get_service_id().lower()
        if (service in self.services): del(self.services[service])
    #
#
