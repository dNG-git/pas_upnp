# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.upnp.gena
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

from time import time
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid
import socket

try: import hashlib
except ImportError: import md5 as hashlib

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.abstract_timed_tasks import AbstractTimedTasks
from dNG.pas.data.binary import Binary
from dNG.pas.module.named_loader import NamedLoader

class Gena(AbstractTimedTasks):
#
	"""
The UPnP GENA manager.

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
Constructor __init__(Gena)

:since: v0.1.00
		"""

		AbstractTimedTasks.__init__(self)

		self.subscriptions = None
		"""
Active subscriptions
		"""
		self.timeouts = [ ]
		"""
Active subscriptions
		"""
		self.notifications = { }
		"""
Cached notifications for submission
		"""

		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
	#

	def __del__(self):
	#
		"""
Destructor __del__(Gena)

:since: v0.1.00
		"""

		if (self.subscriptions != None): self.stop()
		AbstractTimedTasks.__del__(self)
	#

	def cancel(self, service_name, ip):
	#
		"""
Cancels all subscriptions based on the given IP. "deregister()" should be
preferred if possible.

:param service_name: UPnP service name
:param ip: Subscribed client IP

:return: (bool) True if at least one subscription has been canceled.
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.cancel(service_name, {0})- (#echo(__LINE__)#)".format(ip))
		var_return = False

		with Gena.synchronized:
		#
			if (service_name == None): subscriptions = self.subscriptions.copy()
			elif (service_name in self.subscriptions): subscriptions = { service_name: self.subscriptions[service_name].copy() }
			else: subscriptions = None

			if (subscriptions != None):
			#
				for service_name in subscriptions:
				#
					for callback_url in subscriptions[service_name]:
					#
						if (ip in subscriptions[service_name][callback_url]['ips']):
						#
							del(self.subscriptions[service_name][callback_url])
							var_return = True

							for position in range(len(self.timeouts) - 1, -1, -1):
							#
								timeout_entry = self.timeouts[position]
								if (timeout_entry['callback_url'] == callback_url and timeout_entry['service_name'] == service_name): self.timeouts.pop(position)
							#
						#
					#

					if (len(self.subscriptions[service_name]) < 1): del(self.subscriptions[service_name])
				#
			#
		#

		return var_return
	#

	def deregister(self, service_name, sid):
	#
		"""
Removes the subscription identified by the given SID.

:param service_name: UPnP service name
:param sid: UPnP SID

