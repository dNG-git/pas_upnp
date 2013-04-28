# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.upnp.devices.abstract_device
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

from dNG.pas.data.http.links import direct_links
from dNG.pas.data.upnp.device import direct_device
from dNG.pas.data.upnp.services.abstract_service import direct_abstract_service

class direct_abstract_device(direct_device):
#
	"""
An extended, abstract device implementation for server devices.

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
Constructor __init__(direct_abstract_device)

:since: v0.1.00
		"""

		direct_device.__init__(self)

		self.desc_url = None
		"""
UPnP device description URL
		"""
		self.host_device = False
		"""
UPnP device is managed by host
		"""
		self.type = None
		"""
UPnP device type
		"""
		self.udn = None
		"""
UPnP UDN value
		"""
		self.upnp_domain = None
		"""
UPnP device specification domain
		"""
		self.version = None
		"""
UPnP device type version
		"""
	#

	def get_desc_url(self):
	#
		"""
Returns the UPnP device description URL.

:return: (str) Device description URL; None if not managed
:since:  v0.1.00
		"""

		return (self.desc_url if (self.host_device) else None)
	#

	def get_type(self):
	#
		"""
Returns the UPnP device type.

:return: (str) Device type
:since:  v0.1.00
		"""

		return (self.type if (self.host_device) else direct_device.get_type(self))
	#

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP device UUID
:since:  v0.1.00
		"""

		return (self.udn if (self.host_device) else direct_device.get_udn(self))
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP device specification domain.

:return: (str) UPnP device specification domain
:since:  v0.1.00
		"""

		return (self.upnp_domain if (self.host_device) else direct_device.get_upnp_domain(self))
	#

	def get_urn(self):
	#
		"""
Returns the UPnP deviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return ("{0}:device:{1}:{2}".format(self.upnp_domain, self.type, self.version) if (self.host_device) else direct_device.get_urn(self))
	#

	def get_version(self):
	#
		"""
Returns the UPnP device type version.

:return: (str) Device type version; None if undefined
:since:  v0.1.00
		"""

		return (self.version if (self.host_device) else direct_device.get_version(self))
	#

	def get_xml(self, xml_node_path = None, xml_writer = None):
	#
		"""
Returns the UPnP device description.

:return: (str) Device description XML
:since:  v0.1.00
		"""

		xml_writer = self.init_xml_parser()

		attributes = { "xmlns": "urn:schemas-upnp-org:device-1-0", "xmlns:dlna": "urn:schemas-dlna-org:device-1-0" }
		if (self.configid != None): attributes['configId'] = self.configid

		xml_writer.node_add("root", attributes = attributes)
		xml_writer.node_set_cache_path("root")

		spec_version = self.get_spec_version()
		xml_writer.node_add("root specVersion major", "{0:d}".format(spec_version[0]))
		xml_writer.node_add("root specVersion minor", "{0:d}".format(spec_version[1]))

		self.get_xml_walker(xml_writer, "root device")
		return xml_writer.cache_export(True)
	#

	def get_xml_walker(self, xml_writer, xml_base_path):
	#
		"""
Uses the given XML writer instance to add the UPnP device description at the
given XML node path.

:param xml_writer: XML writer instance
:param xml_base_path: Device description XML base path (e.g. "root device")

