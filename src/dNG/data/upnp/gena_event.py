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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasUPnPVersion)#
#echo(__FILEPATH__)#
"""

from dNG.data.xml_resource import XmlResource
from dNG.net.http.client import Client
from dNG.net.upnp.control_point import ControlPoint
from dNG.net.upnp.gena import Gena
from dNG.runtime.value_exception import ValueException

from .abstract_event import AbstractEvent

class GenaEvent(AbstractEvent):
#
	"""
"GenaEvent" is the event class for UPnP GENA related events.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	TYPE_PROPCHANGE = 1
	"""
upnp:propchange event type
	"""

	def __init__(self, _type):
	#
		"""
Constructor __init__(GenaEvent)

:param _type: Event to be delivered

:since: v0.2.00
		"""

		AbstractEvent.__init__(self, _type)

		self.gena = None
		"""
UPnP GENA instance
		"""
		self.moderated_delta = 0
		"""
Moderated event changes required as specified by the formal specification.
		"""
		self.moderated_interval = 0
		"""
The moderated event interval as specified by the formal specification.
		"""
		self.service_id = None
		"""
UPnP serviceId value
		"""
		self.sid = None
		"""
UPnP SID an event is send to
		"""
		self.usn = None
		"""
UPnP USN
		"""
		self.variables = None
		"""
upnp:propchange variables
		"""

		self.control_point = ControlPoint.get_instance()
		self.gena = Gena.get_instance()
	#

	def get_moderated_delta(self):
	#
		"""
Returns the moderated event changes delta required as specified by the
formal specification.

:return: (int) Number of changes before an event should be send
:since:  v0.2.00
		"""

		return self.moderated_delta
	#

	def get_moderated_interval(self):
	#
		"""
Returns the moderated event interval as specified by the formal specification.

:return: (float) Interval in seconds
:since:  v0.2.00
		"""

		return self.moderated_interval
	#

	def _get_subscribers(self):
	#
		"""
Returns a dictionary of subscribers interested in this event.

:return: (dict) Dictionary with SID as key and subscription information
:since:  v0.2.00
		"""

		if (self.sid is None): _return = self.gena.get_subscribers(self.usn)
		else:
		#
			_return = { }

			subscriber = self.gena.get_subscriber(self.sid)
			if (subscriber is not None): _return[self.sid] = subscriber
		#

		return _return
	#

	def _send(self):
	#
		"""
Send event.

:since: v0.2.00
		"""

		# pylint: disable=protected-access

		if (self.usn is None): raise ValueException("UPnP USN is required for GENA events")

		subscribers = self._get_subscribers()

		if (self.type == GenaEvent.TYPE_PROPCHANGE):
		#
			if (not isinstance(self.variables, dict)): raise ValueException("upnp:propchange requires a dictionary of variables changed")

			xml_resource = XmlResource()
			xml_resource.set_cdata_encoding(False)

			xml_resource.add_node("e:propertyset", attributes = { "xmlns:e": "urn:schemas-upnp-org:event-1-0" })

			xml_base_path = "e:propertyset e:property"
			xml_resource.add_node(xml_base_path)
			xml_resource.set_cached_node(xml_base_path)

			for key in self.variables: xml_resource.add_node("{0} {1}".format(xml_base_path, key), self.variables[key])

			xml_data = "<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_resource.export_cache(True))

			for subscriber_sid in subscribers:
			#
				seq = self.gena._approve_seq_for_event(self, subscriber_sid)
				if (seq is not None): self._send_propchange(subscriber_sid, subscribers[subscriber_sid], seq, xml_data)
			#
		#
		#
	#

	def _send_propchange(self, subscriber_sid, subscriber, seq, xml_data):
	#
		"""
Sends the upnp:propchange event to the given subscriber.

:param subscriber_sid: UPnP SID
:param subscriber: Dictionary with subscription information
:param seq: GENA notification sequence number for the event
:param xml_data: XML encoded e:propertyset

:since: v0.2.00
		"""

		for callback_url in subscriber['callback_urls']:
		#
			client = Client(callback_url, 2)
			client.set_header("Content-Type", "text/xml; charset=UTF-8")
			client.set_header("USN", self.usn)
			client.set_header("SID", subscriber_sid)
			client.set_header("NT", "upnp:event")
			client.set_header("NTS", "upnp:propchange")
			client.set_header("SEQ", seq)

			response = client.request("NOTIFY", data = xml_data)
			if (response.is_readable()): break
		#
	#

	def set_moderated_delta(self, changes):
	#
		"""
Sets the moderated event changes delta required as specified by the formal
specification.

:param changes: Number of changes before an event should be send

:since: v0.2.00
		"""

		self.moderated_delta = changes
	#

	def set_moderated_interval(self, seconds):
	#
		"""
Sets the moderated event interval as specified by the formal specification.

:param seconds: Interval in seconds

:since: v0.2.00
		"""

		self.moderated_interval = seconds
	#

	def set_service_id(self, service_id):
	#
		"""
Sets the UPnP serviceId value.

:param service_id: UPnP serviceId value

:since: v0.2.00
		"""

		self.service_id = service_id
	#

	def set_sid(self, sid):
	#
		"""
Sets the UPnP SID an event is send to.

:param sid: UPnP SID

:since: v0.2.00
		"""

		self.sid = sid
	#

	def set_usn(self, usn):
	#
		"""
Sets the UPnP USN.

:param sid: UPnP USN

:since: v0.2.00
		"""

		self.usn = usn
	#

	def set_variables(self, **kwargs):
	#
		"""
Sets the upnp:propchange variables given as keyword arguments.

:since: v0.2.00
		"""

		self.variables = kwargs
	#
#

##j## EOF