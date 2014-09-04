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

from random import randint
from time import time

from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.pas.data.settings import Settings
from dNG.pas.data.upnp.device import Device
from dNG.pas.net.upnp.ssdp_message import SsdpMessage
from dNG.pas.net.upnp.ssdp_response import SsdpResponse
from dNG.pas.runtime.value_exception import ValueException
from .abstract_event import AbstractEvent

class ControlPointEvent(AbstractEvent):
#
	"""
"ControlPointEvent" is the event class for UPnP control point related
events.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	TYPE_DEVICE_ALIVE = 1
	"""
Initial UPnP device announcement
	"""
	TYPE_DEVICE_CONFIG_CHANGED = 2
	"""
Premature UPnP device announcement with a changed UPnP configId value
	"""
	TYPE_DEVICE_REANNOUNCE_ALIVE = 3
	"""
Subsequent UPnP device announcement
	"""
	TYPE_DEVICE_SHUTDOWN = 4
	"""
UPnP device shutdown announcement
	"""
	TYPE_DEVICE_UPDATE = 5
	"""
UPnP device update announcement
	"""
	TYPE_SEARCH_RESULT = 6
	"""
Search result announcement
	"""

	def __init__(self, _type, control_point = None):
	#
		"""
Constructor __init__(ControlPointEvent)

:param _type: Event to be delivered
:param control_point: Control point scheduling delivery

:since: v0.1.03
		"""

		AbstractEvent.__init__(self, _type)

		self.announcement_divider = None
		"""
Divider for the announcements interval to set how many announcements will be within the interval
		"""
		self.announcement_interval = None
		"""
Announcement interval
		"""
		self.configid = None
		"""
UPnP configId value (configid.upnp.org)
		"""
		self.location = None
		"""
UPnP HTTP location URL
		"""
		self.search_target = None
		"""
M-SEARCH ST value
		"""
		self.target_host = None
		"""
M-SEARCH response target host
		"""
		self.target_port = None
		"""
M-SEARCH response target port
		"""
		self.usn = None
		"""
UPnP USN
		"""

		Settings.read_file("{0}/settings/pas_upnp.json".format(Settings.get("path_data")))

		self.announcement_divider = int(Settings.get("pas_upnp_announcement_divider", 3))
		self.announcement_interval = int(Settings.get("pas_upnp_announcement_interval", 3600))
		self.control_point = control_point
	#

	def _send(self):
	#
		"""
Send event.

