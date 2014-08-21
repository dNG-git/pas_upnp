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

from platform import uname
import re

from dNG.data.xml_resource import XmlResource
from dNG.net.http.client import Client as HttpClient
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.thread_lock import ThreadLock
from dNG.pas.runtime.value_exception import ValueException
from .service import Service

class Device(object):
#
	"""
The UPnP Basic:1 device implementation.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	RE_USN_URN = re.compile("^urn:(.+):(.+):(.*):(.*)$", re.I)
	"""
URN RegExp
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Device)

:since: v0.1.00
		"""

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
		self.identifier = None
		"""
Parsed UPnP identifier
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
		self.scpds = { }
		"""
Received Service Control Protocol Definitions
		"""
		self.services = { }
		"""
UPnP services
		"""
		self.spec_major = None
		"""
UPnP specVersion major number
		"""
		self.spec_minor = None
		"""
UPnP specVersion minor number
		"""
		self._lock = ThreadLock()
		"""
Thread safety lock
		"""
		self.url_base = None
		"""
HTTP base URL
		"""
	#

	def add_embedded_device(self, device):
	#
		"""
Add the given device to the list of embedded devices.

:param device: UPnP device

:since: v0.1.00
		"""

		if (not isinstance(device, Device)): raise ValueException("Given object is not a supported UPnP device")
		self.embedded_devices[device.get_udn().lower()] = device
	#

	def add_service(self, service):
	#
		"""
Add the given service to the list of services.

:param service: UPnP service

:since: v0.1.00
		"""

		if (not isinstance(service, Service)): raise ValueException("Given object is not a supported UPnP service")
		self.services[service.get_service_id().lower()] = service
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

	def get_device_model(self):
	#
		"""
Returns the UPnP modelName value.

:return: (str) Model name; None if not set
:since:  v0.1.00
		"""

		return self.device_model
	#

	def get_device_model_desc(self):
	#
		"""
Returns the UPnP modelDescription value.

:return: (str) Model description; None if not set
:since:  v0.1.00
		"""

		return self.device_model_desc
	#

	def get_device_model_upc(self):
	#
		"""
Returns the UPnP UPC value.

:return: (str) UPC code; None if not set
:since:  v0.1.00
		"""

		return self.device_model_upc
	#

	def get_device_model_url(self):
	#
		"""
Returns the UPnP modelURL value.

:return: (str) Device model URL; None if not set
:since:  v0.1.00
		"""

		return self.device_model_url
	#

	def get_device_model_version(self):
	#
		"""
Returns the UPnP modelNumber value.

:return: (str) Device model version; None if not set
:since:  v0.1.00
		"""

		return self.device_model_version
	#

	def get_device_serial_number(self):
	#
		"""
Returns the UPnP serialNumber value.

:return: (str) Device serial number; None if not set
:since:  v0.1.00
		"""

		return self.device_serial_number
	#

	def get_embedded_device(self, uuid):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.00
		"""

		_return = None

		uuid = uuid.lower()

		if (uuid in self.embedded_devices): _return = self.embedded_devices[uuid]
		else:
		#
			for device in self.embedded_devices:
			#
				_return = self.embedded_devices[device].get_embedded_device(uuid)
				if (_return != None): break
			#
		#

		if (_return != None and _return.is_managed()): _return.set_configid(self.configid)

		return _return
	#

	def get_embedded_device_uuids(self):
	#
		"""
Returns a list of embedded device UUIDs.

:return: (object) Embedded device UUIDs
:since:  v0.1.00
		"""

		return self.embedded_devices.keys()
	#

	def get_manufacturer(self):
	#
		"""
Returns the UPnP manufacturer value.

:return: (str) Manufacturer
:since:  v0.1.00
		"""

		return self.manufacturer
	#

	def get_manufacturer_url(self):
	#
		"""
Returns the UPnP manufacturerURL value.

:return: (str) Manufacturer URL; None if not set
:since:  v0.1.00
		"""

		return self.manufacturer_url
	#

	def get_name(self):
	#
		"""
