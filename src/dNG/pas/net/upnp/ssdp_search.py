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

from random import uniform as randfloat

from dNG.pas.data.upnp.client import Client
from dNG.pas.data.upnp.control_point_event import ControlPointEvent
from dNG.pas.data.upnp.device import Device
from .control_point import ControlPoint

class SsdpSearch(object):
#
	"""
The UPnP control point.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def _get_device_result_usn(device, condition_identifier):
	#
		"""
Returns the result UPnP USN based on the search condition.

:param device: Managed UPnP device
:param condition_identifier: Parsed UPnP search condition identifier

:return: (str) UPnP USN
:since:  v0.1.03
		"""

		return ("uuid:{0}::urn:{1}:device:{2}:{3}".format(device.get_udn(),
		                                                  device.get_upnp_domain(),
		                                                  device.get_type(),
		                                                  condition_identifier['version']
		                                                 )
		        if (condition_identifier != None and "version" in condition_identifier) else
		        "uuid:{0}::urn:{1}".format(device.get_udn(), device.get_urn())
		       )
	#

	@staticmethod
	def _get_result_search_target(condition, identifier_instance):
	#
		"""
Returns the result ST returned.

:param condition: UPnP search condition
:param identifier_instance: Instance providing the IdentifierMixin methods

:return: (str) UPnP URN
:since:  v0.1.03
		"""

		return ("urn:{0}".format(identifier_instance.get_urn())
		        if (condition == "ssdp:all") else
		        condition
		       )
	#

	@staticmethod
	def _get_rootdevice_results(condition):
	#
		"""
Appends all UPnP root devices managed by the ControlPoint instance to the
list of results.

:param condition: UPnP search condition

:return: (list) Search results to be send
:since:  v0.1.03
		"""

		_return = [ ]

		managed_devices = ControlPoint.get_instance().get_managed_devices()

		for uuid in managed_devices:
		#
			device = managed_devices[uuid]

			_return.append({ "usn": "uuid:{0}::upnp:rootdevice".format(uuid),
			                 "location": device.get_desc_url(),
			                 "search_target": condition
			               })
		#

		return _return
	#

	@staticmethod
	def _get_service_result_usn(service, condition_identifier):
	#
		"""
Returns the result UPnP USN based on the search condition.

:param service: Managed UPnP service
:param condition_identifier: Parsed UPnP search condition identifier

:return: (str) UPnP USN
:since:  v0.1.03
		"""

		return ("uuid:{0}::urn:{1}:service:{2}:{3}".format(service.get_udn(),
		                                                   service.get_upnp_domain(),
		                                                   service.get_type(),
		                                                   condition_identifier['version']
		                                                  )
		        if (condition_identifier != None and "version" in condition_identifier) else
		        "uuid:{0}::urn:{1}".format(service.get_udn(), service.get_urn())
		       )
	#

	@staticmethod
	def _handle_device_search(condition, condition_identifier, uuid, device):
	#
		"""
Searches for hosted devices matching the given search condition.

:param condition: UPnP search condition
:param condition_identifier: Parsed UPnP search condition identifier
:param uuid: Managed UPnP device UUID
:param device: Managed UPnP device

:return: (list) Search results to be send
:since:  v0.1.03
		"""

		_return = [ ]

		device_matched = False

		if (condition_identifier != None):
		#
			if (condition_identifier['class'] == "device"
			    and device.get_upnp_domain() == condition_identifier['domain']
			    and device.get_type() == condition_identifier['type']
			    and int(device.get_version()) >= int(condition_identifier['version'])
			   ): device_matched = True
		#
		elif (condition == "ssdp:all" or condition == "uuid:{0}".format(uuid)): device_matched = True

		if (device_matched):
		#
			_return.append({ "usn": SsdpSearch._get_device_result_usn(device, condition_identifier),
			                 "location": device.get_desc_url(),
			                 "search_target": SsdpSearch._get_result_search_target(condition, device)
			               })

			if (condition == "ssdp:all"):
			#
				_return.append({ "usn": "uuid:{0}".format(device.get_udn()),
				                 "location": device.get_desc_url(),
				                 "search_target": "uuid:{0}".format(device.get_udn())
				               })

				if (ControlPoint.get_instance().is_rootdevice_known(uuid = uuid)):
				#
					_return.append({ "usn": "uuid:{0}::upnp:rootdevice".format(device.get_udn()),
					                 "location": device.get_desc_url(),
					                 "search_target": "upnp:rootdevice"
					               })
				#
			#
		#

		return _return
	#

	@staticmethod
	def _handle_service_search(condition, condition_identifier, service, device):
	#
		"""
