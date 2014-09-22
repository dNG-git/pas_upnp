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

# pylint: disable=import-error,no-name-in-module

from copy import copy
from locale import getlocale
from platform import uname
from random import uniform as randfloat
from time import time
from threading import Thread
from weakref import ref
import re
import socket

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.net.http.client import Client as HttpClient
from dNG.pas.controller.abstract_http_request import AbstractHttpRequest
from dNG.pas.controller.http_upnp_request import HttpUpnpRequest
from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.upnp.control_point_event import ControlPointEvent
from dNG.pas.data.upnp.device import Device
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.exception_log_trap import ExceptionLogTrap
from dNG.pas.runtime.instance_lock import InstanceLock
from dNG.pas.runtime.value_exception import ValueException
from dNG.pas.tasks.abstract_timed import AbstractTimed
from .gena import Gena
from .ssdp_listener_ipv4_multicast import SsdpListenerIpv4Multicast
from .ssdp_listener_ipv6_multicast import SsdpListenerIpv6Multicast

class ControlPoint(AbstractTimed):
#
	"""
The UPnP control point.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	_instance_lock = InstanceLock()
	"""
Thread safety lock
	"""
	_weakref_instance = None
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
UPnP bootId value (bootid.upnp.org); nextbootid.upnp.org += 1
		"""
		self.configid = 0
		"""
UPnP configId value (configid.upnp.org)
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
		self.http_language = (L10n.get("lang_rfc_region") if (L10n.is_defined("lang_rfc_region")) else None)
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

		Settings.read_file("{0}/settings/pas_upnp.json".format(Settings.get("path_data")))

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

	def _activate_multicast_listener(self, ip):
	#
		"""
Activates all relevant multicast listeners based on the IP address given.

