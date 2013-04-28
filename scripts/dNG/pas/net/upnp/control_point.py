# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.control_point
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
from socket import getfqdn
from threading import RLock
from time import time
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid
import re, socket

try: from urllib.parse import urljoin
except ImportError: from urlparse import urljoin

from dNG.data.rfc.basics import direct_basics as direct_rfc_basics
from dNG.data.rfc.http import direct_http
from dNG.pas.controller.predefined_request import direct_predefined_request
from dNG.pas.controller.upnp_request import direct_upnp_request
from dNG.pas.data.abstract_timed_tasks import direct_abstract_timed_tasks
from dNG.pas.data.settings import direct_settings
from dNG.pas.data.text.l10n import direct_l10n
from dNG.pas.data.upnp.device import direct_device
from dNG.pas.data.upnp.devices.callable_device import direct_callable_device
from dNG.pas.module.named_loader import direct_named_loader
from dNG.pas.net.http.virtual_config import direct_virtual_config
from dNG.pas.net.upnp.ssdp_message import direct_ssdp_message
from dNG.pas.net.upnp.ssdp_response import direct_ssdp_response
from dNG.pas.plugins.hooks import direct_hooks
from dNG.pas.pythonback import direct_str
from .ssdp_listener_ipv4_multicast import direct_ssdp_listener_ipv4_multicast
from .ssdp_listener_ipv6_multicast import direct_ssdp_listener_ipv6_multicast