:since: v0.1.03
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._send()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		bootid = self.control_point.get_bootid()
		configid = (self.control_point.get_configid() if (self.configid == None) else self.configid)

		identifier = Device.get_identifier(self.usn, bootid, configid)

		targets = [ ]
		if (self.control_point.is_listening_ipv4()): targets.append("239.255.255.250")
		if (self.control_point.is_listening_ipv6()): targets += [ "[ff02::c]", "[ff04::c]", "[ff05::c]", "[ff08::c]", "[ff0e::c]" ]

		if (self.type == ControlPointEvent.TYPE_DEVICE_SHUTDOWN):
		#
			device = self.control_point.get_device(identifier)

			services = ([ ] if (device == None) else device.get_unique_service_type_ids())

			for target in targets:
			#
				ssdp_request = SsdpMessage(target)

				for service_id in services:
				#
					service = device.get_service(service_id)

					ssdp_request.reset_headers()
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
					ssdp_request.set_header("USN", service.get_usn())
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#

				ssdp_request.reset_headers()
				ssdp_request.set_header("NTS", "ssdp:byebye")
				ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
				ssdp_request.set_header("USN", self.usn)
				ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
				ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
				ssdp_request.send_notify()

				if (identifier['class'] == "device"):
				#
					ssdp_request.reset_headers()
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#

				if (self.control_point.is_rootdevice_known(device = identifier['device'])):
				#
					ssdp_request.reset_headers()
					ssdp_request.set_header("NTS", "ssdp:byebye")
					ssdp_request.set_header("NT", "upnp:rootdevice")
					ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#
			#
		#
		elif (self.type in ( ControlPointEvent.TYPE_DEVICE_ALIVE,
		                     ControlPointEvent.TYPE_DEVICE_REANNOUNCE_ALIVE,
		                     ControlPointEvent.TYPE_DEVICE_CONFIG_CHANGED,
		                     ControlPointEvent.TYPE_DEVICE_UPDATE
		                   )
		     ):
		#
			if (self.location == None): raise ValueException("UPnP location value is required for ssdp:alive")

			device = self.control_point.get_device(identifier)
			if (device == None or (not device.is_managed())): raise ValueException("UPnP device is invalid")

			nts = ("ssdp:update" if (self.type == ControlPointEvent.TYPE_DEVICE_UPDATE) else "ssdp:alive")
			services = device.get_unique_service_type_ids()

			for target in targets:
			#
				ssdp_request = SsdpMessage(target)

				if (self.control_point.is_rootdevice_known(device = identifier['device'])):
				#
					ssdp_request.reset_headers()
					ssdp_request.set_header("Cache-Control", "max-age={0:d}".format(self.announcement_interval))
					ssdp_request.set_header("NTS", nts)
					ssdp_request.set_header("NT", "upnp:rootdevice")
					ssdp_request.set_header("USN", "uuid:{0}::upnp:rootdevice".format(identifier['uuid']))
					ssdp_request.set_header("LOCATION", self.location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#

				if (identifier['class'] == "device"):
				#
					ssdp_request.reset_headers()
					ssdp_request.set_header("Cache-Control", "max-age={0:d}".format(self.announcement_interval))
					ssdp_request.set_header("NTS", nts)
					ssdp_request.set_header("NT", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("USN", "uuid:{0}".format(identifier['uuid']))
					ssdp_request.set_header("LOCATION", self.location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#

				ssdp_request.reset_headers()
				ssdp_request.set_header("Cache-Control", "max-age={0:d}".format(self.announcement_interval))
				ssdp_request.set_header("NTS", nts)
				ssdp_request.set_header("NT", "urn:{0}".format(identifier['urn']))
				ssdp_request.set_header("USN", self.usn)
				ssdp_request.set_header("LOCATION", self.location)
				ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
				ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
				ssdp_request.send_notify()

				for service_id in services:
				#
					service = device.get_service(service_id)

					ssdp_request.reset_headers()
					ssdp_request.set_header("Cache-Control", "max-age={0:d}".format(self.announcement_interval))
					ssdp_request.set_header("NTS", nts)
					ssdp_request.set_header("NT", "urn:{0}".format(service.get_urn()))
					ssdp_request.set_header("USN", service.get_usn())
					ssdp_request.set_header("LOCATION", self.location)
					ssdp_request.set_header("BOOTID.UPNP.ORG", str(bootid))
					ssdp_request.set_header("CONFIGID.UPNP.ORG", str(configid))
					ssdp_request.send_notify()
				#
			#

			event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_REANNOUNCE_ALIVE, control_point = self.control_point)
			if (self.configid != None): event.set_configid(self.configid)
			event.set_usn(self.usn)
			event.set_location(self.location)

			if (self.type == ControlPointEvent.TYPE_DEVICE_ALIVE): event.schedule(0.3)
			else:
			#
				announcement_divider = (self.announcement_divider if (self.announcement_divider > 0) else 1)

				wait_seconds = randint(int(self.announcement_interval / (2 * announcement_divider)), int(self.announcement_interval / announcement_divider))
				event.schedule(wait_seconds)
			#
		#
		elif (self.type == ControlPointEvent.TYPE_SEARCH_RESULT):
		#
			if (self.location == None): raise ValueException("UPnP location value is required for M-SEARCH responses")
			if (self.search_target == None): raise ValueException("M-SEARCH ST value is invalid")
			if (self.target_host == None or self.target_port == None): raise ValueException("UPnP M-SEARCH response recipient address is invalid")

			ssdp_response = SsdpResponse(self.target_host, self.target_port)

			ssdp_response.set_header("Cache-Control", "max-age={0:d}".format(self.announcement_interval))
			ssdp_response.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
			ssdp_response.set_header("EXT", "")
			ssdp_response.set_header("ST", self.search_target)
			ssdp_response.set_header("USN", self.usn)
			ssdp_response.set_header("LOCATION", self.location)
			ssdp_response.set_header("BOOTID.UPNP.ORG", str(bootid))
			ssdp_response.set_header("CONFIGID.UPNP.ORG", str(configid))
			ssdp_response.send()
		#
	#

	def schedule(self, wait_timeout = 0):
	#
		"""
Activates all relevant multicast listeners based on the IP address given.

:param wait_timeout: Time to wait before delivery

:since: v0.1.03
		"""

		# pylint: disable=star-args


		if (self.type == ControlPointEvent.TYPE_DEVICE_ALIVE):
		#
			event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_SHUTDOWN, control_point = self.control_point)
			if (self.configid != None): event.set_configid(self.configid)
			event.set_usn(self.usn)
			event.schedule()
		#
		elif (self.type == ControlPointEvent.TYPE_DEVICE_UPDATE
		      and (not Settings.get("pas_upnp_ssdp_update_disabled", False))
		     ):
		#
			event = ControlPointEvent(ControlPointEvent.TYPE_DEVICE_SHUTDOWN, control_point = self.control_point)
			if (self.configid != None): event.set_configid(self.configid)
			event.set_usn(self.usn)
			event.set_location(self.location)
			event.schedule()

			self.type = ControlPointEvent.TYPE_DEVICE_ALIVE
			if (wait_timeout < 0.3): wait_timeout = 0.3
		#

		AbstractEvent.schedule(self, wait_timeout)
	#

	def set_configid(self, configid):
	#
		"""
Sets the UPnP configId value.

:param configid: UPnP configId

:since: v0.1.03
		"""

		self.configid = configid
	#

	def set_control_point(self, control_point):
	#
		"""
Sets the UPnP ControlPoint scheduling the event delivery.

:param control_point: Control point scheduling delivery

:since: v0.1.03
		"""

		self.control_point = control_point
	#

	def set_location(self, location):
	#
		"""
Sets the UPnP HTTP location URL.

:param location: UPnP HTTP location URL

:since: v0.1.03
		"""

		self.location = location
	#

	def set_response_target(self, host, port):
	#
		"""
Sets the M-SEARCH response target host and port.

:param host: Target host
:param port: Target port

:since: v0.1.03
		"""

		self.target_host = host
		self.target_port = port
	#

	def set_search_target(self, _value):
	#
		"""
Sets the M-SEARCH ST value.

:param _value: M-SEARCH ST value

:since: v0.1.03
		"""

		self.search_target = _value
	#
#

##j## EOF