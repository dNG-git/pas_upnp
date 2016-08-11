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

from threading import Thread

from dNG.runtime.exception_log_trap import ExceptionLogTrap
from dNG.runtime.not_implemented_exception import NotImplementedException
from dNG.runtime.value_exception import ValueException

class AbstractEvent(Thread):
#
	"""
The abstract event class for scheduled delivery by the UPnP control point.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, _type):
	#
		"""
Constructor __init__(AbstractEvent)

:param _type: Event to be delivered

:since: v0.2.00
		"""

		Thread.__init__(self, target = self._send)

		self.control_point = None
		"""
The UPnP ControlPoint scheduling the event delivery.
		"""
		self.type = _type
		"""
Event type to be handled
		"""
		self.usn = None
		"""
UPnP USN
		"""
	#

	def deliver(self, wait_timeout = 0):
	#
		"""
Activates all relevant multicast listeners based on the IP address given.

:param wait_timeout: Time to wait before delivery

:since: v0.2.00
		"""

		if (wait_timeout > 0): self.schedule(wait_timeout)
		else: self.start()
	#

	def get_usn(self):
	#
		"""
Returns the UPnP USN value.

:return: (str) UPnP USN
:since:  v0.2.00
		"""

		return self.usn
	#

	def run(self):
	#
		"""
python.org: Method representing the thread's activity.

:since: v0.2.00
		"""

		with ExceptionLogTrap("pas_upnp"):
		#
			Thread.run(self)
		#
	#

	def schedule(self, wait_timeout = 0):
	#
		"""
Activates all relevant multicast listeners based on the IP address given.

:param wait_timeout: Time to wait before delivery

:since: v0.2.00
		"""

		# pylint: disable=star-args

		if (self.control_point is None): raise ValueException("UPnP control point needs to be defined to schedule event delivery")

		event_data = { "event": self }
		if (self.usn is not None): event_data['usn'] = self.usn

		self.control_point._add_task(wait_timeout, "deliver_event", **event_data)
	#

	def _send(self):
	#
		"""
Send event.

:since: v0.2.00
		"""

		raise NotImplementedException()
	#

	def set_usn(self, usn):
	#
		"""
Sets the UPnP USN fpr this event.

:param usn: UPnP USN

:since: v0.2.00
		"""

		self.usn = usn
	#
#

##j## EOF