class direct_control_point(direct_abstract_timed_tasks):
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
	ANNOUNCE_DEVICE_SHUTDOWN = 2
	ANNOUNCE_DEVICE_UPDATE = 3
	ANNOUNCE_SEARCH_RESULT = 4
	ANNOUNCE_SERVICE = 5
	REANNOUNCE_DEVICE = 6

	instance = None
	"""
ControlPoint instance
	"""
	ref_count = 0
	"""
Instances used
	"""
	synchronized = RLock()
	"""
Lock used in multi thread environments.
	"""

	def __init__(self):
	#
		"""
Constructor __init__(direct_control_point)

:since: v0.1.00
		"""

		direct_abstract_timed_tasks.__init__(self)

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
		self.http_host = None
		"""
HTTP Accept-Language value
		"""
		self.http_language = (direct_l10n.get("lang_iso") if (direct_l10n.is_defined("lang_iso")) else None)
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
		self.listener_port = int(direct_settings.get("pas_upnp_device_port", 1900))
		"""
Unicast port in the range 49152-65535 (searchport.upnp.org)
		"""
		self.listener_ipv4_multicast = None
		"""
Multicast IPv4 listener
		"""
		self.listener_ipv6_multicast_admin_local = None
		"""
Multicast IPv6 admin-local listener
		"""
		self.listener_ipv6_multicast_link_local = None
		"""
Multicast IPv6 link-local listener
		"""
		self.listener_ipv6_multicast_site_local = None
		"""
Multicast IPv6 site-local listener
		"""
		self.listener_ipv6_multicast_organisation_local = None
		"""
Multicast IPv6 organisation-local listener
		"""
		self.listener_ipv6_multicast_global = None
		"""
Multicast IPv6 global listener
		"""
		self.log_handler = direct_named_loader.get_singleton("dNG.pas.data.logging.log_handler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
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
		self.udn = direct_settings.get("pas_upnp_device_udn")
		"""
UPnP UDN
		"""
		self.upnp_desc = { }
		"""
Received UPnP descriptions
		"""
		self.upnp_desc_unread = { }
		"""
Unread UPnP description URLs
		"""
		self.urn = "schemas-direct-netware-de:device:CallableDevice:1"
		"""
UPnP URN as defined for the root device in "device_add()".
		"""
		self.usns = { }
		"""
List of devices with its services
		"""

		if (self.http_language == None):
		#
			system_language = getlocale()[0]
			http_language = re.sub("\\W", "", (direct_settings.get("core_lang", "en_US") if (system_language == None or system_language == "c") else system_language))
		#
		else: http_language = self.http_language.replace("_", "")

		if (direct_settings.is_defined("core_lang_{0}".format(http_language))): http_language = direct_settings.get("core_lang_{0}".format(http_language))
		elif (direct_settings.is_defined("core_lang_{0}".format(http_language[:2]))): http_language = direct_settings.get("core_lang_{0}".format(http_language[:2]))

		lang_iso_domain = http_language[:2]

		if (len(http_language) > 2): self.http_language = "{0}-{1}".format(http_language[:2], http_language[2:])
		else: self.http_language = http_language

		self.http_language += ", {0}".format(lang_iso_domain)
		if (lang_iso_domain != "en"): self.http_language += ", en-US, en"

		if (self.udn == None): self.udn = str(uuid(NAMESPACE_URL, "upnp://{0}:{1:d}".format(getfqdn(), self.listener_port)))
	#

	def announce(self, type, usn = None, location = None, additional_data = None):
	#
		"""
Announces host device changes over SSDP.

:param type: SSDP message type
:param usn: UPnP USN
:param location: Location of the UPnP description
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.announce(type, usn, location, additional_data)- (#echo(__LINE__)#)")

		if (usn == None): usn = "uuid:{0}::urn:{1}".format(self.udn, self.urn)
		identifier = direct_device.get_identifier(usn, self.bootid, self.configid)

		announce_targets = [ ]
		if (self.listener_ipv4_multicast.is_listening()): announce_targets.append("239.255.255.250")
		if (self.listener_ipv6_multicast_link_local.is_listening()): announce_targets.append("[ff02::c]")
		if (self.listener_ipv6_multicast_admin_local.is_listening()): announce_targets.append("[ff04::c]")
		if (self.listener_ipv6_multicast_site_local.is_listening()): announce_targets.append("[ff05::c]")
		if (self.listener_ipv6_multicast_organisation_local.is_listening()): announce_targets.append("[ff08::c]")
		if (self.listener_ipv6_multicast_global.is_listening()): announce_targets.append("[ff0e::c]")

		if (type == direct_control_point.ANNOUNCE_DEVICE_SHUTDOWN and identifier != None):
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
						ssdp_request = direct_ssdp_message(announce_target)
						ssdp_request.set_header("NTS", "ssdp:byebye")
						ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
						ssdp_request.set_header("USN", "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()))
						ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
						ssdp_request.send_notify()
					#
				#
			#

			for announce_target in announce_targets:
			#
				ssdp_request = direct_ssdp_message(announce_target)
				ssdp_request.set_header("NTS", "ssdp:byebye")
				ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
				ssdp_request.set_header("USN", usn)
				ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
				ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
				ssdp_request.send_notify()

				if (identifier['class'] == "device"):
				#
					ssdp_request = direct_ssdp_message(announce_target)
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
					ssdp_request.send_notify()
				#

				if (self.is_rootdevice(identifier['uuid'])):
				#
					ssdp_request = direct_ssdp_message(announce_target)
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "upnp:rootdevice")
					ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
					ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
					ssdp_request.send_notify()
				#
			#

			self.tasks_remove(identifier['usn'], "reannounce_device")
		#
		elif ((type == direct_control_point.ANNOUNCE_DEVICE or type == direct_control_point.REANNOUNCE_DEVICE) and identifier != None and location != None):
		#
			for announce_target in announce_targets:
			#
				ssdp_request = direct_ssdp_message(announce_target)
				ssdp_request.set_header("Cache-Control", "max-age=3600")
				ssdp_request.set_header("NTS", "ssdp:alive")
				ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
				ssdp_request.set_header("USN", usn)
				ssdp_request.set_header("LOCATION", location)
				ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
				ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
				ssdp_request.send_notify()

				if (identifier['class'] == "device"):
				#
					ssdp_request = direct_ssdp_message(announce_target)
					ssdp_request.set_header("Cache-Control", "max-age=3600")
					ssdp_request.set_header("NTS", "ssdp:alive")
					ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("LOCATION", location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
					ssdp_request.send_notify()
				#

				if (self.is_rootdevice(identifier['uuid'])):
				#
					ssdp_request = direct_ssdp_message(announce_target)
					ssdp_request.set_header("Cache-Control", "max-age=3600")
					ssdp_request.set_header("NTS", "ssdp:alive")
					ssdp_request.set_header("NT", "upnp:rootdevice")
					ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
					ssdp_request.set_header("LOCATION", location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
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
						ssdp_request = direct_ssdp_message(announce_target)
						ssdp_request.set_header("Cache-Control", "max-age=3600")
						ssdp_request.set_header("NTS", "ssdp:alive")
						ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
						ssdp_request.set_header("USN", "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn()))
						ssdp_request.set_header("LOCATION", location)
						ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
						ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
						ssdp_request.send_notify()
					#
				#
			#

			if (type == direct_control_point.ANNOUNCE_DEVICE): self.task_add(0.3, "reannounce_device", usn = usn, location = location)
			else:
			#
				wait_seconds = randint(600, 1800)
				self.task_add(wait_seconds, "reannounce_device", usn = usn, location = location)
			#
		#
		elif (type == direct_control_point.ANNOUNCE_SEARCH_RESULT and identifier != None and location != None and additional_data != None and "search_target" in additional_data and "target_host" in additional_data and "target_port" in additional_data):
		#
			ssdp_request = direct_ssdp_response(additional_data['target_host'], additional_data['target_port'])
			ssdp_request.set_header("Cache-Control", "max-age=3600")
			ssdp_request.set_header("Date", direct_rfc_basics.get_rfc1123_datetime(time()))
			ssdp_request.set_header("EXT", "")
			ssdp_request.set_header("ST", additional_data['search_target'])
			ssdp_request.set_header("USN", usn)
			ssdp_request.set_header("LOCATION", location)
			ssdp_request.set_header("BOOTID.UPNP.ORG", "{0:d}".format(self.bootid))
			ssdp_request.set_header("CONFIGID.UPNP.ORG", "{0:d}".format(self.configid))
			ssdp_request.send()
		#
	#

	def delete(self, identifier, additional_data = None):
	#
		"""
Delete the parsed UPnP identifier from the ControlPoint list.

:param identifier: Parsed UPnP identifier
:param additional_data: Additional data received

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.delete(identifier, additional_data)- (#echo(__LINE__)#)")

		direct_control_point.synchronized.acquire()

		if (identifier['usn'] in self.usns and (identifier['bootid'] == None or self.usns[identifier['usn']]['bootid'] <= identifier['bootid'])):
		#
			usn_data = self.usns[identifier['usn']]

			if (self.log_handler != None): self.log_handler.info("pas.upnp deletes USN '{0}'".format(identifier['usn']))

			if (usn_data['uuid'] in self.managed_devices):
			#
				direct_hooks.call("dNG.pas.upnp.control_point.host_device_remove", identifier = usn_data)
				self.announce(direct_control_point.ANNOUNCE_DEVICE_SHUTDOWN, identifier['usn'])
				del(self.managed_devices[usn_data['uuid']])
			#
			elif ("url_desc_read" in usn_data): direct_hooks.call("dNG.pas.upnp.control_point.usn_delete", identifier = usn_data)

			self.delete_upnp_desc(identifier)

			"""
Always delete the device itself first. Known related devices and services
can be safely deleted afterwards.
			"""

			self.tasks_remove(identifier['usn'])
			del(self.usns[identifier['usn']])

			if (identifier['device'] in self.devices):
			#
				if (identifier['usn'] in self.devices[identifier['device']]): self.devices[identifier['device']].remove(identifier['usn'])

				if (self.is_rootdevice(identifier['uuid'])):
				#
					self.rootdevice_remove(identifier['usn'])

					self.delete_usns(self.devices[identifier['device']])
					if (identifier['device'] in self.devices): del(self.devices[identifier['device']])
				#
			#
		#

		direct_control_point.synchronized.release()
	#

	def delete_upnp_desc(self, identifier):
	#
		"""
Delete the USN from the list of UPnP descriptions.

:param identifier: Parsed UPnP identifier

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.delete_upnp_desc(identifier)- (#echo(__LINE__)#)")

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
			identifier = direct_device.get_identifier(usn, bootid, configid)

			if (identifier != False):
			#
				direct_control_point.synchronized.acquire()
				if (identifier['usn'] in self.usns and identifier['uuid'] not in self.managed_devices): self.delete(identifier, additional_data)
				direct_control_point.synchronized.release()
			#
		#
	#

	def delete_usns(self, usns):
	#
		"""
Delete all USNs from the given list.

:param usns: USN list

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.delete_usns(usns)- (#echo(__LINE__)#)")

		direct_control_point.synchronized.acquire()

		for usn in usns:
		#
			if (usn in self.usns): self.delete(self.usns[usn])
		#

		direct_control_point.synchronized.release()
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.device_add(device)- (#echo(__LINE__)#)")
		var_return = True

		if (isinstance(device, direct_device) and device.is_managed()):
		#
			direct_control_point.synchronized.acquire()

			device_identifier = direct_device.get_identifier("uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn()), self.bootid, self.configid)
			root_identifier = direct_device.get_identifier("uuid:{0}::urn:{1}".format(self.udn, self.urn), self.bootid, self.configid)

			if (root_identifier['usn'] not in self.usns):
			#
				root_device = direct_callable_device()

				if (not root_device.init_device(self, self.udn, self.configid)): var_return = False
				else:
				#
					if (self.log_handler != None): self.log_handler.info("pas.upnp adds UPnP root device with USN '{0}'".format(root_identifier['usn']))

					if (root_identifier['uuid'] not in self.rootdevices): self.rootdevices.append(root_identifier['uuid'])
					root_identifier['managed'] = True
					root_identifier['url_desc'] = root_device.get_desc_url()
					self.managed_devices[root_identifier['uuid']] = root_device
					self.usns[root_identifier['usn']] = root_identifier

					self.announce(direct_control_point.ANNOUNCE_DEVICE_SHUTDOWN)

					wait_seconds = randfloat(0.2, 0.4)
					self.task_add(wait_seconds, "announce_device", usn = root_identifier['usn'], location = root_identifier['url_desc'])

					if (self.log_handler != None): self.log_handler.info("pas.upnp adds UPnP device with USN '{0}'".format(device_identifier['usn']))
					root_device.embedded_device_add(device)

					device_identifier['managed'] = True
					device_identifier['url_desc'] = device.get_desc_url()
					self.managed_devices[device_identifier['uuid']] = device
					self.usns[device_identifier['usn']] = device_identifier

					wait_seconds = randfloat(0.4, 0.6)
					self.task_add(wait_seconds, "announce_device", usn = device_identifier['usn'], location = device_identifier['url_desc'])

					direct_hooks.call("dNG.pas.upnp.control_point.host_device_add", identifier = device_identifier)
				#
			#
			else:
			#
				if (self.configid < 16777216): self.configid += 1
				else: self.configid = 0

				root_device = self.managed_devices[root_identifier['uuid']]

				if (device_identifier['usn'] in self.usns): root_device.embedded_device_remove(device)
				root_device.embedded_device_add(device)

				device_identifier['managed'] = True
				device_identifier['url_desc'] = device.get_desc_url()
				self.managed_devices[device_identifier['uuid']] = device
				self.usns[device_identifier['usn']] = device_identifier

				for uuid in self.managed_devices:
				#
					if (device_identifier['uuid'] != uuid):
					#
						usn = "uuid:{0}::urn:{1}".format(self.managed_devices[uuid].get_udn(), self.managed_devices[uuid].get_urn())
						self.tasks_remove(usn, "reannounce_device")
						self.announce(direct_control_point.REANNOUNCE_DEVICE, usn, self.managed_devices[uuid].get_desc_url())
					#
				#

				if (device_identifier['usn'] in self.usns):
				#
					self.tasks_remove(device_identifier['usn'], "reannounce_device")
					self.announce(direct_control_point.REANNOUNCE_DEVICE, device_identifier['usn'], device_identifier['url_desc'])
				#
				else:
				#
					wait_seconds = randfloat(0.4, 0.6)
					self.task_add(wait_seconds, "announce_device", usn = device_identifier['usn'], location = device_identifier['url_desc'])
				#
			#

			direct_control_point.synchronized.release()
		#
		else: var_return = False

		return var_return
	#

	def device_get(self, identifier):
	#
		"""
Return a UPnP device for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		var_return = None

		device = self.rootdevice_get(identifier)

		if (device != None):
		#
			if (device.get_udn() == identifier['uuid']): var_return = device
			else: var_return = device.embedded_device_get(identifier['uuid'])

			if (var_return != None and var_return.is_managed()): var_return.set_configid(self.configid)
		#

		return var_return
	#

	def device_remove(self, device):
	#
		"""
Remove a device from the managed list and announce the change.

:param device: UPnP host device

:return: (bool) True if added successfully
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.device_remove(device)- (#echo(__LINE__)#)")
		var_return = False

		if (isinstance(device, direct_device) and device.is_managed()):
		#
			direct_control_point.synchronized.acquire()

			device_identifier = direct_device.get_identifier("uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn()), self.bootid, self.configid)
			root_identifier = direct_device.get_identifier("uuid:{0}::urn:{1}".format(self.udn, self.urn), self.bootid, self.configid)

			if (root_identifier['usn'] in self.usns and device_identifier['usn'] in self.usns):
			#
				root_device = self.managed_devices[root_identifier['uuid']]

				if (self.configid < 16777216): self.configid += 1
				else: self.configid = 0

				if (device_identifier['usn'] in self.usns): root_device.embedded_device_remove(device)
				self.delete(device_identifier)

				for uuid in self.managed_devices:
				#
					if (device_identifier['uuid'] != uuid):
					#
						usn = "uuid:{0}::urn:{1}".format(self.managed_devices[uuid].get_udn(), self.managed_devices[uuid].get_urn())
						self.tasks_remove(usn, "reannounce_device")
						self.announce(direct_control_point.REANNOUNCE_DEVICE, usn, self.managed_devices[uuid].get_desc_url())
					#
				#

				var_return = True
			#

			direct_control_point.synchronized.release()
		#

		return var_return
	#

	def is_rootdevice(self, uuid):
	#
		"""
Check if a given UPnP UUID is a known rootdevice.
		"""

		return (uuid in self.rootdevices)
	#

	def get_desc_xml(self, identifier):
	#
		"""
Return the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		var_return = None

		direct_control_point.synchronized.acquire()

		if ("url_desc_read" in identifier and identifier['url_desc_read'] in self.upnp_desc): var_return = self.upnp_desc[identifier['url_desc_read']]['xml_data']
		elif ("url_desc" in identifier and identifier['url_desc'] in self.upnp_desc): var_return = self.upnp_desc[identifier['url_desc']]['xml_data']
		else:
		#
			for url in self.upnp_desc:
			#
				if (identifier['usn'] in self.upnp_desc[url]['usns']):
				#
					var_return = self.upnp_desc[url]['xml_data']
					break
				#
			#
		#

		direct_control_point.synchronized.release()

		return var_return
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

	def get_update_next_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:access: protected
:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.00
		"""

		direct_control_point.synchronized.acquire()

		if (len(self.tasks) > 0): var_return = self.tasks[0]['timestamp']
		else: var_return = -1

		direct_control_point.synchronized.release()

		return var_return
	#

	def handle_soap_request(self, http_wsgi_request, virtual_config):
	#
		"""
Return the raw XML UPnP description for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.handle_soap_request(http_wsgi_request, virtual_config)- (#echo(__LINE__)#)")

		is_valid = False
		virtual_path = http_wsgi_request.get_dsd("upnp_path")

		if (virtual_path != None):
		#
			direct_control_point.synchronized.acquire()

			request_data = virtual_path.split("/", 2)

			if (request_data[0] in self.managed_devices):
			#
				device = self.managed_devices[request_data[0]]
				request_data_length = len(request_data)

				if (request_data_length == 2 and request_data[1] == "desc"): is_valid = True
				elif (request_data_length > 2 and (request_data[2] == "control" or request_data[2] == "eventsub" or request_data[2] == "xml") and device.service_get(request_data[1]) != None): is_valid = True
			#

			direct_control_point.synchronized.release()
		#

		if (is_valid):
		#
			var_return = direct_upnp_request()
			var_return.set_request(http_wsgi_request, self, device, request_data)
		#
		else:
		#
			var_return = direct_predefined_request()
			var_return.set_module("output")
			var_return.set_service("http")
			var_return.set_action("error")
			var_return.set_dsd("code", "404")
		#

		return var_return
	#

	def read_upnp_descs(self):
	#
		"""
Parse unread UPnP descriptions.

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.read_upnp_descs()- (#echo(__LINE__)#)")

		direct_control_point.synchronized.acquire()

		upnp_desc_unread = self.upnp_desc_unread.copy()
		self.upnp_desc_unread.clear()

		direct_control_point.synchronized.release()

		for url in upnp_desc_unread:
		#
			usns = upnp_desc_unread[url]
			http_response = None

			try:
			#
				os_uname = uname()
				http_client = direct_http(url, event_handler = self.log_handler)
				http_client.set_header("Accept-Language", self.http_language)
				http_client.set_header("User-Agent", "{0}/{1} UPnP/1.1 pasUPnP/#echo(pasUPnPIVersion)#".format(os_uname[0], os_uname[2]))

				http_response = http_client.request_get()
				if (isinstance(http_response['body'], Exception)): raise http_response['body']
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
				self.delete_usns(usns)
			#

			if (http_response != None):
			#
				direct_control_point.synchronized.acquire()

				if (url in self.upnp_desc): self.upnp_desc[url]['xml_data'] = direct_str(http_response['body'])
				else: self.upnp_desc[url] = { "xml_data": direct_str(http_response['body']), "usns": [ ] }

				for usn in usns:
				#
					if (usn in self.usns and usn not in self.upnp_desc[url]['usns']):
					#
						self.usns[usn]['url_desc_read'] = url
						self.usns[usn]['httpname'] = (http_response['headers']['server'] if ("server" in http_response['headers']) else None)

						self.upnp_desc[url]['usns'].append(usn)

						direct_hooks.call("dNG.pas.upnp.control_point.usn_new", identifier = self.usns[usn])
					#
				#

				direct_control_point.synchronized.release()
			#
		#
	#

	def return_instance(self):
	#
		"""
The last "return_instance()" call will free the singleton reference.

:since: v0.1.00
		"""

		direct_control_point.synchronized.acquire()

		if (direct_control_point != None):
		#
			if (direct_control_point.ref_count > 0): direct_control_point.ref_count -= 1
			if (direct_control_point.ref_count == 0): direct_control_point.instance = None
		#

		direct_control_point.synchronized.release()
	#

	def rootdevice_add(self, usn, timeout):
	#
		"""
Add a rootdevice to the list of known root devices. It will automatically be
removed if the timeout expires.

:param usn: UPnP USN
		"""

		direct_control_point.synchronized.acquire()

		identifier = direct_device.get_identifier(usn, self.bootid, self.configid)

		if (identifier['uuid'] in self.rootdevices):
		#
			self.tasks_remove(usn, "rootdevice_remove")
			self.task_add(timeout, "rootdevice_remove", usn = usn)
		#
		else:
		#
			if (self.log_handler != None): self.log_handler.debug("pas.upnp adds UPnP root device with USN '{0}' (timeout {1:d})".format(usn, timeout))

			self.rootdevices.append(identifier['uuid'])
			self.task_add(timeout, "rootdevice_remove", usn = usn)
		#

		direct_control_point.synchronized.release()
	#

	def rootdevice_get(self, identifier):
	#
		"""
Return a UPnP rootdevice for the given identifier.

:param identifier: Parsed UPnP identifier

:return: (dict) Parsed UPnP identifier; False on error
:since:  v0.1.00
		"""

		var_return = None

		direct_control_point.synchronized.acquire()

		if (identifier['class'] == "device" and identifier['usn'] in self.usns):
		#
			if (identifier['uuid'] in self.managed_devices):
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp got request to return the hosted device '{0}'".format(identifier['usn']))
				var_return = self.managed_devices[identifier['uuid']]
				var_return.set_configid(self.configid)
			#
			else:
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp got request to create an object for device '{0}'".format(identifier['usn']))

				var_return = (direct_named_loader.get_instance("dNG.pas.data.upnp.devices.{0}".format(direct_device.RE_CAMEL_CASE_SPLITTER.sub("_\\1\\2", identifier['type']).lower()), False) if (identifier['class'] == "device") else None)
				if (var_return == None): var_return = direct_device()
				if (var_return.init_xml_desc(self.usns[identifier['usn']], self.get_desc_xml(identifier)) == False): var_return = None
			#
		#

		direct_control_point.synchronized.release()

		return var_return
	#

	def rootdevice_remove(self, usn):
	#
		"""
Remove a rootdevice from the list of known root devices.

:param usn: UPnP USN
		"""

		identifier = direct_device.get_identifier(usn, self.bootid, self.configid)

		direct_control_point.synchronized.acquire()

		if (identifier['uuid'] in self.rootdevices):
		#
			if (self.log_handler != None): self.log_handler.debug("pas.upnp removes UPnP root device with USN '{0}'".format(usn))

			self.rootdevices.remove(identifier['uuid'])
			self.tasks_remove(usn, "rootdevice_remove")
		#

		direct_control_point.synchronized.release()
	#

	def run(self):
	#
		"""
Worker loop

:access: protected
:since:  v0.1.00
		"""

		direct_control_point.synchronized.acquire()

		if (len(self.tasks) > 0 and self.tasks[0]['timestamp'] <= time()):
		#
			task = self.tasks.pop(0)
			direct_control_point.synchronized.release()

			try:
			#
				if (self.log_handler != None): self.log_handler.debug("pas.upnp runs task type '{0}'".format(task['type']))

				if (task['type'] == "announce_device"): self.announce(direct_control_point.ANNOUNCE_DEVICE, task['usn'], task['location'])
				elif (task['type'] == "announce_search_result"): self.announce(direct_control_point.ANNOUNCE_SEARCH_RESULT, task['usn'], task['location'], task)
				elif (task['type'] == "delete"): self.delete(task['identifier'])
				elif (task['type'] == "read_upnp_descs"): self.read_upnp_descs()
				elif (task['type'] == "reannounce_device"): self.announce(direct_control_point.REANNOUNCE_DEVICE, task['usn'], task['location'])
				elif (task['type'] == "rootdevice_remove"): self.rootdevice_remove(task['usn'])
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
			#
		#
		else: direct_control_point.synchronized.release()

		direct_abstract_timed_tasks.run(self)
	#

	def search(self, source_data, source_wait_timeout, search_target, additional_data = None):
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

		condition_identifier = None

		if (search_target == "ssdp:all" or search_target == "upnp:rootdevice" or search_target.startswith("uuid:")): condition = search_target
		elif (len(search_target) > 41):
		#
			condition = search_target
			condition_identifier = direct_device.get_identifier(search_target, None, None)
		#
		else: condition = False

		results = [ ]

		if (condition != False):
		#
			direct_control_point.synchronized.acquire()

			if (condition_identifier == None and condition == "upnp:rootdevice"):
			#
				usn = "uuid:{0}::urn:{1}".format(self.udn, self.urn)
				if (self.udn in self.managed_devices): results.append({ "usn": usn, "location": self.managed_devices[self.udn].get_desc_url(), "search_target": condition })
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
							if (self.is_rootdevice(uuid)): results.append({ "usn": "uuid:{0}::upnp:rootdevice".format(device.get_udn()), "location": device.get_desc_url(), "search_target": "upnp:rootdevice" })
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

			direct_control_point.synchronized.release()

			if (len(results) > 0):
			#
				wait_seconds = randfloat(0, source_wait_timeout / len(results))
				for result in results: self.task_add(wait_seconds, "announce_search_result", usn = result['usn'], location = result['location'], search_target = result['search_target'], target_host = ("[{0}]".format(source_data[0]) if (":" in source_data[0]) else source_data[0]), target_port = source_data[1])
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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.start()- (#echo(__LINE__)#)")

		self.http_host = direct_hooks.call("dNG.pas.http.server.get_host")
		self.http_port = direct_hooks.call("dNG.pas.http.server.get_port")
		if (self.http_host == None or self.http_port == None): raise RuntimeError("HTTP server must provide the hostname and port for the UPnP ControlPoint", 64)

		direct_hooks.load("upnp")

		direct_control_point.synchronized.acquire()

		self.bootid += 1

		if (self.listener_ipv4_multicast == None):
		#
			self.listener_ipv4_multicast = direct_ssdp_listener_ipv4_multicast()
			self.listener_ipv4_multicast.start()
		#

		if (socket.has_ipv6 and self.listener_ipv6_multicast_link_local == None):
		#
			self.listener_ipv6_multicast_link_local = direct_ssdp_listener_ipv6_multicast()
			self.listener_ipv6_multicast_link_local.start()
		#

		if (socket.has_ipv6 and self.listener_ipv6_multicast_admin_local == None):
		#
			self.listener_ipv6_multicast_admin_local = direct_ssdp_listener_ipv6_multicast("ff04::c")
			self.listener_ipv6_multicast_admin_local.start()
		#

		if (socket.has_ipv6 and self.listener_ipv6_multicast_site_local == None):
		#
			self.listener_ipv6_multicast_site_local = direct_ssdp_listener_ipv6_multicast("ff05::c")
			self.listener_ipv6_multicast_site_local.start()
		#

		if (socket.has_ipv6 and self.listener_ipv6_multicast_organisation_local == None):
		#
			self.listener_ipv6_multicast_organisation_local = direct_ssdp_listener_ipv6_multicast("ff08::c")
			self.listener_ipv6_multicast_organisation_local.start()
		#

		if (socket.has_ipv6 and self.listener_ipv6_multicast_global == None):
		#
			self.listener_ipv6_multicast_global = direct_ssdp_listener_ipv6_multicast("ff0e::c")
			self.listener_ipv6_multicast_global.start()
		#

		direct_virtual_config.set_virtual_path("/upnp/", { "uri": "upnp_path", "uri_prefix": "/upnp/" }, self.handle_soap_request)

		direct_control_point.synchronized.release()

		direct_abstract_timed_tasks.start(self)
		direct_hooks.call("dNG.pas.upnp.control_point.startup")
		if (self.log_handler != None): self.log_handler.info("pas.upnp server starts with bootid '{0:d}' and configid '{1:d}'".format(self.bootid, self.configid))
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Stops all UPnP listeners and deregisters itself.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.stop()- (#echo(__LINE__)#)")

		direct_hooks.call("dNG.pas.upnp.control_point.shutdown")

		direct_control_point.synchronized.acquire()

		self.delete_usns(self.usns.copy())
		self.usns = { }

		direct_virtual_config.unset_virtual_path("/upnp/")

		if (self.listener_ipv4_multicast != None):
		#
			self.listener_ipv4_multicast.stop()
			self.listener_ipv4_multicast = None
		#

		if (self.listener_ipv6_multicast_link_local != None):
		#
			self.listener_ipv6_multicast_link_local.stop()
			self.listener_ipv6_multicast_link_local = None
		#

		if (self.listener_ipv6_multicast_admin_local != None):
		#
			self.listener_ipv6_multicast_admin_local.stop()
			self.listener_ipv6_multicast_admin_local = None
		#

		if (self.listener_ipv6_multicast_site_local != None):
		#
			self.listener_ipv6_multicast_site_local.stop()
			self.listener_ipv6_multicast_site_local = None
		#

		if (self.listener_ipv6_multicast_organisation_local != None):
		#
			self.listener_ipv6_multicast_organisation_local.stop()
			self.listener_ipv6_multicast_organisation_local = None
		#

		if (self.listener_ipv6_multicast_global != None):
		#
			self.listener_ipv6_multicast_global.stop()
			self.listener_ipv6_multicast_global = None
		#

		direct_control_point.synchronized.release()

		direct_abstract_timed_tasks.stop(self)
		if (self.log_handler != None): self.log_handler.info("pas.upnp server stopped")
	#

	def task_add(self, wait_seconds, type, **kwargs):
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

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.task_add({0:.2f}, {1})- (#echo(__LINE__)#)".format(wait_seconds, type))

		direct_control_point.synchronized.acquire()

		timestamp = time() + wait_seconds

		if (wait_seconds > 600):
		#
			index = len(self.tasks)

			if (index > 0):
			#
				tasks = (self.tasks.copy() if (hasattr(self.tasks, "copy")) else copy(self.tasks))
				tasks.reverse()

				for task in tasks:
				#
					if (timestamp > task['timestamp']): break
					else: index -= 1
				#
			#
		#
		else:
		#
			index = 0

			for task in self.tasks:
			#
				if (timestamp < task['timestamp']): break
				else: index += 1
			#
		#

		task = kwargs
		task.update({ "timestamp": timestamp, "type": type })
		self.tasks.insert(index, task)

		direct_control_point.synchronized.release()

		if (index < 1): self.update_timestamp()
	#

	def tasks_remove(self, usn, type = None):
	#
		"""
Delete the USN from the list of UPnP descriptions.

:param usn: UPnP USN
:param type: Task type to be deleted

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.tasks_remove({0}, type)- (#echo(__LINE__)#)".format(usn))

		index = len(self.tasks)

		if (index > 0):
		#
			tasks = (self.tasks.copy() if (hasattr(self.tasks, "copy")) else copy(self.tasks))
			tasks.reverse()

			for task in tasks:
			#
				index -= 1

				if (type == None or task['type'] == type):
				#
					if ("identifier" in task and usn == task['identifier']['usn']): self.tasks.pop(index)
					elif ("usn" in task and usn == task['usn']): self.tasks.pop(index)
				#
			#
		#
	#

	def update(self, servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, url, additional_data = None):
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

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None):
		#
			self.log_handler.debug("#echo(__FILEPATH__)# -upnpControlPoint.update({0}, identifier, bootid, bootid_old, configid, {1:d}, unicast_port, {2:.1f}, {3}, additional_data)- (#echo(__LINE__)#)".format(servername, timeout, http_version, url))
			self.log_handler.info("pas.upnp updates USN '{0}'".format(identifier['usn']))
		#

		url_base = direct_str(urljoin(url, "."))

		usn_data = identifier.copy()
		usn_data.update({ "http_version": http_version, "ssdpname": servername, "unicast_port": unicast_port, "url_base": url_base, "url_desc": url })

		direct_control_point.synchronized.acquire()

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
				self.tasks_remove(identifier['usn'], "delete")

				self.task_add(timeout, "delete", identifier = identifier)
			#
			else: del(self.usns[identifier['usn']])
		#
		else:
		#
			self.usns[identifier['usn']] = usn_data
			self.task_add(timeout, "delete", identifier = identifier)
		#

		if (read_config):
		#
			if (url not in self.upnp_desc_unread): self.upnp_desc_unread[url] = [ identifier['usn'] ]
			elif (identifier['usn'] not in self.upnp_desc_unread[url]): self.upnp_desc_unread[url].append(identifier['usn'])

			self.task_add(0, "read_upnp_descs")
		#

		direct_control_point.synchronized.release()
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
			identifier = direct_device.get_identifier(usn, bootid, configid)

			if (identifier != False):
			#
				direct_control_point.synchronized.acquire()

				if (identifier['uuid'] not in self.managed_devices):
				#
					if (identifier['class'] == "rootdevice"): self.rootdevice_add(identifier['usn'], timeout)
					else: self.update(servername, identifier, bootid, bootid_old, configid, timeout, unicast_port, http_version, url, additional_data)
				#

				direct_control_point.synchronized.release()
			#
		#
	#

	@staticmethod
	def get_instance(count = True):
	#
		"""
Get the control_point singleton.

:param count: Count "get()" request

:return: (direct_control_point) Object on success
:since:  v0.1.00
		"""

		direct_control_point.synchronized.acquire()

		if (direct_control_point.instance == None): direct_control_point.instance = direct_control_point()
		if (count): direct_control_point.ref_count += 1

		direct_control_point.synchronized.release()

		return direct_control_point.instance
	#
#

##j## EOF