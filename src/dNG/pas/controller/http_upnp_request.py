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

from base64 import b64decode

from dNG.data.xml_resource import XmlResource
from dNG.pas.data.binary import Binary
from dNG.pas.data.upnp.client import Client
from dNG.pas.plugins.hook import Hook
from .abstract_inner_http_request import AbstractInnerHttpRequest

class HttpUpnpRequest(AbstractInnerHttpRequest):
#
	"""
"HttpUpnpRequest" implements UPnP request types to get XML files,
invoke SOAP methods or retrieve data.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(HttpUpnpRequest)

:since: v0.1.00
		"""

		AbstractInnerHttpRequest.__init__(self)

		self.body_instance = None
		"""
Retrieved HTTP request body
		"""
		self.upnp_control_point = None
		"""
UPnP ControlPoint
		"""
		self.upnp_device = None
		"""
UPnP device
		"""
		self.upnp_service = None
		"""
UPnP service
		"""
	#

	def get_soap_request(self, timeout = 30):
	#
		"""
Parses the SOAP request to identify the contained request.

:param timeout: Timeout for receiving the SOAP request.

:return: (dict) UPnP request with URN, SOAP action and arguments
:since:  v0.1.00
		"""

		_return = None

		soap_action = self.get_header("SoapAction")
		if (soap_action != None): soap_action = soap_action.strip("\"").split("#", 1)

		if (self.body_instance != None and soap_action != None):
		#
			urn = soap_action[0]
			soap_action = soap_action[1]

			post_data = self.body_instance.get(timeout)

			xml_data = Binary.str(post_data.read())
			xml_resource = XmlResource()
			xml_resource.register_ns("soap", "http://schemas.xmlsoap.org/soap/envelope/")
			xml_resource.register_ns("upnpsns", urn)

			if (xml_resource.xml_to_dict(xml_data) != None):
			#
				soap_arguments = { }
				xml_node = xml_resource.get_node("soap:Envelope soap:Body upnpsns:{0}".format(soap_action))

				if (xml_node != None):
				#
					for position in xml_node:
					#
						if (isinstance(xml_node[position], dict) and "tag" in xml_node[position] and "value" in xml_node[position]): soap_arguments[xml_node[position]['tag']] = xml_node[position]['value']
					#
				#

				_return = { "urn": urn, "action": soap_action, "arguments": soap_arguments }
			#
		#

		return _return
	#

	def get_upnp_control_point(self):
	#
		"""
Returns the active UPnP ControlPoint.

:return: (ControlPoint) UPnP ControlPoint
:since:  v0.1.00
		"""

		return self.upnp_control_point
	#

	def get_upnp_device(self):
	#
		"""
Returns the UPnP device requested.

:return: (object) UPnP device; None if undefined
:since:  v0.1.00
		"""

		return self.upnp_device
	#

	def get_upnp_service(self):
	#
		"""
Returns the UPnP service requested.

:return: (object) UPnP service; None if undefined
:since:  v0.1.00
		"""

		return self.upnp_service
	#

	def set_request(self, http_request, control_point, device, request_data):
	#
		"""
Sets the requested action.

:param http_request: Retrieved HTTP request
:param control_point: Active UPnP ControlPoint
:param device: UPnP device requested
:param request_data: Dict with the parsed request URI

:since: v0.1.00
		"""

		self.body_instance = http_request.get_request_body(content_type_expected = "text/xml")
		self.headers = http_request.get_headers()
		self.module = "upnp"
		self.upnp_control_point = control_point
		self.upnp_device = device

		request_data_length = len(request_data)

		if (request_data_length == 1):
		#
			self.service = "identity"
			self.action = "device"
		#
		elif (request_data_length == 2):
		#
			if (request_data[0] == "stream"):
			#
				self.service = "stream"
				self.action = "source"

				stream_url = None
				user_agent = http_request.get_header("User-Agent")

				client = Client.load_user_agent(user_agent)

				if (client.get("upnp_stream_url_use_filter", False)):
				#
					stream_url_filtered = Hook.call("dNG.pas.http.HttpUpnpRequest.filterStreamUrl", encoded_url = request_data[1], user_agent = user_agent)
					if (stream_url_filtered != None): stream_url = stream_url_filtered
				#

				if (stream_url == None): stream_url = Binary.str(b64decode(Binary.utf8_bytes(request_data[1])))
				self.set_dsd("src", stream_url)
			#
			elif (request_data[1] == "desc"):
			#
				self.service = "xml"
				self.action = "get_device"
			#
			elif (device != None):
			#
				self.upnp_service = device.get_service(request_data[1])

				self.service = "identity"
				self.action = "service"
			#
		#
		elif (device != None):
		#
			self.upnp_service = device.get_service(request_data[1])

			if (request_data[2] == "control"):
			#
				self.service = "control"
				self.action = "request"
				self.output_handler = "http_upnp"
			#
			elif (request_data[2] == "eventsub"):
			#
				self.service = "events"
				self.action = http_request.get_type().lower()
				self.output_handler = "http_upnp"
			#
			else:
			#
				self.service = "xml"
				self.action = "get_service"
			#
		#
	#
#

##j## EOF