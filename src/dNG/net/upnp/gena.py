# -*- coding: utf-8 -*-

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

# pylint: disable=import-error,no-name-in-module

from copy import copy
from time import time
from uuid import NAMESPACE_URL
from uuid import uuid3 as uuid
from weakref import ref
import re
import socket

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.data.text.md5 import Md5
from dNG.data.upnp.abstract_event import AbstractEvent
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook
from dNG.runtime.instance_lock import InstanceLock
from dNG.runtime.type_exception import TypeException
from dNG.tasks.abstract_timed import AbstractTimed

class Gena(AbstractTimed):
    """
The UPnP GENA manager.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    RE_CALLBACK_URL_ELEMENTS = re.compile("<(.+?)>")
    """
RegEx to find UPnP GENA subscription URLs
    """
    SEQ_NUMBER_MAX = 4294967295
    """
Largest sequence number supported by UPnP v1.0
    """

    _instance_lock = InstanceLock()
    """
Thread safety lock
    """
    _weakref_instance = None
    """
UPnP GENA weakref instance
    """

    def __init__(self):
        """
Constructor __init__(Gena)

:since: v0.2.00
        """

        AbstractTimed.__init__(self)

        self.subscriptions = { }
        """
Active subscriptions
        """
        self.timeouts = [ ]
        """
Active subscriptions
        """

        self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
    #

    def _approve_seq_for_event(self, event, sid):
        """
Returns the notification sequence number if the event is approved.

:param event: UPnP event instance
:param sid: UPnP SID

:return: (int) Sequence number
:since:  v0.2.00
        """

        _return = None

        if (not isinstance(event, AbstractEvent)): raise TypeException("Given event is invalid")

        is_approved = False

        moderated_delta = (event.get_moderated_delta()
                           if (hasattr(event, "get_moderated_delta")) else
                           0
                          )

        moderated_interval = (event.get_moderated_interval()
                           if (hasattr(event, "get_moderated_interval")) else
                           0
                          )

        variables_evented = (event.get_variables()
                             if (hasattr(event, "get_variables")) else
                             None
                            )

        usn = event.get_usn()
        service_name = Gena.strip_usn_version(usn)

        if (service_name in self.subscriptions):
            with self.lock:
                # Thread safety
                if (service_name in self.subscriptions and sid in self.subscriptions[service_name]):
                    moderated_subscription_delta = 0
                    subscription = self.subscriptions[service_name][sid]
                    _time = time()

                    is_approved = (moderated_interval == 0 or subscription.get("time_updated", 0) + moderated_interval < _time)

                    variables_subscribed = subscription.get("variables_subscribed")

                    if (is_approved
                        and variables_evented is not None
                        and variables_subscribed != "*"
                       ):
                        is_variable_subscribed = False

                        for variable_name in variables_evented:
                            if (variable_name in variables_subscribed):
                                is_variable_subscribed = True
                                break
                            #
                        #

                        if (not is_variable_subscribed): is_approved = False
                    #

                    if (is_approved and moderated_delta > 0):
                        moderated_subscription_delta = subscription.get("moderated_delta", 0)
                        moderated_subscription_delta += 1

                        is_approved = (moderated_delta == 0 or subscription.get("moderated_delta", 0) >= moderated_delta)
                        subscription['moderated_delta'] = moderated_subscription_delta
                    #

                    if (is_approved):
                        _return = subscription['seq']

                        subscription['seq'] += 1
                        if (subscription['seq'] > Gena.SEQ_NUMBER_MAX): subscription['seq'] = 1

                        subscription['time_updated'] = _time
                    #
                #
            #
        #

        return _return
    #

    def cancel(self, usn, ip):
        """
Cancels all subscriptions based on the given IP. "deregister()" should be
preferred if possible.

:param usn: UPnP USN
:param ip: Subscribed client IP