Returns the UPnP friendlyName value.

:return: (str) Network name
:since:  v0.1.00
		"""

		return self.name
	#

	def get_presentation_url(self):
	#
		"""
Returns the UPnP presentationURL value.

:return: (str) Presentation URL; None if not set
:since:  v0.1.00
		"""

		return self.presentation_url
	#

	def get_service(self, _id):
	#
		"""
Returns a UPnP service for the given UPnP service ID.

:param _id: UPnP serviceId value

:return: (object) UPnP service; None if unknown
:since:  v0.1.00
		"""

		_return = None

		_id = _id.lower()

		if (_id in self.services):
		#
			_return = self.services[_id]

			if (not _return.is_initialized()):
			#
				with self._lock:
				#
					scpd_url = _return.get_url_scpd()

					if (scpd_url not in self.scpds):
					#
						os_uname = uname()

						http_client = HttpClient(scpd_url, event_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False))
						http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
						http_client.set_ipv6_link_local_interface(Settings.get("pas_global_ipv6_link_local_interface"))
						http_response = http_client.request_get()

						if (http_response.is_readable()): self.scpds[scpd_url] = Binary.str(http_response['body'])
					#

					if (scpd_url in self.scpds):
					#
						_return.init_xml_scpd(self.scpds[scpd_url])
						if (_return.is_managed()): _return.set_configid(self.configid)
					#
				#
			#
		#

		return _return
	#

	def get_service_ids(self):
	#
		"""
Returns a list of all UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.1.00
		"""

		return self.services.keys()
	#

	def get_unique_service_type_ids(self):
	#
		"""
Returns a list of unique (serviceType differs) UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.1.00
		"""

		_return = { }

		for service_id in self.services:
		#
			urn = self.services[service_id].get_service_id_urn()
			if (self.get_type() == self.services[service_id].get_service_id() or urn not in _return): _return[urn] = service_id
		#

		return self.services.keys()
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
Returns the UPnP device type.

:return: (str) Device type
:since:  v0.1.00
		"""

		return self.identifier['type']
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

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP device UDN
:since:  v0.1.00
		"""

		return self.identifier['uuid']
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP device specification domain.

:return: (str) UPnP device specification domain
:since:  v0.1.00
		"""

		return self.identifier['domain']
	#

	def get_urn(self):
	#
		"""
Returns the UPnP deviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return self.identifier['urn']
	#

	def get_version(self):
	#
		"""
Returns the UPnP device type version.

:return: (str) Device type version; None if undefined
:since:  v0.1.00
		"""

		return (self.identifier['version'] if ("urn" in self.identifier) else None)
	#

	def _init_device_xml_tree(self, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		xml_resource = self._init_xml_resource()

		if (xml_resource.set(xml_tree, True) != False and xml_resource.count_node("upnp:device") > 0): xml_resource.set_cached_node("upnp:device")
		else: _return = False

		if (_return):
		#
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
	#
		"""
Initialize the list of embedded devices from a UPnP description.

