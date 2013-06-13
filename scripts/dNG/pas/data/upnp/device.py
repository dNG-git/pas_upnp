# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.Device
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

from os import uname
from threading import RLock
import re

from dNG.data.xml_writer import XmlWriter
from dNG.data.rfc.http import Http
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.module.named_loader import NamedLoader
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
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
		self.synchronized = RLock()
		"""
Lock used in multi thread environments.
		"""
		self.url_base = None
		"""
HTTP base URL
		"""
	#

	def embedded_device_add(self, device):
	#
		"""
Add the given device to the list of embedded devices.

:param device: UPnP device

:access: protected
:since:  v0.1.00
		"""

		if (isinstance(device, Device)): self.embedded_devices[device.get_udn().lower()] = device
		else: raise TypeError("Given object is not a supported UPnP device")
	#

	def embedded_device_get(self, uuid):
	#
		"""
Returns an embedded device.

:return: (object) Embedded device
:since:  v0.1.00
		"""

		var_return = None

		uuid = uuid.lower()

		if (uuid in self.embedded_devices): var_return = self.embedded_devices[uuid]
		else:
		#
			for device in self.embedded_devices:
			#
				var_return = self.embedded_devices[device].embedded_device_get(uuid)
				if (var_return != None): break
			#
		#

		if (var_return != None and var_return.is_managed()): var_return.set_configid(self.configid)

		return var_return
	#

	def embedded_device_get_uuids(self):
	#
		"""
Returns a list of embedded device UUIDs.

:return: (object) Embedded device UUIDs
:since:  v0.1.00
		"""

		return self.embedded_devices.keys()
	#

	def embedded_device_remove(self, device):
	#
		"""
Remove the given device from the list of embedded devices.

:param device: UPnP device

:access: protected
:since:  v0.1.00
		"""

		if (isinstance(device, Device)):
		#
			device = device.get_udn().lower()
			if (device in self.embedded_devices): del(self.embedded_devices[device])
		#
		else: raise TypeError("Given object is not a supported UPnP device")
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

	def service_add(self, service):
	#
		"""
Add the given service to the list of services.

:param service: UPnP service

:access: protected
:since:  v0.1.00
		"""

		if (isinstance(service, Service)): self.services[service.get_service_id().lower()] = service
		else: raise TypeError("Given object is not a supported UPnP service")
	#

	def service_get(self, id):
	#
		"""
Return a UPnP service for the given UPnP service ID.

:param id: UPnP serviceId value

:return: (object) UPnP service; None if unknown
:since:  v0.1.00
		"""

		var_return = None

		id = id.lower()

		if (id in self.services):
		#
			var_return = self.services[id]

			if (not var_return.is_initialized()):
			#
				with self.synchronized:
				#
					scpd_url = var_return.get_url_scpd()

					if (scpd_url not in self.scpds):
					#
						os_uname = uname()

						http_client = Http(scpd_url, event_handler = self.log_handler)
						http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
						http_client.set_ipv6_link_local_interface(Settings.get("pas_global_ipv6_link_local_interface"))
						http_response = http_client.request_get()

						if (not isinstance(http_response['body'], Exception)): self.scpds[scpd_url] = Binary.str(http_response['body'])
					#

					if (scpd_url in self.scpds):
					#
						var_return.init_xml_scpd(self.scpds[scpd_url])
						if (var_return.is_managed()): var_return.set_configid(self.configid)
					#
				#
			#
		#

		return var_return
	#

	def service_get_ids(self):
	#
		"""
Returns a list of unique (serviceType differs) UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.1.00
		"""

		return self.services.keys()
	#

	def service_get_unique_types(self):
	#
		"""
Returns a list of unique (serviceType differs) UPnP service USNs.

:return: (list) UPnP service USNs
:since:  v0.1.00
		"""

		var_return = { }

		for service_id in self.services:
		#
			urn = self.services[service_id].get_service_id_urn()
			if (self.get_type() == self.services[service_id].get_service_id() or urn not in var_return): var_return[urn] = service_id
		#

		return self.services.keys()
	#

	def service_remove(self, service):
	#
		"""
Remove the given service from the list of services.

:param service: UPnP service

:access: protected
:since:  v0.1.00
		"""

		if (isinstance(service, Service)):
		#
			service = service.get_service_id().lower()
			if (service in self.services): del(self.services[service])
		#
		else: raise TypeError("Given object is not a supported UPnP service")
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

