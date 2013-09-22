# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.ControlPoint
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

from copy import copy
from locale import getlocale
from os import uname
from random import randint
from random import uniform as randfloat
from time import time
from weakref import ref
import re
import socket

try: from urllib.parse import urljoin, urlsplit
except ImportError: from urlparse import urljoin, urlsplit

from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.data.rfc.http import Http
from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.upnp.device import Device
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.net.upnp.ssdp_message import SsdpMessage
from dNG.pas.net.upnp.ssdp_response import SsdpResponse
from dNG.pas.plugins.hooks import Hooks
from dNG.pas.tasks.abstract_timed import AbstractTimed
from .gena import Gena
from .ssdp_listener_ipv4_multicast import SsdpListenerIpv4Multicast
from .ssdp_listener_ipv6_multicast import SsdpListenerIpv6Multicast

class ControlPoint(AbstractTimed):
#
	"""
The UPnP ControlPoint.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	ANNOUNCE_DEVICE = 1
	"""
Initial UPnP device announcement
	"""
	ANNOUNCE_DEVICE_SHUTDOWN = 2
	"""
UPnP device shutdown announcement
	"""
	ANNOUNCE_DEVICE_UPDATE = 3
	"""
UPnP device update announcement
	"""
	ANNOUNCE_SEARCH_RESULT = 4
	"""
Search result announcement
	"""
	ANNOUNCE_SERVICE = 5
	"""
UPnP service announcement
	"""
	REANNOUNCE_DEVICE = 6
	"""
Subsequent UPnP device announcement
	"""

	weakref_instance = None
	"""
ControlPoint weakref instance
	"""

	def __init__(self):
	#
		"""
Constructor __init__(ControlPoint)

:since: v0.1.00
		"""

		AbstractTimed.__init__(self)

		self.bootid = 0
		"""
UPnP bootid value (bootid.upnp.org); nextbootid.upnp.org += 1
		"""
		self.configid = 0
		"""
UPnP configid value (configid.upnp.org)
		"""
		self.devices = { }
		"""
List of devices with its services
		"""
		self.gena = None
		"""
UPnP GENA manager
		"""
		self.http_host = None
		"""
HTTP Accept-Language value
		"""
		self.http_language = (L10n.get("lang_iso") if (L10n.is_defined("lang_iso")) else None)
		"""
HTTP Accept-Language value
		"""
		self.http_port = None
		"""
HTTP Accept-Language value
		"""
		self.listener_ipv4 = None
		"""
Unicast IPv4 listener
		"""
		self.listener_port = int(Settings.get("pas_upnp_device_port", 1900))
		"""
Unicast port in the range 49152-65535 (searchport.upnp.org)
		"""
		self.listeners_multicast = { }
		"""
Multicast listeners
		"""
		self.listeners_multicast_ipv4 = 0
		"""
Number of IPv4 multicast listeners
		"""
		self.listeners_multicast_ipv6 = 0
		"""
Number of IPv6 multicast listeners
		"""
		self.managed_devices = { }
		"""
List of managed devices
		"""
		self.rootdevices = [ ]
		"""
List of UPnP root devices
		"""
		self.tasks = [ ]
		"""
List of tasks (e.g. timed out services) to run
		"""
		self.upnp_desc = { }
		"""
Received UPnP descriptions
		"""
		self.upnp_desc_unread = { }
		"""
Unread UPnP description URLs
		"""
		self.usns = { }
		"""
List of devices with its services
		"""

		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)

		if (self.http_language == None):
		#
			system_language = getlocale()[0]
			http_language = re.sub("\\W", "", (Settings.get("core_lang", "en_US") if (system_language == None or system_language == "c") else system_language))
		#
		else: http_language = self.http_language.replace("_", "")

		if (Settings.is_defined("core_lang_{0}".format(http_language))): http_language = Settings.get("core_lang_{0}".format(http_language))
		elif (Settings.is_defined("core_lang_{0}".format(http_language[:2]))): http_language = Settings.get("core_lang_{0}".format(http_language[:2]))

		lang_iso_domain = http_language[:2]

		if (len(http_language) > 2): self.http_language = "{0}-{1}".format(http_language[:2], http_language[2:])
		else: self.http_language = http_language

		self.http_language += ", {0}".format(lang_iso_domain)
		if (lang_iso_domain != "en"): self.http_language += ", en-US, en"
	#

	def _announce(self, _type, usn = None, location = None, additional_data = None):
	#
		"""
Announces host device changes over SSDP.