Searches for hosted devices matching the given search condition.

:param condition: UPnP search condition
:param condition_identifier: Parsed UPnP search condition identifier
:param service: Managed UPnP service
:param device: Managed UPnP device

:return: (list) Search results to be send
:since:  v0.1.03
		"""

		_return = [ ]

		service_matched = False

		if (condition == "ssdp:all"): service_matched = True
		elif (service.get_upnp_domain() == condition_identifier['domain']
		      and service.get_type() == condition_identifier['type']
		      and int(service.get_version()) >= int(condition_identifier['version'])
		     ): service_matched = True

		if (service_matched):
		#
			_return.append({ "usn": SsdpSearch._get_service_result_usn(service, condition_identifier),
			                 "location": device.get_desc_url(),
			                 "search_target": SsdpSearch._get_result_search_target(condition, service)
			               })
		#

		return _return
	#

	@staticmethod
	def handle_request(source_data, source_wait_timeout, search_target, additional_data = None):
	#
		"""
Searches for hosted devices matching the given UPnP search target.

:param source_data: UPnP client address data
:param source_wait_timeout: UPnP MX value
:param search_target: UPnP search target
:param additional_data: Additional data received

:since: v0.1.03
		"""

		condition = None
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

		results = [ ]

		if (condition != None):
		#
			control_point = ControlPoint.get_instance()

			if (condition_identifier == None
			    and condition == "upnp:rootdevice"
			   ): results += SsdpSearch._get_rootdevice_results(condition)
			else:
			#
				managed_devices = control_point.get_managed_devices()

				for uuid in managed_devices:
				#
					device = managed_devices[uuid]

					results += SsdpSearch._handle_device_search(condition,
					                                            condition_identifier,
					                                            uuid,
					                                            device
					                                           )

					if (condition == "ssdp:all"
					    or (condition_identifier != None and condition_identifier['class'] == "service")
					   ):
					#
						services = device.get_service_ids()

						for service_id in services:
						#
							service = device.get_service(service_id)

							results += SsdpSearch._handle_service_search(condition,
							                                             condition_identifier,
							                                             service,
							                                             device
							                                            )
						#
					#

					embedded_devices = device.get_embedded_device_uuids()

					for embedded_uuid in embedded_devices:
					#
						embedded_device = device.get_embedded_device(embedded_uuid)

						results += SsdpSearch._handle_device_search(condition,
						                                            condition_identifier,
						                                            embedded_uuid,
						                                            embedded_device
						                                           )

						if (condition_identifier != None and condition_identifier['class'] == "service"):
						#
							services = embedded_device.get_service_ids()

							for service_id in services:
							#
								service = embedded_device.get_service(service_id)

								results += SsdpSearch._handle_service_search(condition,
								                                             condition_identifier,
								                                             service,
								                                             embedded_device
								                                            )
							#
						#
					#
				#
			#

			if (len(results) > 0):
			#
				if (additional_data != None):
				#
					if ('USER-AGENT' in additional_data):
					#
						client = Client.load_user_agent(additional_data['USER-AGENT'])
						source_wait_timeout = client.get("ssdp_upnp_search_wait_timeout", source_wait_timeout)
					#
					elif (source_wait_timeout < 4):
					# Expect broken clients if no user-agent is given and MX is too small
						source_wait_timeout = 0
					#
				#

				if (source_wait_timeout > 0):
				#
					wait_seconds = randfloat(0,
					                         (source_wait_timeout if (source_wait_timeout < 10) else 10) / len(results)
					                        )
				#
				else: wait_seconds = 0

				for result in results:
				#
					event = ControlPointEvent(ControlPointEvent.TYPE_SEARCH_RESULT, control_point = control_point)
					event.set_usn(result['usn'])
					event.set_location(result['location'])
					event.set_search_target(result['search_target'])

					event.set_response_target(("[{0}]".format(source_data[0]) if (":" in source_data[0]) else source_data[0]),
					                          source_data[1]
					                         )

					event.schedule(wait_seconds)
				#
			#
		#
	#
#

##j## EOF