:return: (bool) True if at least one subscription has been canceled.
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.cancel({1})- (#echo(__LINE__)#)", self, ip, context = "pas_upnp")
        _return = False

        with self.lock:
            if (usn is None): subscriptions = self.subscriptions.copy()
            elif (usn in self.subscriptions):
                service_name = Gena.strip_usn_version(usn)
                subscriptions = { service_name: self.subscriptions[service_name].copy() }
            else: subscriptions = None

            if (subscriptions is not None):
                for service_name_subscribed in subscriptions:
                    for sid in subscriptions[service_name_subscribed]:
                        if (ip in subscriptions[service_name_subscribed][sid]['ips']): self.deregister(service_name_subscribed, sid)
                        _return = True
                    #
                #
            #
        #

        return _return
    #

    def deregister(self, usn, sid):
        """
Removes the subscription identified by the given SID.

:param usn: UPnP USN
:param sid: UPnP SID

:return: (bool) True if successful
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.deregister({1}, {2})- (#echo(__LINE__)#)", self, usn, sid, context = "pas_upnp")
        _return = False

        service_name = Gena.strip_usn_version(usn)

        if (service_name in self.subscriptions):
            with self.lock:
                # Thread safety
                if (service_name in self.subscriptions and sid in self.subscriptions[service_name]):
                    del(self.subscriptions[service_name][sid])
                    if (len(self.subscriptions[service_name]) < 1): del(self.subscriptions[service_name])

                    for position in range(len(self.timeouts) - 1, -1, -1):
                        timeout_entry = self.timeouts[position]
                        if (timeout_entry['sid'] == sid): self.timeouts.pop(position)
                    #

                    _return = True
                #
            #

            if (_return):
                if (self.log_handler is not None): self.log_handler.debug("{0!r} removes subscription '{1}' for '{2}'", self, sid, usn, context = "pas_upnp")
                Hook.call("dNG.pas.upnp.Gena.onUnregistered", usn = usn, sid = sid)
            #
        #

        return _return
    #

    def _get_next_update_timestamp(self):
        """
Get the implementation specific next "run()" UNIX timestamp.

:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.2.00
        """

        _return = -1

        if (len(self.timeouts) > 0):
            with self.lock:
                # Thread safety
                if (len(self.timeouts) > 0): _return = self.timeouts[0]['timestamp']
            #
        #

        return _return
    #

    def get_subscriber(self, sid):
        """
Returns the subscription identified by the given SID.

:param sid: UPnP SID

:return: (dict) Subscription information as dict; None if not subscribed
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_subscriber({1})- (#echo(__LINE__)#)", self, sid, context = "pas_upnp")
        _return = None

        subscriptions = self.subscriptions.copy()

        for service_name_subscribed in subscriptions:
            if (sid in subscriptions[service_name_subscribed]):
                _return = subscriptions[service_name_subscribed][sid]
                break
            #
        #

        return _return
    #

    def get_subscribers(self, usn):
        """
Returns a list of subscriptions identified by the given USN.

:param usn: UPnP USN

:return: (dict) Dictionary with SID as key and subscription information
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_subscribers({1})- (#echo(__LINE__)#)", self, usn, context = "pas_upnp")

        service_name = Gena.strip_usn_version(usn)
        subscriptions = self.subscriptions.copy()

        return subscriptions.get(service_name, { })
    #

    def register(self, usn, callback_value, timeout, variables = None):
        """
Registers a callback URL endpoint for notifications for the given service
name.

:param usn: UPnP USN
:param callback_value: Endpoint URL(s) for notification messages
:param timeout: Timeout in seconds for the subscription
:param variables: CSV of UPnP state variables interested in

:return: (bool) True if successful
:since:  v0.2.00
        """

        _return = None

        index = 1
        timestamp = -1
        variables = ("" if (variables is None) else variables.strip())

        callback_urls = Gena.RE_CALLBACK_URL_ELEMENTS.findall(callback_value)

        if (len(callback_urls) > 1):
            sorted_callback_urls = (callback_urls.copy() if (hasattr(callback_urls, "copy")) else copy(callback_urls))
            sorted_callback_urls.sort()

            sid = "uuid:{0}".format(uuid(NAMESPACE_URL, "upnp-gena://{0}/{1}".format(socket.getfqdn(), Md5.hash(" ".join(sorted_callback_urls)))))
        else: sid = "uuid:{0}".format(uuid(NAMESPACE_URL, "upnp-gena://{0}/{1}".format(socket.getfqdn(), Md5.hash(callback_value))))

        service_name = Gena.strip_usn_version(usn)
        variables_subscribed = "*"

        if (variables != ""):
            # TODO: Implementation missing
            pass
        #

        with self.lock:
            if (service_name not in self.subscriptions): self.subscriptions[service_name] = { }

            if (sid not in self.subscriptions[service_name]):
                self.subscriptions[service_name][sid] = { "callback_urls": callback_urls,
                                                          "ips": [ ],
                                                          "seq": 0,
                                                          "variables_subscribed": variables_subscribed
                                                        }

                for callback_url in callback_urls:
                    url_elements = urlsplit(callback_url)

                    try:
                        ip_address_list = socket.getaddrinfo(url_elements.hostname,
                                                             url_elements.port,
                                                             socket.AF_UNSPEC,
                                                             0,
                                                             socket.IPPROTO_TCP
                                                            )

                        if (len(ip_address_list) > 0):
                            ips = [ ]

                            for ip_address_data in ip_address_list:
                                if (ip_address_data[0] == socket.AF_INET or ip_address_data[0] == socket.AF_INET6): ips.append(ip_address_data[4][0])
                            #

                            if (len(ips) > 0): self.subscriptions[service_name][sid]['ips'] += ips
                        #
                    except socket.error as handled_exception:
                        if (self.log_handler is not None): self.log_handler.error(handled_exception)
                    #
                #

                index = len(self.timeouts)
                timestamp = int(time() + timeout + 1)

                if (index > 0):
                    for position in range(index - 1, -1, -1):
                        if (timestamp > self.timeouts[position]['timestamp']):
                            index = position
                            break
                        #
                    #
                #

                self.timeouts.insert(index, { "timestamp": timestamp, "usn": usn, "sid": sid })
                if (self.log_handler is not None): self.log_handler.debug("{0!r} adds subscription '{1}' for '{2}' with callback URL value '{3}' and timeout '{4:d}'", self, sid, usn, " ".join(callback_urls), timeout, context = "pas_upnp")

                _return = sid
            #
        #

        if (index < 1): self.update_timestamp(timestamp)
        if (_return is not None): Hook.call("dNG.pas.upnp.Gena.onRegistered", usn = usn, sid = _return)

        return _return
    #

    def reregister(self, usn, sid, timeout):
        """
Renews an subscription identified by the given SID.

:param usn: UPnP USN
:param sid: UPnP SID
:param timeout: Timeout in seconds for the subscription

:return: (bool) True if successful
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.reregister({1}, {2}, {3:d})- (#echo(__LINE__)#)", self, usn, sid, timeout, context = "pas_upnp")
        _return = False

        index = 1
        service_name = Gena.strip_usn_version(usn)
        timestamp = -1

        if (service_name in self.subscriptions):
            with self.lock:
                # Thread safety
                if (service_name in self.subscriptions and sid in self.subscriptions[service_name]):
                    index = None
                    timestamp = int(time() + timeout + 1)

                    for position in range(len(self.timeouts) - 1, -1, -1):
                        timeout_entry = self.timeouts[position]

                        if (timeout_entry['sid'] == sid): self.timeouts.pop(position)
                        elif (index is None and timestamp > timeout_entry['timestamp']): index = position
                    #

                    if (index is None): index = len(self.timeouts)
                    self.timeouts.insert(index, { "timestamp": timestamp, "usn": usn, "sid": sid })

                    _return = True
                #
            #
        #

        if (index < 1): self.update_timestamp(timestamp)
        return _return
    #

    def run(self):
        """
Timed task execution

:since: v0.2.00
        """

        timeout_entry = None

        if (self.timer_active):
            with self.lock:
                # Thread safety
                if (self.timer_active
                    and len(self.timeouts) > 0
                    and int(self.timeouts[0]['timestamp']) <= time()
                   ): timeout_entry = self.timeouts.pop(0)

                AbstractTimed.run(self)
            #
        #

        if (timeout_entry is not None): self.deregister(timeout_entry['usn'], timeout_entry['sid'])
    #

    def start(self, params = None, last_return = None):
        """
Starts the GENA manager.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.start()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        self.subscriptions = { }

        return AbstractTimed.start(self)
    #

    @staticmethod
    def get_instance():
        """
Get the GENA singleton.

:return: (Gena) Object on success
:since:  v0.2.00
        """

        _return = None

        with Gena._instance_lock:
            if (Gena._weakref_instance is not None): _return = Gena._weakref_instance()

            if (_return is None):
                _return = Gena()
                Gena._weakref_instance = ref(_return)
            #
        #

        return _return
    #

    @staticmethod
    def strip_usn_version(usn):
        """
Returns the USN without the version.

:return: (str) UPnP service name (USN without version)
:since:  v0.2.00
        """

        return usn.rsplit(":", 1)[0]
    #
#