:return: (bool) True if successful
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.deregister({0}, {1})- (#echo(__LINE__)#)".format(service_name, sid))
		var_return = False

		with Gena.synchronized:
		#
			if (service_name in self.subscriptions):
			#
				subscriptions = self.subscriptions[service_name].copy()

				for callback_url in subscriptions:
				#
					if (subscriptions[callback_url]['sid'] == sid):
					#
						del(self.subscriptions[service_name][callback_url])
						var_return = True
						break
					#
				#

				if (len(self.subscriptions[service_name]) < 1): del(self.subscriptions[service_name])
			#

			if (var_return):
			#
				for position in range(len(self.timeouts) - 1, -1, -1):
				#
					timeout_entry = self.timeouts[position]
					if (timeout_entry['callback_url'] == callback_url and timeout_entry['service_name'] == service_name): self.timeouts.pop(position)
				#
			#
		#

		return var_return
	#

	def get_next_update_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:access: protected
:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.00
		"""

		with Gena.synchronized:
		#
			if (len(self.timeouts) > 0): var_return = self.timeouts[0]['timestamp']
			else: var_return = -1
		#

		return var_return
	#

	def register(self, service_name, callback_url, timeout):
	#
		"""
Registers a callback URL endpoint for notifications for the given service
name.

:param service_name: UPnP service name
:param callback_url: Endpoint for notification messages
:param timeout: Timeout in seconds for the subscription

:return: (bool) True if successful
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.register({0}, {1}, {2:d})- (#echo(__LINE__)#)".format(service_name, callback_url, timeout))
		var_return = None

		index = 1

		with Gena.synchronized:
		#
			if (service_name not in self.subscriptions or callback_url not in self.subscriptions[service_name]):
			#
				var_return = "uuid:{0}".format(uuid(NAMESPACE_URL, "upnp-gena://{0}/{1}".format(socket.getfqdn(), hashlib.md5(Binary.utf8_bytes(callback_url)).hexdigest())))
				if (service_name not in self.subscriptions): self.subscriptions[service_name] = { }

				self.subscriptions[service_name][callback_url] = { "seq": 0, "sid": var_return }
				url_elements = urlsplit(callback_url)
				ip_address_paths = socket.getaddrinfo(url_elements.hostname, url_elements.port, socket.AF_UNSPEC, 0, socket.IPPROTO_TCP)

				if (len(ip_address_paths) > 0):
				#
					ips = [ ]

					for ip_address_data in ip_address_paths:
					#
						if (ip_address_data[0] == socket.AF_INET or ip_address_data[0] == socket.AF_INET6): ips.append(ip_address_data[4][0])
					#

					if (len(ips) > 0): self.subscriptions[service_name][callback_url]['ips'] = ips
				#

				index = len(self.timeouts)
				timestamp = time() + timeout

				if (index > 0):
				#
					for position in range(index - 1, -1, -1):
					#
						if (timestamp > self.timeouts[position]['timestamp']):
						#
							index = position
							break
						#
					#
				#

				self.timeouts.insert(index, { "timestamp": timestamp, "service_name": service_name, "callback_url": callback_url })
			#
		#

		if (index < 1): self.update_timestamp()
		return var_return
	#

	def reregister(self, service_name, sid, timeout):
	#
		"""
Renews an subscription identified by the given SID.

:param service_name: UPnP service name
:param sid: UPnP SID
:param timeout: Timeout in seconds for the subscription

:return: (bool) True if successful
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.reregister({0}, {1}, {2:d})- (#echo(__LINE__)#)".format(service_name, sid, timeout))
		var_return = False

		index = 1

		with Gena.synchronized:
		#
			sid_callback_url = None

			if (service_name in self.subscriptions):
			#
				for callback_url in self.subscriptions[service_name]:
				#
					if (self.subscriptions[service_name][callback_url]['sid'] == sid):
					#
						sid_callback_url = callback_url
						var_return = True
						break
					#
				#
			#

			if (var_return):
			#
				index = None
				timestamp = time() + timeout

				for position in range(len(self.timeouts) - 1, -1, -1):
				#
					timeout_entry = self.timeouts[position]

					if (timeout_entry['callback_url'] == sid_callback_url and timeout_entry['service_name'] == service_name): self.timeouts.pop(position)
					elif (index == None and timestamp > timeout_entry['timestamp']): index = position
				#

				if (index == None): index = len(self.timeouts)
				self.timeouts.insert(index, { "timestamp": timestamp, "service_name": service_name, "callback_url": callback_url })
			#
		#

		if (index < 1): self.update_timestamp()
		return var_return
	#

	def return_instance(self):
	#
		"""
The last "return_instance()" call will free the singleton reference.

:since: v0.1.00
		"""

		with Gena.synchronized:
		#
			if (Gena.instance != None):
			#
				if (Gena.ref_count > 0): Gena.ref_count -= 1

				if (Gena.ref_count == 0):
				#
					Gena.instance.stop()
					Gena.instance = None
				#
			#
		#
	#

	def run(self):
	#
		"""
Worker loop

:access: protected
:since:  v0.1.00
		"""

		Gena.synchronized.acquire()

		if (len(self.timeouts) > 0 and self.timeouts[0]['timestamp'] <= time()):
		#
			timeout_entry = self.timeouts.pop(0)

			if (self.subscriptions != None and timeout_entry['service_name'] in self.subscriptions and timeout_entry['callback_url'] in self.subscriptions[timeout_entry['service_name']]):
			#
				del(self.subscriptions[timeout_entry['service_name']][timeout_entry['callback_url']])
				if (len(self.subscriptions[timeout_entry['service_name']]) < 1): del(self.subscriptions[timeout_entry['service_name']])
			#

			Gena.synchronized.release()

			if (self.log_handler != None): self.log_handler.debug("pas.upnp GENA removes subscription '{0}'".format(timeout_entry['service_name']))
		#
		else: Gena.synchronized.release()

		AbstractTimedTasks.run(self)
	#

	def start(self, params = None, last_return = None):
	#
		"""
Starts the GENA manager.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.start()- (#echo(__LINE__)#)")

		AbstractTimedTasks.start(self)
		self.subscriptions = { }

		return last_return
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Stops the GENA manager.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -upnpGena.stop()- (#echo(__LINE__)#)")

		AbstractTimedTasks.stop(self)
		self.subscriptions = None

		return last_return
	#

	@staticmethod
	def get_instance(count = True):
	#
		"""
Get the GENA singleton.

:param count: Count "get()" request

:return: (Gena) Object on success
:since:  v0.1.00
		"""

		with Gena.synchronized:
		#
			if (Gena.instance == None): Gena.instance = Gena()
			if (count): Gena.ref_count += 1
		#

		return Gena.instance
	#
#

##j## EOF