:param _type: SSDP message type
:param usn: UPnP USN
:param location: Location of the UPnP description
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._announce(_type, usn, location, additional_data)- (#echo(__LINE__)#)")

		identifier = (None if (usn == None) else Device.get_identifier(usn, self.bootid, self.configid))

		announce_targets = [ ]
		if (self.listeners_multicast_ipv4 > 0): announce_targets.append("239.255.255.250")
		if (self.listeners_multicast_ipv6 > 0): announce_targets += [ "[ff02::c]", "[ff04::c]", "[ff05::c]", "[ff08::c]", "[ff0e::c]" ]

		with ControlPoint.synchronized:
		#
			if (_type == ControlPoint.ANNOUNCE_DEVICE_SHUTDOWN and identifier != None):
			#
				if (identifier['uuid'] in self.managed_devices):
				#
					device = self.managed_devices[identifier['uuid']]
					services = device.service_get_unique_types()

					for service_id in services:
					#
						for announce_target in announce_targets:
						#
							service = device.service_get(service_id)
							ssdp_request = SsdpMessage(announce_target)
							ssdp_request.set_header("NTS", "ssdp:byebye")
							ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
							ssdp_request.set_header("USN", "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()))
							ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
							ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
							ssdp_request.send_notify()
						#
					#
				#

				for announce_target in announce_targets:
				#
					ssdp_request = SsdpMessage(announce_target)
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
					ssdp_request.set_header("USN", usn)
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
					ssdp_request.send_notify()

					if (identifier['class'] == "device"):
					#
						ssdp_request = SsdpMessage(announce_target)
						ssdp_request.set_header("NTS", "ssdp:byebye")
						ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
						ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
						ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
						ssdp_request.send_notify()
					#

					if (self.rootdevice_is_known(identifier['uuid'])):
					#
						ssdp_request = SsdpMessage(announce_target)
						ssdp_request.set_header("NTS", "ssdp:byebye")
						ssdp_request.set_header("NT", "upnp:rootdevice")
						ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
						ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
						ssdp_request.send_notify()
					#
				#

				self._tasks_remove(identifier['usn'], "reannounce_device")
			#
			elif ((_type == ControlPoint.ANNOUNCE_DEVICE or _type == ControlPoint.REANNOUNCE_DEVICE) and identifier != None and location != None):
			#
				for announce_target in announce_targets:
				#
					ssdp_request = SsdpMessage(announce_target)
					ssdp_request.set_header("Cache-Control", "max-age=3600")
					ssdp_request.set_header("NTS", "ssdp:alive")
					ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
					ssdp_request.set_header("USN", usn)
					ssdp_request.set_header("LOCATION", location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
					ssdp_request.send_notify()

					if (identifier['class'] == "device"):
					#
						ssdp_request = SsdpMessage(announce_target)
						ssdp_request.set_header("Cache-Control", "max-age=3600")
						ssdp_request.set_header("NTS", "ssdp:alive")
						ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
						ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
						ssdp_request.set_header("LOCATION", location)
						ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
						ssdp_request.send_notify()
					#

					if (self.rootdevice_is_known(identifier['uuid'])):
					#
						ssdp_request = SsdpMessage(announce_target)
						ssdp_request.set_header("Cache-Control", "max-age=3600")
						ssdp_request.set_header("NTS", "ssdp:alive")
						ssdp_request.set_header("NT", "upnp:rootdevice")
						ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
						ssdp_request.set_header("LOCATION", location)
						ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
						ssdp_request.send_notify()
					#
				#

				if (identifier['uuid'] in self.managed_devices):
				#
					device = self.managed_devices[identifier['uuid']]
					services = device.service_get_unique_types()

					for service_id in services:
					#
						for announce_target in announce_targets:
						#
							service = device.service_get(service_id)
							ssdp_request = SsdpMessage(announce_target)
							ssdp_request.set_header("Cache-Control", "max-age=3600")
							ssdp_request.set_header("NTS", "ssdp:alive")
							ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
							ssdp_request.set_header("USN", "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()))
							ssdp_request.set_header("LOCATION", location)
							ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
							ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
							ssdp_request.send_notify()
						#
					#
				#

				if (_type == ControlPoint.ANNOUNCE_DEVICE): self._task_add(0.3, "reannounce_device", usn = usn, location = location)
				else:
				#
					wait_seconds = randint(600, 1800)
					self._task_add(wait_seconds, "reannounce_device", usn = usn, location = location)
				#
			#
			elif (_type == ControlPoint.ANNOUNCE_SEARCH_RESULT and identifier != None and location != None and additional_data != None and "search_target" in additional_data and "target_host" in additional_data and "target_port" in additional_data):
			#
				ssdp_request = SsdpResponse(additional_data['target_host'], additional_data['target_port'])
				ssdp_request.set_header("Cache-Control", "max-age=3600")
				ssdp_request.set_header("Date", RfcBasics.get_rfc1123_datetime(time()))
				ssdp_request.set_header("EXT", "")
				ssdp_request.set_header("ST", additional_data['search_target'])
				ssdp_request.set_header("USN", usn)
				ssdp_request.set_header("LOCATION", location)
				ssdp_request.set_header("BOOTID.UPNP.ORG", str(self.bootid))
				ssdp_request.set_header("CONFIGID.UPNP.ORG", str(self.configid))
				ssdp_request.send()
			#
		#
	#

	def _delete(self, identifier, additional_data = None):
	#
		"""
Delete the parsed UPnP identifier from the ControlPoint list.

:param identifier: Parsed UPnP identifier
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._delete(identifier, additional_data)- (#echo(__LINE__)#)")

		with ControlPoint.synchronized:
		#
			if (identifier['usn'] in self.usns and (identifier['bootid'] == None or self.usns[identifier['usn']]['bootid'] <= identifier['bootid'])):
			#
				usn_data = self.usns[identifier['usn']]

				if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint deletes USN '{0}'".format(identifier['usn']))

				if (usn_data['uuid'] in self.managed_devices):
				#
					Hooks.call("dNG.pas.upnp.control_point.host_device_remove", identifier = identifier)
					self._announce(ControlPoint.ANNOUNCE_DEVICE_SHUTDOWN, identifier['usn'])
					del(self.managed_devices[usn_data['uuid']])
				#
				elif ("url_desc_read" in usn_data):
				#
					if (self.gena != None and "ips" in usn_data):
					#
						for ip in usn_data['ips']: self.gena.cancel(("{0}:{1}:{2}".format(usn_data['domain'], usn_data['class'], usn_data['type']) if ("urn" in usn_data) else None), ip)
					#

					if (usn_data['class'] == "device"): Hooks.call("dNG.pas.upnp.control_point.device_remove", identifier = usn_data)
					Hooks.call("dNG.pas.upnp.control_point.usn_delete", identifier = usn_data)
				#

				self._delete_upnp_desc(identifier)

				"""
Always delete the device itself first. Known related devices and services
can be safely deleted afterwards.
				"""

				self._tasks_remove(identifier['usn'])
				del(self.usns[identifier['usn']])

				if (identifier['device'] in self.devices):
				#
					if (identifier['usn'] in self.devices[identifier['device']]): self.devices[identifier['device']].remove(identifier['usn'])

					if (self.rootdevice_is_known(identifier['uuid'])):
					#
						self.rootdevice_remove(identifier['usn'])

						self._delete_usns(self.devices[identifier['device']])
						if (identifier['device'] in self.devices): del(self.devices[identifier['device']])
					#
				#
			#
		#
	#

	def _delete_upnp_desc(self, identifier):
	#
		"""
Delete the USN from the list of UPnP descriptions.

:param identifier: Parsed UPnP identifier

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._delete_upnp_desc(identifier)- (#echo(__LINE__)#)")

		upnp_desc = self.upnp_desc.copy()

		for url in upnp_desc:
		#
			if (identifier['usn'] in self.upnp_desc[url]['usns']): self.upnp_desc[url]['usns'].remove(identifier['usn'])
			if (len(self.upnp_desc[url]['usns']) < 1): del(self.upnp_desc[url])
		#
	#

	def delete_usn(self, usn, bootid, configid, additional_data = None):
	#
		"""
Delete the USN from the ControlPoint list.

:param usn: UPnP USN
:param bootid: UPnP bootid (bootid.upnp.org) if any
:param configid: UPnP configid (configid.upnp.org) if any
:param url: UPnP description location
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (len(usn) > 41):
		#
			identifier = Device.get_identifier(usn, bootid, configid)

			if (identifier != None):
			#
				with ControlPoint.synchronized:
				#
					if (identifier['usn'] in self.usns and identifier['uuid'] not in self.managed_devices): self._delete(identifier, additional_data)
				#
			#
		#
	#

	def _delete_usns(self, usns):
	#
		"""
Delete all USNs from the given list.

:param usns: USN list

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._delete_usns(usns)- (#echo(__LINE__)#)")

		with ControlPoint.synchronized:
		#
			for usn in usns:
			#
				if (usn in self.usns): self._delete(self.usns[usn])
			#
		#
	#

	def device_add(self, device):
	#
		"""
Add a device to the managed list and announce it. Multiple hierarchies are not
supported and must be handled separately.

:param device: UPnP host device

:return: (bool) True if added successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint.device_add(device)- (#echo(__LINE__)#)")
		_return = True

		if (isinstance(device, Device) and device.is_managed()):
		#
			with ControlPoint.synchronized:
			#
				if (self.configid < 16777216): self.configid += 1
				else: self.configid = 0

				device_identifier = Device.get_identifier("uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn()), self.bootid, self.configid)

				if (device_identifier != None and device_identifier['usn'] not in self.usns):
				#
					if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint adds UPnP root device USN '{0}'".format(device_identifier['usn']))

					if (device_identifier['uuid'] not in self.rootdevices): self.rootdevices.append(device_identifier['uuid'])
					device_identifier['managed'] = True
					device_identifier['url_desc'] = device.get_desc_url()
					self.managed_devices[device_identifier['uuid']] = device
					self.usns[device_identifier['usn']] = device_identifier

					self._announce(ControlPoint.ANNOUNCE_DEVICE_SHUTDOWN, device_identifier['usn'], device_identifier['url_desc'])

					wait_seconds = randfloat(0.2, 0.4)
					self._task_add(wait_seconds, "announce_device", usn = device_identifier['usn'], location = device_identifier['url_desc'])

					Hooks.call("dNG.pas.upnp.control_point.host_device_add", identifier = device_identifier)

					embedded_device_uuids = device.embedded_device_get_uuids()

					for uuid in embedded_device_uuids:
					#
						embedded_device = device.embedded_device_get(uuid)
						embedded_device_identifier = Device.get_identifier("uuid:{0}::urn:{1}".format(embedded_device.get_udn(), embedded_device.get_urn()), self.bootid, self.configid)
						if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint adds UPnP device USN '{0}'".format(embedded_device_identifier['usn']))

						embedded_device_identifier['managed'] = True
						embedded_device_identifier['url_desc'] = embedded_device.get_desc_url()
						self.managed_devices[embedded_device_identifier['uuid']] = embedded_device
						self.usns[embedded_device_identifier['usn']] = embedded_device_identifier

						wait_seconds = randfloat(0.4, 0.6)
						self._task_add(wait_seconds, "announce_device", usn = embedded_device_identifier['usn'], location = embedded_device_identifier['url_desc'])

						Hooks.call("dNG.pas.upnp.control_point.host_device_add", identifier = embedded_device_identifier)
					#

					if (self.gena == None):
					#
						self.gena = Gena.get_instance()
						self.gena.start()
					#
				#
				else: _return = False
			#
		#
		else: _return = False

		return _return
	#

	def device_get(self, identifier):
	#
		"""
Return a UPnP device for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		device = self.rootdevice_get(identifier)

		if (device != None):
		#
			if (device.get_udn() == identifier['uuid']): _return = device
			else: _return = device.embedded_device_get(identifier['uuid'])

			if (_return != None and _return.is_managed()): _return.set_configid(self.configid)
		#

		return _return
	#

	def device_remove(self, device):
	#
		"""
Remove a device from the managed list and announce the change.

:param device: UPnP host device

:return: (bool) True if added successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint.device_remove(device)- (#echo(__LINE__)#)")
		_return = False

		if (isinstance(device, Device) and device.is_managed()):
		#
			with ControlPoint.synchronized:
			#
				device_identifier = Device.get_identifier("uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn()), self.bootid, self.configid)

				if (device_identifier != None and device_identifier['usn'] in self.usns):
				#
					if (self.configid < 16777216): self.configid += 1
					else: self.configid = 0

					self._delete(device_identifier)

					for uuid in self.managed_devices:
					#
						if (device_identifier['uuid'] != uuid):
						#
							usn = "uuid:{0}::urn:{1}".format(self.managed_devices[uuid].get_udn(), self.managed_devices[uuid].get_urn())
							self._tasks_remove(usn, "reannounce_device")
							self._announce(ControlPoint.REANNOUNCE_DEVICE, usn, self.managed_devices[uuid].get_desc_url())
						#
					#

					if (len(self.managed_devices) < 1 and self.gena != None): self.gena = None
					_return = True
				#
			#
		#

		return _return
	#

	def get_desc_xml(self, identifier):
	#
		"""
Return the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		with ControlPoint.synchronized:
		#
			if ("url_desc_read" in identifier and identifier['url_desc_read'] in self.upnp_desc): _return = self.upnp_desc[identifier['url_desc_read']]['xml_data']
			elif ("url_desc" in identifier and identifier['url_desc'] in self.upnp_desc): _return = self.upnp_desc[identifier['url_desc']]['xml_data']
			else:
			#
				for url in self.upnp_desc:
				#
					if (identifier['usn'] in self.upnp_desc[url]['usns']):
					#
						_return = self.upnp_desc[url]['xml_data']
						break
					#
				#
			#
		#

		return _return
	#

	def get_http_host(self):
	#
		"""
Returns the UPnP HTTP server hostname.

:since: v0.1.00
		"""

		return self.http_host
	#

	def get_http_port(self):
	#
		"""
Returns the UPnP HTTP server port.

:since: v0.1.00
		"""

		return self.http_port
	#

	def _get_next_update_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.00
		"""

		with ControlPoint.synchronized:
		#
			if (len(self.tasks) > 0): _return = self.tasks[0]['timestamp']
			else: _return = -1
		#

		return _return
	#

	def handle_soap_request(self, http_wsgi_request, virtual_config):
	#
		"""
Return the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint.handle_soap_request(http_wsgi_request, virtual_config)- (#echo(__LINE__)#)")

		client_host = http_wsgi_request.get_client_host()
		is_allowed = False
		is_valid = False

		if (client_host == None): is_allowed = True
		else:
		#
			ip_address_paths = socket.getaddrinfo(client_host, http_wsgi_request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
			is_allowed = (False if (len(ip_address_paths) < 1) else self.is_ip_allowed(ip_address_paths[0][4][0]))
		#

		if (is_allowed):
		#
			virtual_path = http_wsgi_request.get_dsd("upnp_path")

			if (virtual_path != None):
			#
				with ControlPoint.synchronized:
				#
					device = None
					request_data = virtual_path.split("/", 2)
					request_data_length = len(request_data)

					if (request_data_length == 2 and request_data[0] == "stream"): is_valid = True
					elif (request_data[0] in self.managed_devices):
					#
						device = self.managed_devices[request_data[0]]

						if (request_data_length == 1): is_valid = True
						elif (request_data_length == 2 and request_data[1] == "desc"): is_valid = True
						elif (request_data_length > 2 and (request_data[2] == "control" or request_data[2] == "eventsub" or request_data[2] == "xml") and device.service_get(request_data[1]) != None): is_valid = True
					#
				#
			#
		#

		if (not is_allowed):
		#
			if (self.log_handler != None): self.log_handler.warning("pas.upnp.ControlPoint refused client '{0}'".format(client_host))

			_return = PredefinedHttpRequest()
			_return.set_output_format("http_upnp")
			_return.set_module("output")
			_return.set_service("http")
			_return.set_action("error")
			_return.set_dsd("code", "403")
		#
		elif (not is_valid):
		#
			_return = PredefinedHttpRequest()
			_return.set_output_format("http_upnp")
			_return.set_module("output")
			_return.set_service("http")
			_return.set_action("error")
			_return.set_dsd("code", "400")
		#
		else:
		#
			_return = HttpUpnpRequest()
			_return.set_request(http_wsgi_request, self, device, request_data)
		#

		return _return
	#

	def is_ip_allowed(self, ip):
	#
		"""
Returns true if the given IP is a allowed to send UPnP control requests.

:param ip: IPv4 or IPv6

:return: (bool) True if IP is known
:since:  v0.1.00
		"""

		allowed_networks = Settings.get("pas_upnp_allowed_networks")
		_return = False

		if (allowed_networks == None):
		#
			with ControlPoint.synchronized:
			#
				for usn in self.usns:
				#
					if ("ips" in self.usns[usn] and ip in self.usns[usn]['ips']):
					#
						_return= True
						break
					#
				#
			#
		#
		else:
		#
			for network_prefix in allowed_networks:
			#
				if (":" in network_prefix and network_prefix[-2:] != "::"): network_prefix += "::"
				elif (network_prefix[-1:] != "."): network_prefix += "."

				if (ip.startswith(network_prefix)):
				#
					_return = True
					break
				#
			#
		#

		return _return
	#

	def _listeners_multicast_add(self, ip):
	#
		"""
Starts all multicast listeners based on the IP address given.

:param ip: IPv4 / IPv6 address

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._listeners_multicast_add({0})- (#echo(__LINE__)#)".format(ip))

		with ControlPoint.synchronized:
		#
			if (ip not in self.listeners_multicast):
			#
				if (":" in ip):
				#
					self.listeners_multicast[ip] = [
						SsdpListenerIpv6Multicast(ip),
						SsdpListenerIpv6Multicast(ip, "ff04::c"),
						SsdpListenerIpv6Multicast(ip, "ff05::c"),
						SsdpListenerIpv6Multicast(ip, "ff08::c"),
						SsdpListenerIpv6Multicast(ip, "ff0e::c")
					]

					self.listeners_multicast_ipv6 += 1
				#
				else:
				#
					self.listeners_multicast[ip] = [ SsdpListenerIpv4Multicast(ip) ]
					self.listeners_multicast_ipv4 += 1
				#

				for listener in self.listeners_multicast[ip]: listener.start()
			#
		#
	#

	def _listeners_multicast_remove(self, ip):
	#
		"""
Stops all multicast listeners based on the IP address given.

:param ip: IPv4 / IPv6 address

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._listeners_multicast_remove({0})- (#echo(__LINE__)#)".format(ip))

		with ControlPoint.synchronized:
		#
			if (ip in self.listeners_multicast):
			#
				for listener in self.listeners_multicast[ip]: listener.stop()
				del(self.listeners_multicast[ip])

				if (":" in ip): self.listeners_multicast_ipv6 -= 1
				else: self.listeners_multicast_ipv4 -= 1
			#
		#
	#

	def _read_upnp_descs(self):
	#
		"""
Parse unread UPnP descriptions.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._read_upnp_descs()- (#echo(__LINE__)#)")

		with ControlPoint.synchronized:
		#
			upnp_desc_unread = self.upnp_desc_unread.copy()
			self.upnp_desc_unread.clear()
		#

		os_uname = uname()

		for url in upnp_desc_unread:
		#
			usns = upnp_desc_unread[url]
			http_response = None

			try:
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint reads UPnP device description from '{0}'".format(url))

				http_client = Http(url, event_handler = self.log_handler)
				http_client.set_header("Accept-Language", self.http_language)
				http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
				http_client.set_ipv6_link_local_interface(Settings.get("pas_global_ipv6_link_local_interface"))

				http_response = http_client.request_get()
				if (isinstance(http_response['body'], Exception)): raise http_response['body']
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
				self._delete_usns(usns)
			#

			if (http_response != None):
			#
				with ControlPoint.synchronized:
				#
					if (url in self.upnp_desc): self.upnp_desc[url]['xml_data'] = Binary.str(http_response['body'])
					else: self.upnp_desc[url] = { "xml_data": Binary.str(http_response['body']), "usns": [ ] }

					for usn in usns:
					#
						if (usn in self.usns and usn not in self.upnp_desc[url]['usns']):
						#
							self.usns[usn]['url_desc_read'] = url
							self.usns[usn]['httpname'] = (http_response['headers']['SERVER'] if ("SERVER" in http_response['headers']) else None)

							self.upnp_desc[url]['usns'].append(usn)

							Hooks.call("dNG.pas.upnp.control_point.usn_new", identifier = self.usns[usn])
							if (self.usns[usn]['class'] == "device"): Hooks.call("dNG.pas.upnp.control_point.device_add", identifier = self.usns[usn])
						#
					#
				#
			#
		#
	#

	def rootdevice_add(self, usn, timeout):
	#
		"""
Add a rootdevice to the list of known root devices. It will automatically be
removed if the timeout expires.

:param usn: UPnP USN
		"""

		with ControlPoint.synchronized:
		#
			identifier = Device.get_identifier(usn, self.bootid, self.configid)

			if (identifier['uuid'] in self.rootdevices):
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint renews TTL for UPnP root device USN '{0}' (TTL '{1:d}')".format(usn, timeout))

				self._tasks_remove(usn, "rootdevice_remove")
				self._task_add(timeout, "rootdevice_remove", usn = usn)
			#
			else:
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint adds UPnP root device USN '{0}' (TTL '{1:d}')".format(usn, timeout))

				self.rootdevices.append(identifier['uuid'])
				self._task_add(timeout, "rootdevice_remove", usn = usn)
			#
		#
	#

	def rootdevice_is_known(self, uuid):
	#
		"""
Check if a given UPnP UUID is a known rootdevice.
		"""

		return (uuid in self.rootdevices)
	#

	def rootdevice_get(self, identifier):
	#
		"""
Return a UPnP rootdevice for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		with ControlPoint.synchronized:
		#
			if (identifier['class'] == "device" and identifier['usn'] in self.usns):
			#
				if (identifier['uuid'] in self.managed_devices):
				#
					if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint got request to return the hosted device '{0}'".format(identifier['usn']))
					_return = self.managed_devices[identifier['uuid']]
					_return.set_configid(self.configid)
				#
				else:
				#
					if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint got request to create an object for device '{0}'".format(identifier['usn']))

					_return = (NamedLoader.get_instance("dNG.pas.data.upnp.devices.{0}".format(identifier['type']), False) if (identifier['class'] == "device") else None)
					if (_return == None): _return = Device()
					if (_return.init_xml_desc(self.usns[identifier['usn']], self.get_desc_xml(identifier)) == False): _return = None
				#
			#
		#

		return _return
	#

	def rootdevice_remove(self, usn):
	#
		"""
Remove a rootdevice from the list of known root devices.

:param usn: UPnP USN
		"""

		identifier = Device.get_identifier(usn, self.bootid, self.configid)

		with ControlPoint.synchronized:
		#
			if (identifier['uuid'] in self.rootdevices):
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint removes UPnP root device USN '{0}'".format(usn))

				self.rootdevices.remove(identifier['uuid'])
				self._tasks_remove(usn, "rootdevice_remove")
			#
		#
	#

	def run(self):
	#
		"""
Worker loop

:since: v0.1.00
		"""

		task = None

		with ControlPoint.synchronized:
		#
			if (len(self.tasks) > 0 and self.tasks[0]['timestamp'] <= time()): task = self.tasks.pop(0)
			AbstractTimed.run(self)
		#

		if (task != None):
		#
			try:
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint runs task type '{0}'".format(task['type']))

				if (task['type'] == "announce_device"): self._announce(ControlPoint.ANNOUNCE_DEVICE, task['usn'], task['location'])
				elif (task['type'] == "announce_search_result"): self._announce(ControlPoint.ANNOUNCE_SEARCH_RESULT, task['usn'], task['location'], task)
				elif (task['type'] == "delete"): self._delete(task['identifier'])
				elif (task['type'] == "read_upnp_descs"): self._read_upnp_descs()
				elif (task['type'] == "reannounce_device"): self._announce(ControlPoint.REANNOUNCE_DEVICE, task['usn'], task['location'])
				elif (task['type'] == "rootdevice_remove"): self.rootdevice_remove(task['usn'])
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
			#
		#
	#

	def search(self, source_data, source_wait_timeout, search_target, additional_data = None):
	#
		"""
Searches for hosted devices matching the given UPnP search target.

:param source_data: UPnP client address data
:param source_wait_timeout: UPnP MX value
:param search_target: UPnP search target
:param additional_data: Additional data received

:since: v0.1.00
		"""

		condition_identifier = None

		if (search_target == "ssdp:all" or search_target == "upnp:rootdevice" or search_target.startswith("uuid:")): condition = search_target
		elif (search_target.startswith("urn:")):
		#
			condition = search_target
			condition_identifier = Device.get_identifier("uuid:00000000-0000-0000-0000-000000000000::{0}".format(search_target), None, None)
		#
		elif (len(search_target) > 41):
		#
			condition = search_target
			condition_identifier = Device.get_identifier(search_target, None, None)
		#
		else: condition = False

		results = [ ]

		if (condition != False):
		#
			with ControlPoint.synchronized:
			#
				if (condition_identifier == None and condition == "upnp:rootdevice"):
				#
					for uuid in self.managed_devices:
					#
						if (uuid in self.rootdevices):
						#
							device = self.managed_devices[uuid]
							results.append({ "usn": "uuid:{0}::upnp:rootdevice".format(uuid), "location": device.get_desc_url(), "search_target": condition })
						#
					#
				#
				else:
				#
					for uuid in self.managed_devices:
					#
						device = self.managed_devices[uuid]
						device_matched = False

						if (condition_identifier != None):
						#
							if (condition_identifier['class'] == "device" and device.get_upnp_domain() == condition_identifier['domain'] and device.get_type() == condition_identifier['type'] and int(device.get_version()) >= int(condition_identifier['version'])): device_matched = True
						#
						elif (condition == "ssdp:all" or condition == "uuid:{0}".format(uuid)): device_matched = True

						if (device_matched):
						#
							results.append({ "usn": "uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn()), "location": device.get_desc_url(), "search_target": ("urn:{0}".format(device.get_urn()) if (condition == "ssdp:all") else condition) })

							if (condition == "ssdp:all"):
							#
								results.append({ "usn": "uuid:{0}".format(device.get_udn()), "location": device.get_desc_url(), "search_target": "uuid:{0}".format(device.get_udn()) })
								if (self.rootdevice_is_known(uuid)): results.append({ "usn": "uuid:{0}::upnp:rootdevice".format(device.get_udn()), "location": device.get_desc_url(), "search_target": "upnp:rootdevice" })
							#
						#

						embedded_devices = self.managed_devices[uuid].embedded_device_get_uuids()

						for embedded_uuid in embedded_devices:
						#
							embedded_device = self.managed_devices[uuid].embedded_device_get(embedded_uuid)
							embedded_device_matched = False

							if (condition_identifier != None and condition_identifier['class'] == "device" and embedded_device.get_upnp_domain() == condition_identifier['domain'] and embedded_device.get_type() == condition_identifier['type'] and int(embedded_device.get_version()) >= int(condition_identifier['version'])): embedded_device_matched = True
							elif (condition == "ssdp:all" or condition_identifier != None):
							#
								if (condition == "ssdp:all"): embedded_device_matched = True

								if (condition_identifier != None and condition_identifier['class'] == "service"):
								#
									services = embedded_device.service_get_ids()
		
									for service_id in services:
									#
										service = embedded_device.service_get(service_id)
										service_matched = False

										if (condition == "ssdp:all"): service_matched = True
										elif (service.get_upnp_domain() == condition_identifier['domain'] and service.get_type() == condition_identifier['type'] and int(service.get_version()) >= int(condition_identifier['version'])): service_matched = True

										if (service_matched): results.append({ "usn": "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()), "location": embedded_device.get_desc_url(), "search_target": ("urn:{0}".format(device.get_urn()) if (condition == "ssdp:all") else condition) })
									#
								#
							#
							elif ("uuid:{0}".format(uuid) == condition): embedded_device_matched = True

							if (embedded_device_matched):
							#
								results.append({ "usn": "uuid:{0}::urn:{1}".format(embedded_device.get_udn(), embedded_device.get_urn()), "location": embedded_device.get_desc_url(), "search_target": ("urn:{0}".format(device.get_urn()) if (condition == "ssdp:all") else condition) })
								if (condition == "ssdp:all"): results.append({ "usn": "uuid:{0}".format(device.get_udn()), "location": device.get_desc_url(), "search_target": "uuid:{0}".format(device.get_udn()) })
							#
						#

						if (condition == "ssdp:all" or (condition_identifier != None and condition_identifier['class'] == "service")):
						#
							services = self.managed_devices[uuid].service_get_ids()

							for service_id in services:
							#
								service = device.service_get(service_id)
								service_matched = False

								if (condition == "ssdp:all"): service_matched = True
								elif (service.get_upnp_domain() == condition_identifier['domain'] and service.get_type() == condition_identifier['type'] and int(service.get_version()) >= int(condition_identifier['version'])): service_matched = True

								if (service_matched): results.append({ "usn": "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()), "location": device.get_desc_url(), "search_target": ("urn:{0}".format(device.get_urn()) if (condition == "ssdp:all") else condition) })
							#
						#
					#
				#
			#

			if (len(results) > 0):
			#
				wait_seconds = randfloat(0, (source_wait_timeout if (source_wait_timeout < 10) else 10) / len(results))
				for result in results: self._task_add(wait_seconds, "announce_search_result", usn = result['usn'], location = result['location'], search_target = result['search_target'], target_host = ("[{0}]".format(source_data[0]) if (":" in source_data[0]) else source_data[0]), target_port = source_data[1])
			#
		#
	#

	def start(self, params = None, last_return = None):
	#
		"""
Starts all UPnP listeners and announces itself.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint.start()- (#echo(__LINE__)#)")

		self.http_host = Hooks.call("dNG.pas.http.server.get_host")
		self.http_port = Hooks.call("dNG.pas.http.server.get_port")
		if (self.http_host == None or self.http_port == None): raise RuntimeError("HTTP server must provide the hostname and port for the UPnP ControlPoint", 64)

		Hooks.load("upnp")

		with ControlPoint.synchronized:
		#
			self.bootid += 1

			ip_addresses = Settings.get("pas_upnp_bind_network_addresses")
			listener_addresses = 0

			if (type(ip_addresses) != list):
			#
				ip_addresses = [ ]

				if (Settings.get("pas_upnp_bind_network_detect_addresses", True)):
				#
					ip_address_paths = socket.getaddrinfo(self.http_host, None, socket.AF_UNSPEC, 0, socket.IPPROTO_UDP)

					for ip_address_data in ip_address_paths:
					#
						if (ip_address_data[0] == socket.AF_INET or (socket.has_ipv6 and ip_address_data[0])): ip_addresses.append(ip_address_data[4][0])
					#

					if (self.log_handler != None and len(ip_addresses) < 1): self.log_handler.warning("pas.upnp.ControlPoint was unable to find available networks")
				#
			#

			for ip_address in ip_addresses:
			#
				if (ip_address[:4] != "127." and ip_address != "::1"):
				#
					self._listeners_multicast_add(ip_address)
					listener_addresses += 1
				#
			#

			if (listener_addresses < 1):
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp.ControlPoint will bind to all interfaces")

				self._listeners_multicast_add("0.0.0.0")
				if (socket.has_ipv6): self._listeners_multicast_add("::0")
			#

			VirtualConfig.set_virtual_path("/upnp/", { "uri": "upnp_path", "uri_prefix": "/upnp/" }, self.handle_soap_request)
		#

		AbstractTimed.start(self)
		Hooks.call("dNG.pas.upnp.control_point.startup")
		if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint starts with bootid '{0:d}' and configid '{1:d}'".format(self.bootid, self.configid))

		return last_return
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Stops all UPnP listeners and deregisters itself.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint.stop()- (#echo(__LINE__)#)")

		Hooks.call("dNG.pas.upnp.control_point.shutdown")

		with ControlPoint.synchronized:
		#
			self._delete_usns(self.usns.copy())
			self.usns = { }

			VirtualConfig.unset_virtual_path("/upnp/")

			listeners_multicast = self.listeners_multicast.copy()
			for ip in listeners_multicast: self._listeners_multicast_remove(ip)
		#

		AbstractTimed.stop(self)
		if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint stopped")

		return last_return
	#

	def _task_add(self, wait_seconds, _type, **kwargs):
	#
		"""
Update the list with the given parsed UPnP identifier.

:param wait_seconds: Seconds to wait
:param _type: Task type to be added

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._task_add({0:.2f}, {1})- (#echo(__LINE__)#)".format(wait_seconds, _type))

		index = 1
		timestamp = int(time() + wait_seconds)

		with ControlPoint.synchronized:
		#
			if (wait_seconds > 600):
			#
				index = len(self.tasks)

				if (index > 0):
				#
					for position in range(index - 1, -1, -1):
					#
						if (timestamp > self.tasks[position]['timestamp']):
						#
							index = position
							break
						#
					#
				#
			#
			else:
			#
				index = None

				for position in range(0, len(self.tasks)):
				#
					if (timestamp < self.tasks[position]['timestamp']):
					#
						index = position
						break
					#
				#

				if (index == None): index = len(self.tasks)
			#

			task = kwargs
			task.update({ "timestamp": timestamp, "type": _type })
			self.tasks.insert(index, task)
		#

		if (index < 1): self.update_timestamp(timestamp)
	#

	def _tasks_remove(self, usn, _type = None):
	#
		"""
Delete the USN from the list of UPnP descriptions.

:param usn: UPnP USN
:param _type: Task type to be deleted

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._tasks_remove({0}, _type)- (#echo(__LINE__)#)".format(usn))

		with ControlPoint.synchronized:
		#
			index = len(self.tasks)

			if (index > 0):
			#
				tasks = (self.tasks.copy() if (hasattr(self.tasks, "copy")) else copy(self.tasks))
				tasks.reverse()

				for task in tasks:
				#
					index -= 1

					if (_type == None or task['type'] == _type):
					#
						if ("identifier" in task and usn == task['identifier']['usn']): self.tasks.pop(index)
						elif ("usn" in task and usn == task['usn']): self.tasks.pop(index)
					#
				#
			#
		#
	#

	def _update(self, servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, url, additional_data = None):
	#
		"""
Update the list with the given parsed UPnP identifier.

:param servername: UPnP server string
:param identifier: Parsed UPnP identifier
:param bootid: UPnP bootid (bootid.upnp.org) if any
:param bootid_old: Current UPnP bootid in case of ssdp:update
:param configid: UPnP configid (configid.upnp.org) if any
:param timeout: UPnP USN expire time
:param unicast_port: Received unicast port
:param http_version: HTTP request version
:param url: UPnP description location
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -ControlPoint._update({0}, identifier, bootid, bootid_old, configid, {1:d}, unicast_port, {2:.1f}, {3}, additional_data)- (#echo(__LINE__)#)".format(servername, timeout, http_version, url))

		url_base = Binary.str(urljoin(url, "."))
		usn_data = identifier.copy()
		usn_data.update({ "http_version": http_version, "ssdpname": servername, "unicast_port": unicast_port, "url_base": url_base, "url_desc": url })
		url_elements = urlsplit(url_base)

		ip_address_paths = socket.getaddrinfo(url_elements.hostname, url_elements.port, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

		if (len(ip_address_paths) > 0):
		#
			ips = [ ]

			for ip_address_data in ip_address_paths:
			#
				if (ip_address_data[0] == socket.AF_INET or ip_address_data[0] == socket.AF_INET6): ips.append(ip_address_data[4][0])
			#

			if (len(ips) > 0): usn_data['ips'] = ips
		#

		with ControlPoint.synchronized:
		#
			if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint updates USN '{0}'".format(identifier['usn']))

			is_update = False
			read_config = True

			if (identifier['usn'] in self.usns):
			#
				is_update = True

				if (bootid != None and bootid_old != None):
				#
					"""
Three possibilities:
1. It is a ssdp:alive and we are up-to-date
2. It is an unexpected ssdp:update
3. It is an expected ssdp:update and we do not need to reread the UPnP
   description.
					"""

					if (self.usns[identifier['usn']]['bootid'] == bootid): read_config = False
					elif (self.usns[identifier['usn']]['bootid'] != bootid_old): is_update = False
					else:
					#
						read_config = False
						self.usns[identifier['usn']]['bootid'] = bootid
					#
				#

				if (self.get_desc_xml(usn_data) == None):
				#
					for url in self.upnp_desc_unread:
					#
						if (identifier['usn'] in self.upnp_desc_unread[url]):
						#
							read_config = False
							break
						#
					#
				#
				else: read_config = False
			#

			if ("urn" in identifier):
			#
				if (identifier['device'] in self.devices):
				#
					if (identifier['usn'] not in self.devices[identifier['device']]): self.devices[identifier['device']].append(identifier['usn'])
					elif (not is_update): self.devices[identifier['device']].remove(identifier['usn'])
				#
				else: self.devices[identifier['device']] = [ identifier['usn'] ]
			#

			if (identifier['usn'] in self.usns):
			#
				if (is_update):
				#
					self.usns[identifier['usn']].update(usn_data)
					self._tasks_remove(identifier['usn'], "delete")
					self._task_add(timeout, "delete", identifier = identifier)
				#
				else: self._delete(identifier)
			#
			else:
			#
				self.usns[identifier['usn']] = usn_data
				self._task_add(timeout, "delete", identifier = identifier)
			#

			if (read_config):
			#
				if (url not in self.upnp_desc_unread): self.upnp_desc_unread[url] = [ identifier['usn'] ]
				elif (identifier['usn'] not in self.upnp_desc_unread[url]): self.upnp_desc_unread[url].append(identifier['usn'])

				self._task_add(0, "read_upnp_descs")
			#
		#
	#

	def update_usn(self, servername, usn, bootid, bootid_old, configid, timeout, unicast_port, http_version, url, additional_data = None):
	#
		"""
Update the list with the given USN.

:param servername: UPnP server string
:param usn: UPnP USN
:param bootid: UPnP bootid (bootid.upnp.org) if any
:param bootid_old: Current UPnP bootid in case of ssdp:update
:param configid: UPnP configid (configid.upnp.org) if any
:param timeout: UPnP USN expire time
:param unicast_port: Received unicast port
:param http_version: HTTP request version
:param url: UPnP description location
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (len(usn) > 41):
		#
			identifier = Device.get_identifier(usn, bootid, configid)

			if (identifier != None):
			#
				with ControlPoint.synchronized:
				#
					if (identifier['uuid'] not in self.managed_devices):
					#
						if (identifier['class'] == "rootdevice"): self.rootdevice_add(identifier['usn'], timeout)
						else: self._update(servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, url, additional_data)
					#
				#
			#
		#
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the control_point singleton.

:return: (ControlPoint) Object on success
:since:  v0.1.00
		"""

		_return = None

		with ControlPoint.synchronized:
		#
			if (ControlPoint.weakref_instance != None): _return = ControlPoint.weakref_instance()

			if (_return == None):
			#
				Settings.read_file("{0}/settings/pas_upnp.json".format(Settings.get("path_data")))
				_return = ControlPoint()

				ControlPoint.weakref_instance = ref(_return)
			#
		#

		return _return
	#
#

##j## EOF