:param identifier: Parsed UPnP identifier
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		xml_resource = self._init_xml_resource()

		if (xml_resource.set(xml_tree, True) != False and xml_resource.count_node("upnp:deviceList") > 0): xml_resource.set_cached_node("upnp:deviceList")
		else: _return = False

		devices_count = xml_resource.count_node("upnp:deviceList upnp:device")

		if (devices_count > 0):
		#
			for position in range(0, devices_count):
			#
				usn = xml_resource.get_node_value("upnp:deviceList upnp:device#{0:d} upnp:UDN".format(position))

				if (usn != None):
				#
					value = xml_resource.get_node_value("upnp:deviceList upnp:device#{0:d} upnp:deviceType".format(position))
					usn = (None if (value == None) else "{0}::{1}".format(usn, value))
				#

				if (usn != None):
				#
					embedded_identifier = Device.get_identifier(usn, identifier['bootid'], identifier['configid'])

					embedded_device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.{0}".format(embedded_identifier['type']), False)
					if (embedded_device == None): embedded_device = Device()

					embedded_xml_data = { "device": xml_resource.get_node("upnp:deviceList upnp:device#{0:d}".format(position), False) }
					if (embedded_device.init_embedded_device_xml_tree(embedded_identifier, self.url_base, embedded_xml_data)): self.add_embedded_device(embedded_device)
				#
			#
		#

		return _return
	#

	def init_embedded_device_xml_tree(self, identifier, url_base, xml_tree):
	#
		"""
Initialize the embedded device from a UPnP description.

:param identifier: Parsed UPnP identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		xml_resource = self._init_xml_resource()

		if (xml_resource.set(xml_tree, True) != False and xml_resource.count_node("upnp:device") > 0): xml_resource.set_cached_node("upnp:device")
		else: _return = False

		if (_return):
		#
			value = xml_resource.get_node_value("upnp:device upnp:deviceType")
			if (value == None or identifier['urn'] != value[4:]): _return = False
		#

		if (_return):
		#
			value = xml_resource.get_node_value("upnp:device upnp:UDN")
			if (value == None or identifier['uuid'] != value[5:]): _return = False
		#

		if (_return): _return = self._init_device_xml_tree(xml_tree)

		if (_return and xml_resource.count_node("upnp:device upnp:deviceList upnp:device") > 0):
		#
			xml_data = { "deviceList": xml_resource.get_node("upnp:device upnp:deviceList", False) }
			_return = self._init_embedded_device_list_xml_tree(identifier, xml_data)
		#

		if (_return):
		#
			self.identifier = identifier
			self.url_base = url_base

			xml_node = xml_resource.get_node("upnp:device upnp:serviceList", False)
			if (xml_node != None and "xml.item" in xml_node): _return = self._init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
		#

		return _return
	#

	def _init_services_xml_tree(self, xml_tree):
	#
		"""
Initialize the list of services from a UPnP description.

:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		_return = True

		xml_resource = self._init_xml_resource()

		if (xml_resource.set(xml_tree, True) != False and xml_resource.count_node("upnp:serviceList") > 0): xml_resource.set_cached_node("upnp:serviceList")
		else: _return = False

		services_count = (xml_resource.count_node("upnp:serviceList upnp:service") if (_return) else 0)

		if (services_count > 0):
		#
			xml_resource.set_cached_node("upnp:serviceList")

			for position in range(0, services_count):
			#
				service = Service()
				xml_node = xml_resource.get_node("upnp:serviceList upnp:service#{0:d}".format(position), False)
				if (xml_node != None and "xml.item" in xml_node and service.init_metadata_xml_tree(self.identifier, self.url_base, { xml_node['xml.item']['tag']: xml_node })): self.add_service(service)
			#
		#

		return _return
	#

	def init_xml_desc(self, usn_data, xml_data):
	#
		"""
Initialize the device structure from a UPnP description.

:param usn_data: Received USN data
:param xml_data: Received UPnP description

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		# pylint: disable=broad-except

		_return = True

		try:
		#
			xml_resource = self._init_xml_resource()

			if (xml_resource.xml_to_dict(xml_data) == None or xml_resource.count_node("upnp:root") < 1): _return = False
			else: xml_resource.set_cached_node("upnp:root")

			if (_return):
			#
				xml_node_attributes = xml_resource.get_node_attributes("upnp:root")

				if ("configid" in xml_node_attributes):
				#
					if (usn_data['configid'] == xml_node_attributes['configid']): self.configid = usn_data['configid']
					else: _return = False
				#
			#

			if (_return and usn_data['class'] == "rootdevice"):
			#
				if (xml_resource.count_node("upnp:root upnp:device") < 1): _return = False
				elif ("urn" in usn_data):
				#
					value = xml_resource.get_node_value("upnp:root upnp:device upnp:deviceType")
					if (value == None or usn_data['urn'] != value[4:]): _return = False
				#
			#

			if (_return and usn_data['class'] == "rootdevice"):
			#
				value = xml_resource.get_node_value("upnp:root upnp:device upnp:UDN")
				if (value == None or usn_data['uuid'] != value[5:]): _return = False
			#

			if (_return):
			#
				self.spec_major = int(xml_resource.get_node_value("upnp:root upnp:specVersion upnp:major"))
				self.spec_minor = int(xml_resource.get_node_value("upnp:root upnp:specVersion upnp:minor"))

				value = xml_resource.get_node_value("upnp:root upnp:URLBase")
				self.url_base = (usn_data['url_base'] if (value == None) else value)

				xml_data = { "device": xml_resource.get_node("upnp:root upnp:device", False) }
				_return = self._init_device_xml_tree(xml_data)
			#

			if (_return and xml_resource.count_node("upnp:root upnp:device upnp:deviceList upnp:device") > 0):
			#
				xml_data = { "deviceList": xml_resource.get_node("upnp:root upnp:device upnp:deviceList", False) }
				_return = self._init_embedded_device_list_xml_tree(usn_data, xml_data)
			#
		#
		except Exception as handled_exception:
		#
			LogLine.error(handled_exception, context = "pas_upnp")
			_return = False
		#

		if (_return):
		#
			self.identifier = Device.get_identifier(usn_data['usn'], usn_data['bootid'], usn_data['configid'])

			xml_node = xml_resource.get_node("upnp:root upnp:device upnp:serviceList", False)
			if (xml_node != None and "xml.item" in xml_node): _return = self._init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
		#

		return _return
	#

	def _init_xml_resource(self):
	#
		"""
