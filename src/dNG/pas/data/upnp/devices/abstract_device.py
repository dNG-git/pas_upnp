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

from binascii import hexlify
from os import urandom
from socket import gethostname
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid_of_namespace

from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.text.link import Link
from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.device import Device
from dNG.pas.data.upnp.services.abstract_service import AbstractService

class AbstractDevice(Device):
#
	"""
An extended, abstract device implementation for server devices.

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
Constructor __init__(AbstractDevice)

:since: v0.1.00
		"""

		Device.__init__(self)

		self.client_user_agent = None
		"""
Client user agent
		"""
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

	def get_service(self, _id):
	#
		"""
Returns a UPnP service for the given UPnP service ID.

:param _id: UPnP serviceId value

:return: (object) UPnP service; None if unknown
:since:  v0.1.00
		"""

		_return = Device.get_service(self, _id)
		if (_return != None and _return.is_managed()): _return.set_client_user_agent(self.client_user_agent)

		return _return
	#

	def get_type(self):
	#
		"""
Returns the UPnP device type.

:return: (str) Device type
:since:  v0.1.00
		"""

		return (self.type if (self.host_device) else Device.get_type(self))
	#

	def get_udn(self):
	#
		"""
Returns the UPnP UDN value.

:return: (str) UPnP device UUID
:since:  v0.1.00
		"""

		return (self.udn if (self.host_device) else Device.get_udn(self))
	#

	def get_upnp_domain(self):
	#
		"""
Returns the UPnP device specification domain.

:return: (str) UPnP device specification domain
:since:  v0.1.00
		"""

		return (self.upnp_domain if (self.host_device) else Device.get_upnp_domain(self))
	#

	def get_urn(self):
	#
		"""
Returns the UPnP deviceType value.

:return: (str) UPnP URN
:since:  v0.1.00
		"""

		return ("{0}:device:{1}:{2}".format(self.get_upnp_domain(), self.get_type(), self.get_version())
		        if (self.host_device) else
		        Device.get_urn(self)
		       )
	#

	def get_version(self):
	#
		"""
Returns the UPnP device type version.

:return: (str) Device type version; None if undefined
:since:  v0.1.00
		"""

		return (self.version if (self.host_device) else Device.get_version(self))
	#

	def get_xml(self):
	#
		"""
Returns the UPnP device description.

:return: (str) Device description XML
:since:  v0.1.00
		"""

		xml_resource = self._get_xml(self._init_xml_resource())
		return xml_resource.export_cache(True)
	#

	def _get_xml(self, xml_resource):
	#
		"""
Returns the UPnP device description for encoding.

:param xml_resource: XML resource

:return: (object) Device description XML resource
:since:  v0.1.01
		"""

		LogLine.debug("#echo(__FILEPATH__)# -{0!r}._get_xml()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		client = Client.load_user_agent(self.client_user_agent)
		if (not client.get("upnp_xml_cdata_encoded", False)): xml_resource.set_cdata_encoding(False)

		attributes = { "xmlns": "urn:schemas-upnp-org:device-1-0" }
		if (self.configid != None): attributes['configId'] = self.configid

		xml_resource.add_node("root", attributes = attributes)
		xml_resource.set_cached_node("root")

		client = Client.load_user_agent(self.client_user_agent)

		spec_version = (self.get_spec_version()
		                if (client.get("upnp_spec_versioning_supported", True)) else
		                ( 1, 0 )
		               )

		xml_resource.add_node("root specVersion major", str(spec_version[0]))
		xml_resource.add_node("root specVersion minor", str(spec_version[1]))

		self._get_xml_walker(xml_resource, "root device")
		return xml_resource
	#

	def _get_xml_walker(self, xml_resource, xml_base_path):
	#
		"""
Uses the given XML resource to add the UPnP device description at the given
XML node path.

:param xml_resource: XML resource
:param xml_base_path: Device description XML base path (e.g. "root device")

:since: v0.1.00
		"""

		# pylint: disable=protected-access

		udn = "uuid:{0}".format(self.get_udn())
		xml_resource.add_node("{0} UDN".format(xml_base_path), udn)
		xml_resource.set_cached_node(xml_base_path)

		xml_resource.add_node("{0} deviceType".format(xml_base_path), "urn:{0}".format(self.get_urn()))
		xml_resource.add_node("{0} friendlyName".format(xml_base_path), self.get_name())
		xml_resource.add_node("{0} manufacturer".format(xml_base_path), self.get_manufacturer())

		value = self.get_manufacturer_url()
		if (value != None): xml_resource.add_node("{0} manufacturerURL".format(xml_base_path), value)

		value = self.get_device_model()
		if (value != None): xml_resource.add_node("{0} modelName".format(xml_base_path), value)

		value = self.get_device_model_desc()
		if (value != None): xml_resource.add_node("{0} modelDescription".format(xml_base_path), value)

		value = self.get_device_model_version()
		if (value != None): xml_resource.add_node("{0} modelNumber".format(xml_base_path), value)

		value = self.get_device_model_url()
		if (value != None): xml_resource.add_node("{0} modelURL".format(xml_base_path), value)

		value = self.get_device_model_upc()
		if (value != None): xml_resource.add_node("{0} UPC".format(xml_base_path), value)

		value = self.get_device_serial_number()
		if (value != None): xml_resource.add_node("{0} serialNumber".format(xml_base_path), value)

		value = self.get_presentation_url()
		if (value != None): xml_resource.add_node("{0} presentationURL".format(xml_base_path), value)

		if (len(self.services) > 0):
		#
			position = 0

			for service_name in self.services:
			#
				service = self.get_service(service_name)

				if (isinstance(service, AbstractService)):
				#
					xml_service_base_path = "{0} serviceList service#{1:d}".format(xml_base_path, position)

					xml_resource.add_node(xml_service_base_path)
					xml_resource.set_cached_node(xml_service_base_path)

					xml_resource.add_node("{0} serviceId".format(xml_service_base_path), "urn:{0}".format(service.get_service_id_urn()))
					xml_resource.add_node("{0} serviceType".format(xml_service_base_path), "urn:{0}".format(service.get_urn()))
					xml_resource.add_node("{0} SCPDURL".format(xml_service_base_path), service.get_url_scpd())
					xml_resource.add_node("{0} controlURL".format(xml_service_base_path), service.get_url_control())
					xml_resource.add_node("{0} eventSubURL".format(xml_service_base_path), service.get_url_event_control())

					position += 1
				#
			#
		#

		if (len(self.embedded_devices) > 0):
		#
			position = 0

			for uuid in self.embedded_devices:
			#
				device = self.get_embedded_device(uuid)

				if (isinstance(device, AbstractDevice)):
				#
					xml_resource.add_node("{0} deviceList device#{1:d}".format(xml_base_path, position))

					device._get_xml_walker(xml_resource, "{0} deviceList device#{1:d}".format(xml_base_path, position))
					position += 1
				#
			#
		#
	#

	def init_device(self, control_point, udn = None, configid = None):
	#
		"""
Initialize a host device.

:return: (bool) Returns true if initialization was successful.
:since:  v0.1.00
		"""

		self.configid = configid
		self.host_device = True
		if (self.name == None): self.name = "{0} {1}".format(gethostname(), self.type)
		self.udn = (str(uuid_of_namespace(NAMESPACE_URL, "upnp://{0}:{1:d}/{2}".format(control_point.get_http_host(), control_point.get_http_port(), hexlify(urandom(10))))) if (udn == None) else udn)

		url = "http://{0}:{1:d}/upnp/{2}".format(control_point.get_http_host(), control_point.get_http_port(), Link.encode_query_value(self.udn))
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
#

##j## EOF