:since: v0.1.00
		"""

		udn = "uuid:{0}".format(self.get_udn())
		xml_writer.node_add("{0} UDN".format(xml_base_path), udn)
		xml_writer.node_set_cache_path(xml_base_path)

		xml_writer.node_add("{0} deviceType".format(xml_base_path), "urn:{0}".format(self.get_urn()))
		xml_writer.node_add("{0} friendlyName".format(xml_base_path), self.get_name())
		xml_writer.node_add("{0} manufacturer".format(xml_base_path), self.get_manufacturer())

		value = self.get_manufacturer_url()
		if (value != None): xml_writer.node_add("{0} manufacturerURL".format(xml_base_path), value)

		value = self.get_device_model()
		if (value != None): xml_writer.node_add("{0} modelName".format(xml_base_path), value)

		value = self.get_device_model_desc()
		if (value != None): xml_writer.node_add("{0} modelDescription".format(xml_base_path), value)

		value = self.get_device_model_version()
		if (value != None): xml_writer.node_add("{0} modelNumber".format(xml_base_path), value)

		value = self.get_device_model_url()
		if (value != None): xml_writer.node_add("{0} modelURL".format(xml_base_path), value)

		value = self.get_device_model_upc()
		if (value != None): xml_writer.node_add("{0} UPC".format(xml_base_path), value)

		value = self.get_device_serial_number()
		if (value != None): xml_writer.node_add("{0} serialNumber".format(xml_base_path), value)

		value = self.get_presentation_url()
		if (value != None): xml_writer.node_add("{0} presentationURL".format(xml_base_path), value)

		if (len(self.services) > 0):
		#
			position = 0

			for service_name in self.services:
			#
				service = self.service_get(service_name)

				if (isinstance(service, direct_abstract_service)):
				#
					xml_service_base_path = "{0} serviceList service#{1:d}".format(xml_base_path, position)

					xml_writer.node_add("{0} serviceId".format(xml_service_base_path), "urn:{0}".format(service.get_service_id_urn()))
					xml_writer.node_set_cache_path(xml_service_base_path)

					xml_writer.node_add("{0} serviceType".format(xml_service_base_path), "urn:{0}".format(service.get_urn()))
					xml_writer.node_add("{0} SCPDURL".format(xml_service_base_path), service.get_url_scpd())
					xml_writer.node_add("{0} controlURL".format(xml_service_base_path), service.get_url_control())
					xml_writer.node_add("{0} eventSubURL".format(xml_service_base_path), service.get_url_event_control())

					position += 1
				#
			#
		#

		if (len(self.embedded_devices) > 0):
		#
			position = 0

			for uuid in self.embedded_devices:
			#
				device = self.embedded_device_get(uuid)

				if (isinstance(device, direct_abstract_device)):
				#
					device.get_xml_walker(xml_writer, "{0} deviceList device#{1:d}".format(xml_base_path, position))
					position += 1
				#
			#
		#
	#

	def init_device(self, control_point, udn, configid = None):
	#
		"""
Initialize a host device.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.configid = configid
		self.host_device = True
		self.udn = udn

		url = "http://{0}:{1:d}/upnp/{2}".format(control_point.get_http_host(), control_point.get_http_port(), direct_links.escape(self.udn))
		self.desc_url = "{0}/desc".format(url)
		self.url_base = "{0}/".format(url)

		return False
	#

	def is_managed(self):
	#
		"""
True if the host manages the device.

:return: (bool) False if remote UPnP device
:since:  v0.1.00
		"""

		return self.host_device
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

	def set_device_model(self, model):
	#
		"""
Sets the UPnP modelDescription value.

:param model: Model name

:since: v0.1.00
		"""

		self.device_model = model
	#

	def set_device_model_upc(self, model_upc):
	#
		"""
Sets the UPnP UPC value.

:return model_upc: UPC code

:since: v0.1.00
		"""

		self.device_model_upc = model_upc
	#

	def set_device_model_url(self, model_url):
	#
		"""
Sets the UPnP modelURL value.

:param model_url: Device model URL

:since: v0.1.00
		"""

		self.device_model_url = model_url
	#

	def set_device_model_version(self, model_version):
	#
		"""
Sets the UPnP modelNumber value.

:param model_version: Device model version

:since: v0.1.00
		"""

		self.device_model_version = model_version
	#

	def set_device_serial_number(self, serial_number):
	#
		"""
Sets the UPnP serialNumber value.

:param serial_number: Device serial number

:since: v0.1.00
		"""

		self.device_serial_number = serial_number
	#

	def set_manufacturer(self, manufacturer):
	#
		"""
Sets the UPnP manufacturer value.

:param manufacturer: Manufacturer

:since: v0.1.00
		"""

		self.manufacturer = manufacturer
	#

	def set_manufacturer_url(self, manufacturer_url):
	#
		"""
Sets the UPnP manufacturerURL value.

:param manufacturer_url: Manufacturer URL

:since: v0.1.00
		"""

		self.manufacturer_url = manufacturer_url
	#

	def set_name(self, name):
	#
		"""
Sets the UPnP friendlyName value.

:param name: Network name

:since: v0.1.00
		"""

		self.name = name
	#

	def set_presentation_url(self, presentation_url):
	#
		"""
Sets the UPnP presentationURL value.

:param presentation_url: Presentation URL

:since: v0.1.00
		"""

		self.presentation_url = presentation_url
	#

	def set_spec_version(self, version):
	#
		"""
Sets the UPnP specVersion number.

:param version: (tuple) UPnP Device Architecture version

:since: v0.1.00
		"""

		if (type(version) == tuple and len(version) == 2):
		#
			self.spec_major = version[0]
			self.spec_minor = version[1]
		#
	#
#

##j## EOF