Returns a XML parser with predefined XML namespaces.

:return: (object) XML parser
:since:  v0.1.00
		"""

		_return = XmlResource()
		_return.register_ns("dlna", "urn:schemas-dlna-org:device-1-0")
		_return.register_ns("upnp", "urn:schemas-upnp-org:device-1-0")
		return _return
	#

	def is_managed(self):
	#
		"""
True if the host manages the device.

:return: (bool) False if remote UPnP device
:since:  v0.1.00
		"""

		return False
	#

	def remove_embedded_device(self, device):
	#
		"""
Remove the given device from the list of embedded devices.

:param device: UPnP device

:since: v0.1.00
		"""

		if (not isinstance(device, Device)): raise ValueException("Given object is not a supported UPnP device")

		device = device.get_udn().lower()
		if (device in self.embedded_devices): del(self.embedded_devices[device])
	#

	def remove_service(self, service):
	#
		"""
Remove the given service from the list of services.

:param service: UPnP service

:since: v0.1.00
		"""

		if (not isinstance(service, Service)): raise ValueException("Given object is not a supported UPnP service")

		service = service.get_service_id().lower()
		if (service in self.services): del(self.services[service])
	#

	@staticmethod
	def get_identifier(usn, bootid = None, configid = None):
	#
		"""
Parses the given USN string.

:param usn: UPnP USN
:param bootid: UPnP bootid (bootid.upnp.org) if any
:param configid: UPnP configid (configid.upnp.org) if any

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		usn = Binary.str(usn)

		if (type(usn) == str):
		#
			usn_data = usn.split("::", 1)
			device_id = usn_data[0].lower().replace("-", "")
		#
		else: device_id = ""

		if (device_id.startswith("uuid:")):
		#
			device_id = device_id[5:]
			_return = { "device": device_id, "bootid": None, "configid": None, "uuid": usn_data[0][5:], "class": "unknown", "managed": False, "usn": usn }

			if (bootid != None and configid != None):
			#
				_return['bootid'] = bootid
				_return['configid'] = configid
			#

			re_result = (Device.RE_USN_URN.match(usn_data[1]) if (len(usn_data) > 1) else None)

			if (re_result != None):
			#
				_return['urn'] = usn_data[1][4:]

				_return['domain'] = re_result.group(1)
				_return['class'] = re_result.group(2)
				_return['type'] = re_result.group(3)
				_return['version'] = re_result.group(4)
			#
			elif (usn[-17:].lower() == "::upnp:rootdevice"): _return['class'] = "rootdevice"
		#
		else: _return = None

		return _return
	#
#

##j## EOF