:return: (str) UPnP device UUID
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

	def init_device_xml_tree(self, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param xml_tree: Input tree dict

:access: protected
:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		xml_parser = self.init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:device") > 0): xml_parser.node_set_cache_path("upnp:device")
		else: var_return = False

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:device upnp:friendlyName")
			self.name = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:manufacturer")
			self.manufacturer = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:manufacturerURL")
			if (xml_node != False): self.manufacturer_url = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:modelDescription")
			if (xml_node != False): self.device_model_desc = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:modelName")
			self.device_model = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:modelNumber")
			if (xml_node != False): self.device_model_version = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:modelURL")
			if (xml_node != False): self.device_model_url = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:serialNumber")
			if (xml_node != False): self.device_serial_number = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:UPC")
			if (xml_node != False): self.device_model_upc = xml_node['value']

			xml_node = xml_parser.node_get("upnp:device upnp:presentationURL")
			if (xml_node != False): self.presentation_url = xml_node['value']
		#

		return var_return
	#

	def init_embedded_device_list_xml_tree(self, identifier, url_base, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param identifier: Parsed UPnP identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		xml_parser = self.init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:deviceList") > 0): xml_parser.node_set_cache_path("upnp:deviceList")
		else: var_return = False

		devices_count = xml_parser.node_count("upnp:deviceList upnp:device")

		if (devices_count > 0):
		#
			for position in range(0, devices_count):
			#
				xml_node = xml_parser.node_get("upnp:deviceList upnp:device#{0:d} upnp:UDN".format(position))
				usn = (None if (xml_node == False) else xml_node['value'])

				if (usn != None):
				#
					xml_node = xml_parser.node_get("upnp:deviceList upnp:device#{0:d} upnp:deviceType".format(position))
					usn = ("{0}::{1}".format(usn, xml_node['value']) if (xml_node != False) else None)
				#

				if (usn != None):
				#
					embedded_identifier = Device.get_identifier(usn, identifier['bootid'], identifier['configid'])

					embedded_device = NamedLoader.get_instance("dNG.pas.data.upnp.devices.{0}".format(embedded_identifier['type']), False)
					if (embedded_device == None): embedded_device = Device()

					embedded_xml_data = { "device": xml_parser.node_get("upnp:deviceList upnp:device#{0:d}".format(position), False) }
					if (embedded_device.init_embedded_device_xml_tree(embedded_identifier, self.url_base, embedded_xml_data)): self.embedded_device_add(embedded_device)
				#
			#
		#

		return var_return
	#

	def init_embedded_device_xml_tree(self, identifier, url_base, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param identifier: Parsed UPnP identifier
:param url_base: HTTP base URL
:param xml_tree: Input tree dict

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		xml_parser = self.init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:device") > 0): xml_parser.node_set_cache_path("upnp:device")
		else: var_return = False

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:device upnp:deviceType")
			if (xml_node == False or identifier['urn'] != xml_node['value'][4:]): var_return = False
		#

		if (var_return):
		#
			xml_node = xml_parser.node_get("upnp:device upnp:UDN")
			if (xml_node == False or identifier['uuid'] != xml_node['value'][5:]): var_return = False
		#

		if (var_return): var_return = self.init_device_xml_tree(xml_tree)

		if (var_return and xml_parser.node_count("upnp:device upnp:deviceList upnp:device") > 0):
		#
			xml_data = { "deviceList": xml_parser.node_get("upnp:device upnp:deviceList", False) }
			var_return = self.init_embedded_device_list_xml_tree(identifier, self.url_base, xml_data)
		#

		if (var_return):
		#
			self.identifier = identifier
			self.url_base = url_base

			xml_node = xml_parser.node_get("upnp:device upnp:serviceList", False)
			if (xml_node != False and "xml.item" in xml_node): var_return = self.init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
		#

		return var_return
	#

	def init_services_xml_tree(self, xml_tree):
	#
		"""
Initialize the device from a UPnP description.

:param xml_tree: Input tree dict

:access: protected
:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		xml_parser = self.init_xml_parser()

		if (xml_parser.set(xml_tree, True) != False and xml_parser.node_count("upnp:serviceList") > 0): xml_parser.node_set_cache_path("upnp:serviceList")
		else: var_return = False

		services_count = (xml_parser.node_count("upnp:serviceList upnp:service") if (var_return) else 0)

		if (services_count > 0):
		#
			xml_parser.node_set_cache_path("upnp:serviceList")

			for position in range(0, services_count):
			#
				service = Service()
				xml_node = xml_parser.node_get("upnp:serviceList upnp:service#{0:d}".format(position), False)
				if (xml_node != False and "xml.item" in xml_node and service.init_metadata_xml_tree(self.identifier, self.url_base, { xml_node['xml.item']['tag']: xml_node })): self.service_add(service)
			#
		#

		return var_return
	#

	def init_xml_desc(self, usn_data, xml_data):
	#
		"""
Initialize the device from a UPnP description.

:param usn_data: Received USN data
:param xml_data: Received UPnP description

:return: (bool) True if parsed successfully
:since:  v0.1.00
		"""

		var_return = True

		try:
		#
			xml_parser = self.init_xml_parser()

			if (xml_parser.xml2dict(xml_data) != False and xml_parser.node_count("upnp:root") > 0): xml_parser.node_set_cache_path("upnp:root")
			else: var_return = False

			if (var_return):
			#
				root_xml_item = xml_parser.node_get("upnp:root", False)['xml.item']

				if ("attributes" in root_xml_item and "configid" in root_xml_item['attributes']):
				#
					if (usn_data['configid'] == root_xml_item['attributes']['configid']): self.configid = usn_data['configid']
					else: var_return = False
				#
			#

			if (var_return and usn_data['class'] == "rootdevice"):
			#
				if (xml_parser.node_count("upnp:root upnp:device") < 1): var_return = False
				elif ("urn" in usn_data):
				#
					xml_node = xml_parser.node_get("upnp:root upnp:device upnp:deviceType")
					if (xml_node == False or usn_data['urn'] != xml_node['value'][4:]): var_return = False
				#
			#

			if (var_return and usn_data['class'] == "rootdevice"):
			#
				xml_node = xml_parser.node_get("upnp:root upnp:device upnp:UDN")
				if (xml_node == False or usn_data['uuid'] != xml_node['value'][5:]): var_return = False
			#

			if (var_return):
			#
				xml_node = xml_parser.node_get("upnp:root upnp:specVersion upnp:major")
				self.spec_major = int(xml_node['value'])

				xml_node = xml_parser.node_get("upnp:root upnp:specVersion upnp:minor")
				self.spec_minor = int(xml_node['value'])

				xml_node = xml_parser.node_get("upnp:root upnp:URLBase")

				if (xml_node == False): self.url_base = usn_data['url_base']
				else: self.url_base = xml_node['value']

				xml_data = { "device": xml_parser.node_get("upnp:root upnp:device", False) }
				var_return = self.init_device_xml_tree(xml_data)
			#

			if (var_return and xml_parser.node_count("upnp:root upnp:device upnp:deviceList upnp:device") > 0):
			#
				xml_data = { "deviceList": xml_parser.node_get("upnp:root upnp:device upnp:deviceList", False) }
				var_return = self.init_embedded_device_list_xml_tree(usn_data, self.url_base, xml_data)
			#
		#
		except Exception as handled_exception:
		#
			LogLine.error(handled_exception)
			var_return = False
		#

		if (var_return):
		#
			self.identifier = Device.get_identifier(usn_data['usn'], usn_data['bootid'], usn_data['configid'])

			xml_node = xml_parser.node_get("upnp:root upnp:device upnp:serviceList", False)
			if (xml_node != False and "xml.item" in xml_node): var_return = self.init_services_xml_tree({ xml_node['xml.item']['tag']: xml_node })
		#

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

		var_return = XmlWriter()
		var_return.ns_register("dlna", "urn:schemas-dlna-org:device-1-0")
		var_return.ns_register("upnp", "urn:schemas-upnp-org:device-1-0")
		return var_return
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

	@staticmethod
	def get_identifier(usn, bootid, configid):
	#
		"""
Parses the given USN string.

:param usn: UPnP USN
:param bootid: UPnP bootid (bootid.upnp.org) if any
:param configid: UPnP configid (configid.upnp.org) if any
:param url: UPnP description location

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
			var_return = { "device": device_id, "bootid": None, "configid": None, "uuid": usn_data[0][5:], "class": "unknown", "managed": False, "usn": usn }

			if (bootid != None and configid != None):
			#
				var_return['bootid'] = bootid
				var_return['configid'] = configid
			#

			re_result = (Device.RE_USN_URN.match(usn_data[1]) if (len(usn_data) > 1) else None)

			if (re_result != None):
			#
				var_return['urn'] = usn_data[1][4:]

				var_return['domain'] = re_result.group(1)
				var_return['class'] = re_result.group(2)
				var_return['type'] = re_result.group(3)
				var_return['version'] = re_result.group(4)
			#
			elif (usn[-17:].lower() == "::upnp:rootdevice"): var_return['class'] = "rootdevice"
		#
		else: var_return = None

		return var_return
	#
#

##j## EOF