:param ip: IPv4 / IPv6 address

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._activate_multicast_listener({1})- (#echo(__LINE__)#)", self, ip, context = "pas_upnp")

		with self.lock:
		#
			if (ip not in self.listeners_multicast):
			#
				if (":" in ip):
				#
					listener = SsdpListenerIpv6Multicast(ip)
					listener.add_address("ff04::c")
					listener.add_address("ff05::c")
					listener.add_address("ff08::c")
					listener.add_address("ff0e::c")

					self.listeners_multicast[ip] = listener
					self.listeners_multicast_ipv6 += 1
				#
				else:
				#
					self.listeners_multicast[ip] = SsdpListenerIpv4Multicast(ip)
					self.listeners_multicast_ipv4 += 1
				#

				self.listeners_multicast[ip].start()
			#
		#
	#

	def add_device(self, device):
	#
		"""
Add a device to the managed list and announce it. Multiple hierarchies are not
supported and must be handled separately.

:param device: UPnP host device

:return: (bool) True if added successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_device()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = True

		if (isinstance(device, Device) and device.is_managed()):
		#
			with self.lock:
			#
				device_identifier = Device.get_identifier(device.get_usn(), self.bootid, self.configid)

				if (device_identifier != None and device_identifier['usn'] not in self.usns):
				#
					if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint adds UPnP device USN '{0}'", device_identifier['usn'], context = "pas_upnp")

					if (device_identifier['device'] not in self.rootdevices): self.rootdevices.append(device_identifier['device'])
					device_identifier['url_desc'] = device.get_desc_url()
					self.managed_devices[device_identifier['uuid']] = device
					self.usns[device_identifier['usn']] = device_identifier

					self._remove_task(device_identifier['usn'], "deliver_event")

					if (self.configid < 16777216): self.configid += 1
					else: self.configid = 0

					wait_seconds = randfloat(0.2, 0.4)

					event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_ALIVE, control_point = self)
					event.set_usn(device_identifier['usn'])
					event.set_location(device_identifier['url_desc'])
					event.schedule(wait_seconds)

					Hook.call("dNG.pas.upnp.ControlPoint.onHostDeviceAdded", identifier = device_identifier)

					embedded_device_uuids = device.get_embedded_device_uuids()

					for uuid in embedded_device_uuids:
					#
						embedded_device = device.get_embedded_device(uuid)
						embedded_device_identifier = Device.get_identifier(embedded_device.get_usn(), self.bootid, self.configid)
						if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint adds UPnP device USN '{0}'", embedded_device_identifier['usn'], context = "pas_upnp")

						embedded_device_identifier['url_desc'] = embedded_device.get_desc_url()
						self.managed_devices[embedded_device_identifier['uuid']] = embedded_device
						self.usns[embedded_device_identifier['usn']] = embedded_device_identifier

						wait_seconds = randfloat(0.4, 0.6)

						event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_ALIVE, control_point = self)
						event.set_usn(embedded_device_identifier['usn'])
						event.set_location(embedded_device_identifier['url_desc'])
						event.schedule(wait_seconds)

						Hook.call("dNG.pas.upnp.ControlPoint.onHostDeviceAdded", identifier = embedded_device_identifier)
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

	def add_http_client_name_to_ip(self, user_agent, ip):
	#
		"""
"User-Agent" HTTP header strings are often different to HTTP server and SSDP
ones. Keep track of them after their first query.

:param user_agent: "User-Agent" HTTP header value
:param ip: IP of the requesting host

:since: v0.1.01
		"""

		if (user_agent != None and user_agent != ""):
		#
			with self.lock:
			#
				for usn in self.usns:
				#
					if ("http_client_name" not in self.usns[usn]
					    and ip in self.usns[usn].get("ips", [ ])
					   ): self.usns[usn]['http_client_name'] = user_agent
				#
			#
		#
	#

	def add_rootdevice(self, usn, timeout):
	#
		"""
Add a rootdevice to the list of known root devices. It will automatically be
removed if the timeout expires.

:param usn: UPnP USN
		"""

		with self.lock:
		#
			identifier = Device.get_identifier(usn, self.bootid, self.configid)

			if (identifier['device'] in self.rootdevices):
			#
				if (self.log_handler != None): self.log_handler.debug("{0!r} renews TTL for UPnP root device USN '{1}' (TTL '{2:d}')", self, usn, timeout, context = "pas_upnp")

				self._remove_task(usn, "remove_rootdevice")
				self._add_task(timeout, "remove_rootdevice", usn = usn)
			#
			else:
			#
				if (self.log_handler != None): self.log_handler.debug("{0!r} adds UPnP root device USN '{1}' (TTL '{2:d}')", self, usn, timeout, context = "pas_upnp")

				self.rootdevices.append(identifier['device'])
				self._add_task(timeout, "remove_rootdevice", usn = usn)
			#
		#
	#

	def _add_task(self, wait_seconds, _type, **kwargs):
	#
		"""
Update the list with the given parsed UPnP identifier.

:param wait_seconds: Seconds to wait
:param _type: Task type to be added

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._add_task({1:.2f}, {2})- (#echo(__LINE__)#)", self, wait_seconds, _type, context = "pas_upnp")

		timestamp = int(time() + wait_seconds)

		with self.lock:
		#
			tasks_count = len(self.tasks)

			if (wait_seconds > 600):
			#
				index = 0

				if (tasks_count > 0):
				#
					for position in range((tasks_count - 1), -1, -1):
					#
						if (timestamp > self.tasks[position]['timestamp']):
						#
							index = 1 + position
							break
						#
					#
				#
			#
			else:
			#
				index = len(self.tasks)

				for position in range(0, tasks_count):
				#
					if (timestamp < self.tasks[position]['timestamp']):
					#
						index = position
						break
					#
				#
			#

			task = kwargs
			task.update({ "timestamp": timestamp, "type": _type })
			self.tasks.insert(index, task)
		#

		if (index < 1): self.update_timestamp(timestamp)
	#

	def _deactivate_multicast_listener(self, ip):
	#
		"""
Deactivates all relevant multicast listeners based on the IP address given.

:param ip: IPv4 / IPv6 address

:since: v0.1.01
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._deactivate_multicast_listener({1})- (#echo(__LINE__)#)", self, ip, context = "pas_upnp")

		with self.lock:
		#
			if (ip in self.listeners_multicast):
			#
				self.listeners_multicast[ip].stop()
				del(self.listeners_multicast[ip])

				if (":" in ip): self.listeners_multicast_ipv6 -= 1
				else: self.listeners_multicast_ipv4 -= 1
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._delete()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		with self.lock:
		#
			if (identifier['usn'] in self.usns and (identifier['bootid'] == None or self.usns[identifier['usn']]['bootid'] <= identifier['bootid'])):
			#
				usn_data = self.usns[identifier['usn']]

				if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint deletes USN '{0}'", identifier['usn'], context = "pas_upnp")

				if (usn_data['uuid'] in self.managed_devices):
				#
					if (self.configid < 16777216): self.configid += 1
					else: self.configid = 0

					event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_SHUTDOWN, control_point = self)
					event.set_usn(identifier['usn'])
					event.deliver()

					Hook.call("dNG.pas.upnp.ControlPoint.onHostDeviceRemoved", identifier = identifier)
					self._remove_task(identifier['usn'], "deliver_event")
					del(self.managed_devices[usn_data['uuid']])
				#
				elif ("url_desc_read" in usn_data):
				#
					if (self.gena != None and "ips" in usn_data):
					#
						for ip in usn_data['ips']: self.gena.cancel(("{0}:{1}:{2}".format(usn_data['domain'], usn_data['class'], usn_data['type']) if ("urn" in usn_data) else None), ip)
					#

					if (usn_data['class'] == "device"): Hook.call("dNG.pas.upnp.ControlPoint.onDeviceRemoved", identifier = usn_data)
					Hook.call("dNG.pas.upnp.ControlPoint.onUsnRemoved", identifier = usn_data)
				#

				self._delete_upnp_desc(identifier)

				"""
Always delete the device itself first. Known related devices and services
can be safely deleted afterwards.
				"""

				self._remove_task(identifier['usn'])
				del(self.usns[identifier['usn']])

				if (identifier['device'] in self.devices):
				#
					if (identifier['usn'] in self.devices[identifier['device']]): self.devices[identifier['device']].remove(identifier['usn'])

					if (self.is_rootdevice_known(device = identifier['device'])):
					#
						self.remove_rootdevice(identifier['usn'])

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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._delete_upnp_desc()- (#echo(__LINE__)#)", self, context = "pas_upnp")

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
:param bootid: UPnP bootId (bootid.upnp.org) if any
:param configid: UPnP configId (configid.upnp.org) if any
:param url: UPnP description location
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.delete_usn({1})- (#echo(__LINE__)#)", self, usn, context = "pas_upnp")

		if (len(usn) > 41):
		#
			identifier = Device.get_identifier(usn, bootid, configid)

			if (identifier != None):
			#
				with self.lock:
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._delete_usns()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		with self.lock:
		#
			for usn in usns:
			#
				if (usn in self.usns): self._delete(self.usns[usn])
			#
		#
	#

	def get_bootid(self):
	#
		"""
Returns the UPnP bootId value (bootid.upnp.org).

:return: (int) UPnP bootId value (bootid.upnp.org)
:since:  v0.1.02
		"""

		return self.bootid
	#

	def get_configid(self):
	#
		"""
Returns the UPnP configId value (configid.upnp.org).

:return: (int) UPnP configId value (configid.upnp.org)
:since:  v0.1.02
		"""

		return self.configid
	#

	def get_desc_xml(self, identifier):
	#
		"""
Returns the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		with self.lock:
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

	def get_device(self, identifier):
	#
		"""
Returns a UPnP device for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		# pylint: disable=maybe-no-member

		_return = None

		device = self.get_rootdevice(identifier)

		if (device != None):
		#
			if (device.get_udn() == identifier['uuid']): _return = device
			else: _return = device.get_embedded_device(identifier['uuid'])

			if (_return != None and _return.is_managed()): _return.set_configid(self.configid)
		#

		return _return
	#

	def get_http_client_name_of_ip(self, ip):
	#
		"""
Returns the known "User-Agent" HTTP header value previously recorded for
the given IP.

:param ip: IP of the requesting host

:return: (str) "User-Agent" HTTP header value if known; None otherwise
:since:  v0.1.01
		"""

		_return = None

		with self.lock:
		#
			for usn in self.usns:
			#
				if (ip in self.usns[usn].get("ips", [ ])):
				#
					if ("http_client_name" in self.usns[usn]): _return = self.usns[usn]['http_client_name']
					break
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

	def get_http_server_name_of_ip(self, ip):
	#
		"""
Returns the known "Server" HTTP header value for the given IP.

:param ip: IP to look up

:return: (str) "Server" HTTP header value if known; None otherwise
:since:  v0.1.01
		"""

		_return = None

		with self.lock:
		#
			for usn in self.usns:
			#
				if (ip in self.usns[usn].get("ips", [ ])):
				#
					if ("http_server_name" in self.usns[usn]): _return = self.usns[usn]['http_server_name']
					break
				#
			#
		#

		return _return
	#

	def _get_next_update_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.00
		"""

		with self.lock:
		#
			if (len(self.tasks) > 0): _return = self.tasks[0]['timestamp']
			else: _return = -1
		#

		return _return
	#

	def get_managed_devices(self):
	#
		"""
Returns all UPnP devices managed by this ControlPoint instance.

:return: (dict) Dict with UUID as key and device instance as value
:since:  v0.1.03
		"""

		return self.managed_devices.copy()
	#

	def get_rootdevice(self, identifier):
	#
		"""
Returns a UPnP rootdevice for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		with self.lock:
		#
			if (identifier['class'] == "device" and identifier['usn'] in self.usns):
			#
				if (identifier['uuid'] in self.managed_devices):
				#
					if (self.log_handler != None): self.log_handler.debug("{0!r} got request to return the hosted device '{1}'", self, identifier['usn'], context = "pas_upnp")
					_return = self.managed_devices[identifier['uuid']]
					_return.set_configid(self.configid)
				#
				else:
				#
					if (self.log_handler != None): self.log_handler.debug("{0!r} got request to create an object for device '{1}'", self, identifier['usn'], context = "pas_upnp")

					_return = (NamedLoader.get_instance("dNG.pas.data.upnp.devices.{0}".format(identifier['type']), False) if (identifier['class'] == "device") else None)
					if (_return == None): _return = Device()
					if (_return.init_xml_desc(self.usns[identifier['usn']], self.get_desc_xml(identifier)) == False): _return = None
				#
			#
		#

		return _return
	#

	def get_rootdevice_for_host(self, host):
	#
		"""
Returns a UPnP rootdevice for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		_return = None

		ip_address_list = socket.getaddrinfo(host, None, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

		for ip_address_data in ip_address_list:
		#
			ip = ip_address_data[4][0]

			if (self.is_ip_allowed(ip)):
			#
				with self.lock:
				#
					for usn in self.usns:
					#
						if (ip in self.usns[usn].get("ips", [ ])):
						#
							_return = self.get_rootdevice(self.usns[usn])
							break
						#
					#
				#
			#

			if (_return != None): break
		#

		return _return
	#

	def get_ssdp_server_name_of_ip(self, ip):
	#
		"""
Returns the known "Server" SSDP header value for the given IP.

:param ip: IP to look up

:return: (str) "Server" SSDP header value if known; None otherwise
:since:  v0.1.01
		"""

		_return = None

		with self.lock:
		#
			for usn in self.usns:
			#
				if (ip in self.usns[usn].get("ips", [ ])):
				#
					if ("ssdp_server_name" in self.usns[usn]): _return = self.usns[usn]['ssdp_server_name']
					break
				#
			#
		#

		return _return
	#

	def handle_soap_request(self, http_request, virtual_config):
	#
		"""
Returns the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_soap_request()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		if (not isinstance(http_request, AbstractHttpRequest)): raise TranslatableException("pas_http_core_400", 400)

		client_host = http_request.get_client_host()
		is_allowed = False
		is_valid = False

		if (client_host == None): is_allowed = True
		else:
		#
			ip_address_list = socket.getaddrinfo(client_host, http_request.get_client_port(), socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)
			is_allowed = (False if (len(ip_address_list) < 1) else self.is_ip_allowed(ip_address_list[0][4][0]))
		#

		if (is_allowed):
		#
			virtual_path = http_request.get_dsd("upnp_path")

			if (virtual_path != None):
			#
				with self.lock:
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
						elif (request_data_length > 2 and (request_data[2] == "control" or request_data[2] == "eventsub" or request_data[2] == "xml") and device.get_service(request_data[1]) != None): is_valid = True
					#
				#
			#
		#

		if (not is_allowed):
		#
			if (self.log_handler != None): self.log_handler.warning("pas.upnp.ControlPoint refused client '{0}'", client_host, context = "pas_upnp")

			_return = PredefinedHttpRequest()
			_return.set_output_handler("http_upnp")
			_return.set_module("output")
			_return.set_service("http")
			_return.set_action("error")
			_return.set_dsd("code", "403")
		#
		elif (not is_valid):
		#
			_return = PredefinedHttpRequest()
			_return.set_output_handler("http_upnp")
			_return.set_module("output")
			_return.set_service("http")
			_return.set_action("error")
			_return.set_dsd("code", "400")
		#
		else:
		#
			_return = HttpUpnpRequest()
			_return.set_request(http_request, self, device, request_data)
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

		if (not Settings.get("pas_upnp_allowed_networks_only", True)): _return = True
		elif (allowed_networks == None):
		#
			with self.lock:
			#
				for usn in self.usns:
				#
					if (ip in self.usns[usn].get("ips", [ ])):
					#
						_return = True
						break
					#
				#
			#
		#
		else:
		#
			for network_prefix in allowed_networks:
			#
				if (":" in network_prefix):
				#
					if (network_prefix[-2:] != "::"): network_prefix += "::"
				#
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

	def is_listening_ipv4(self):
	#
		"""
Returns true if the UPnP control point is listening on an IPv4 address.

:return: (bool) True if listening at IPv4 addresses
:since:  v0.1.02
		"""

		return (self.listeners_multicast_ipv4 > 0)
	#

	def is_listening_ipv6(self):
	#
		"""
Returns true if the UPnP control point is listening on an IPv6 address.

:return: (bool) True if listening at IPv6 addresses
:since:  v0.1.02
		"""

		return (self.listeners_multicast_ipv6 > 0)
	#

	def is_rootdevice_known(self, **kwargs):
	#
		"""
Check if a given UPnP UUID is a known rootdevice.
		"""

		if ("device" in kwargs): _return = (kwargs['device'] in self.rootdevices)
		elif ("usn" in kwargs):
		#
			identifier = Device.get_identifier(kwargs['usn'], self.bootid, self.configid)
			_return = (identifier['uuid'] in self.rootdevices)
		#
		elif ("uuid" in kwargs): _return = (kwargs['uuid'].lower().replace("-", "") in self.rootdevices)
		else: _return = False

		return _return
	#

	def _read_upnp_descs(self):
	#
		"""
Parse unread UPnP descriptions.

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._read_upnp_descs()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		with self.lock:
		#
			upnp_desc_unread = self.upnp_desc_unread.copy()
			self.upnp_desc_unread.clear()
		#

		os_uname = uname()

		for url in upnp_desc_unread:
		#
			if (self.log_handler != None): self.log_handler.debug("{0!r} reads UPnP device description from '{1}'", self, url, context = "pas_upnp")

			usns = upnp_desc_unread[url]

			http_client = HttpClient(url, event_handler = self.log_handler)
			http_client.set_header("Accept-Language", self.http_language)
			http_client.set_header("User-Agent", "{0}/{1} UPnP/2.0 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))
			http_client.set_ipv6_link_local_interface(Settings.get("pas_global_ipv6_link_local_interface"))

			http_response = http_client.request_get()

			if (http_response.is_readable()):
			#
				with self.lock:
				#
					if (url in self.upnp_desc): self.upnp_desc[url]['xml_data'] = Binary.raw_str(http_response.read())
					else: self.upnp_desc[url] = { "xml_data": Binary.raw_str(http_response.read()), "usns": [ ] }

					for usn in usns:
					#
						if (usn in self.usns and usn not in self.upnp_desc[url]['usns']):
						#
							self.usns[usn]['url_desc_read'] = url
							self.usns[usn]['http_server_name'] = http_response.get_header("Server")

							self.upnp_desc[url]['usns'].append(usn)

							Hook.call("dNG.pas.upnp.ControlPoint.onUsnAdded", identifier = self.usns[usn])
							if (self.usns[usn]['class'] == "device"): Hook.call("dNG.pas.upnp.ControlPoint.onDeviceAdded", identifier = self.usns[usn])
						#
					#
				#
			#
			else:
			#
				if (self.log_handler != None): self.log_handler.error(http_response.get_error_message(), context = "pas_upnp")
				self._delete_usns(usns)
			#
		#
	#

	def remove_device(self, device):
	#
		"""
Remove a device from the managed list and announce the change.

:param device: UPnP host device

:return: (bool) True if added successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.remove_device()- (#echo(__LINE__)#)", self, context = "pas_upnp")
		_return = False

		if (isinstance(device, Device) and device.is_managed()):
		#
			with self.lock:
			#
				device_identifier = Device.get_identifier(device.get_usn(), self.bootid, self.configid)

				if (device_identifier != None and device_identifier['usn'] in self.usns):
				#
					self._delete(device_identifier)

					if (self.configid < 16777216): self.configid += 1
					else: self.configid = 0

					for uuid in self.managed_devices:
					#
						if (device_identifier['uuid'] != uuid):
						#
							usn = "uuid:{0}::urn:{1}".format(self.managed_devices[uuid].get_udn(), self.managed_devices[uuid].get_urn())

							self._remove_task(usn, "deliver_event")

							event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_CONFIG_CHANGED, control_point = self)
							event.set_usn(usn)
							event.set_location(self.managed_devices[uuid].get_desc_url())
							event.schedule()
						#
					#

					if (len(self.managed_devices) < 1 and self.gena != None): self.gena = None
					_return = True
				#
			#
		#

		return _return
	#

	def remove_rootdevice(self, usn):
	#
		"""
Remove a rootdevice from the list of known root devices.

:param usn: UPnP USN
		"""

		identifier = Device.get_identifier(usn, self.bootid, self.configid)

		with self.lock:
		#
			if (identifier['device'] in self.rootdevices):
			#
				if (self.log_handler != None): self.log_handler.debug("{0!r} removes UPnP root device USN '{1}'", self, usn, context = "pas_upnp")

				self.rootdevices.remove(identifier['device'])
				self._remove_task(usn, "remove_rootdevice")
			#
		#
	#

	def _remove_task(self, usn, _type = None):
	#
		"""
Delete the USN from the list of UPnP descriptions.

:param usn: UPnP USN
:param _type: Task type to be deleted

:since: v0.1.00
		"""

		# pylint: disable=no-member

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._remove_task({1})- (#echo(__LINE__)#)", self, usn, context = "pas_upnp")

		with self.lock:
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
						elif (usn == task.get("usn")): self.tasks.pop(index)
					#
				#
			#
		#
	#

	def run(self):
	#
		"""
Timed task execution

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		task = None

		if (self.timer_active):
		#
			with self.lock:
			#
				if (len(self.tasks) > 0 and self.tasks[0]['timestamp'] <= time()): task = self.tasks.pop(0)
				AbstractTimed.run(self)
			#
		#

		if (task != None):
		#
			with ExceptionLogTrap("pas_upnp"):
			#
				if (self.log_handler != None): self.log_handler.debug("{0!r} runs task type '{1}'", self, task['type'], context = "pas_upnp")

				thread = None

				if (task['type'] == "delete"): self._delete(task['identifier'])
				elif (task['type'] == "deliver_event"): thread = task['event']
				elif (task['type'] == "read_upnp_descs"): thread = Thread(target = self._read_upnp_descs)
				elif (task['type'] == "remove_rootdevice"): self.remove_rootdevice(task['usn'])

				if (thread != None): thread.start()
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

		# pylint: disable=broad-except

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.start()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		# Set bootid and configid to a value between 0 and 16777215
		startupid = int(time()) % 16777216

		self.bootid = startupid
		self.configid = startupid

		preferred_host = Settings.get("pas_upnp_server_preferred_host")
		preferred_port = Settings.get("pas_upnp_server_preferred_port")

		upnp_http_host = (Hook.call("dNG.pas.http.Server.getHost")
		                  if (preferred_host == None) else
		                  preferred_host
		                 )

		if (Settings.get("pas_upnp_server_bind_host_to_ipv4", False)):
		#
			try: upnp_http_host = socket.gethostbyname(upnp_http_host)
			except socket.error as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.debug(handled_exception)
			#
		#

		self.http_host = upnp_http_host

		self.http_port = (Hook.call("dNG.pas.http.Server.getPort")
		                  if (preferred_port == None) else
		                  preferred_port
		                 )

		if (self.http_host == None or self.http_port == None): raise ValueException("HTTP server must provide the hostname and port for the UPnP ControlPoint")

		if (not Settings.is_defined("pas_http_site_preferred_url_base_upnp")):
		#
			Settings.set("pas_http_site_preferred_url_base_upnp",
			             "http://{0}:{1:d}".format(self.http_host, self.http_port)
			            )
		#

		Hook.load("upnp")

		with self.lock:
		#
			self.bootid += 1

			ip_addresses = Settings.get("pas_upnp_bind_network_addresses", [ ])
			if (type(ip_addresses) != list): ip_addresses = [ ]

			listener_addresses = 0

			if (len(ip_addresses) < 1 and Settings.get("pas_upnp_bind_network_addresses_detect", True)):
			#
				ip_address_list = socket.getaddrinfo(None, self.listener_port, socket.AF_UNSPEC, 0, socket.IPPROTO_UDP)
				ip_address_list += socket.getaddrinfo(self.http_host, self.http_port, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

				for ip_address_data in ip_address_list:
				#
					if ((ip_address_data[0] == socket.AF_INET
					     or (socket.has_ipv6 and ip_address_data[0] == socket.AF_INET6)
					    )
					    and ip_address_data[4][0] not in ip_addresses
					   ): ip_addresses.append(ip_address_data[4][0])
				#

				if (self.log_handler != None and len(ip_addresses) < 1): self.log_handler.warning("pas.upnp.ControlPoint was unable to find available networks", context = "pas_upnp")
			#

			for ip_address in ip_addresses:
			#
				if (ip_address[:4] != "127." and ip_address != "::1"):
				# Accept user defined or discovered list of IP addresses to listen on to fail on startup
					try:
					#
						self._activate_multicast_listener(ip_address)
						listener_addresses += 1
					#
					except Exception: pass
				#
			#

			if (listener_addresses < 1):
			#
				if (self.log_handler != None): self.log_handler.debug("{0!r} will bind to all interfaces", self, context = "pas_upnp")

				self._activate_multicast_listener("0.0.0.0")
				if (socket.has_ipv6): self._activate_multicast_listener("::0")
			#

			VirtualConfig.set_virtual_path("/upnp/", { "path": "upnp_path" }, self.handle_soap_request)
		#

		AbstractTimed.start(self)
		Hook.call("dNG.pas.upnp.ControlPoint.onStartup")
		if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint starts with bootId '{0:d}' and configId '{1:d}'", self.bootid, self.configid, context = "pas_upnp")

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

		Hook.call("dNG.pas.upnp.ControlPoint.onShutdown")

		AbstractTimed.stop(self)

		with self.lock:
		#
			self._delete_usns(self.usns.copy())
			self.usns = { }

			VirtualConfig.unset_virtual_path("/upnp/")

			listeners_multicast = self.listeners_multicast.copy()
			for ip in listeners_multicast: self._deactivate_multicast_listener(ip)
		#

		return last_return
	#

	def _update(self, servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, location_url, additional_data = None):
	#
		"""
Update the list with the given parsed UPnP identifier.

:param servername: UPnP server string
:param identifier: Parsed UPnP identifier
:param bootid: UPnP bootId (bootid.upnp.org) if any
:param bootid_old: Current UPnP bootId in case of ssdp:update
:param configid: UPnP configId (configid.upnp.org) if any
:param timeout: UPnP USN expire time
:param unicast_port: Received unicast port
:param http_version: HTTP request version
:param location_url: UPnP location URL
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._update({1}, {2:d}, {3:.1f}, {4})- (#echo(__LINE__)#)", self, servername, timeout, http_version, location_url, context = "pas_upnp")

		url_base = location_url.rsplit("/", 1)[0]
		usn_data = identifier.copy()
		usn_data.update({ "http_version": http_version, "ssdp_server_name": servername, "unicast_port": unicast_port })
		url_elements = urlsplit(url_base)

		is_url_desc_available = (url_elements.scheme != "ssdp")

		if (is_url_desc_available):
		#
			usn_data['url_base'] = url_base
			usn_data['url_desc'] = location_url
		#

		ip_address_list = (socket.getaddrinfo(url_elements.hostname, None)
		                   if (url_elements.scheme == "ssdp") else
		                   socket.getaddrinfo(url_elements.hostname,
		                                      url_elements.port,
		                                      socket.AF_UNSPEC,
		                                      0,
		                                      socket.IPPROTO_TCP
		                                     )
		                  )

		if (len(ip_address_list) > 0):
		#
			ips = [ ]

			for ip_address_data in ip_address_list:
			#
				if (ip_address_data[0] == socket.AF_INET or ip_address_data[0] == socket.AF_INET6): ips.append(ip_address_data[4][0])
			#

			if (len(ips) > 0): usn_data['ips'] = ips
		#

		with self.lock:
		#
			if (self.log_handler != None): self.log_handler.info("pas.upnp.ControlPoint updates USN '{0}'", identifier['usn'], context = "pas_upnp")

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
				elif (is_url_desc_available and self.get_desc_xml(usn_data) == None):
				#
					for desc_url in self.upnp_desc_unread:
					#
						if (identifier['usn'] in self.upnp_desc_unread[desc_url]):
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
					self._remove_task(identifier['usn'], "delete")
					self._add_task(timeout, "delete", identifier = identifier)
				#
				else: self._delete(identifier)
			#
			else:
			#
				self.usns[identifier['usn']] = usn_data
				self._add_task(timeout, "delete", identifier = identifier)
			#

			if (not is_url_desc_available):
			#
				Hook.call("dNG.pas.upnp.ControlPoint.onUsnAdded", identifier = identifier)
				if (identifier['class'] == "device"): Hook.call("dNG.pas.upnp.ControlPoint.onDeviceAdded", identifier = identifier)
			#
			elif (read_config):
			#
				if (location_url not in self.upnp_desc_unread): self.upnp_desc_unread[location_url] = [ identifier['usn'] ]
				elif (identifier['usn'] not in self.upnp_desc_unread[location_url]): self.upnp_desc_unread[location_url].append(identifier['usn'])

				self._add_task(0, "read_upnp_descs")
			#
		#
	#

	def update_usn(self, servername, usn, bootid, bootid_old, configid, timeout, unicast_port, http_version, location_url, additional_data = None):
	#
		"""
Update the list with the given USN.

:param servername: UPnP server string
:param usn: UPnP USN
:param bootid: UPnP bootId (bootid.upnp.org) if any
:param bootid_old: Current UPnP bootId in case of ssdp:update
:param configid: UPnP configId (configid.upnp.org) if any
:param timeout: UPnP USN expire time
:param unicast_port: Received unicast port
:param http_version: HTTP request version
:param location_url: UPnP location URL
:param additional_data: Additional data received

:since: v0.1.00
		"""

		if (len(usn) > 41):
		#
			identifier = Device.get_identifier(usn, bootid, configid)

			if (identifier != None):
			#
				with self.lock:
				#
					if (identifier['uuid'] not in self.managed_devices):
					#
						if (identifier['class'] == "rootdevice"): self.add_rootdevice(identifier['usn'], timeout)
						else: self._update(servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, location_url, additional_data)
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

		with ControlPoint._instance_lock:
		#
			if (ControlPoint._weakref_instance != None): _return = ControlPoint._weakref_instance()

			if (_return == None):
			#
				_return = ControlPoint()
				ControlPoint._weakref_instance = ref(_return)
			#
		#

		return _return
	#
#

##j## EOF