# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.HttpUpnpRequest
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

from base64 import b64decode

from dNG.data.xml_writer import XmlWriter
from dNG.pas.data.binary import Binary
from dNG.pas.data.http.request_body import RequestBody
from dNG.pas.data.http.request_headers_mixin import RequestHeadersMixin
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
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(HttpUpnpRequest)

:since: v0.1.00
		"""

		AbstractInnerHttpRequest.__init__(self)
		RequestHeadersMixin.__init__(self)

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
		self.wsgi_request = None
		"""
Retrieved WSGI request
		"""
	#

	def get_upnp_control_point(self):
	#
		"""
Return the active UPnP ControlPoint.

:return: (ControlPoint) UPnP ControlPoint
:since:  v0.1.00
		"""

		return self.upnp_control_point
	#

	def get_upnp_device(self):
	#
		"""
Sets the requested action.

:return: (object) UPnP device
:since:  v0.1.00
		"""

		return self.upnp_device
	#

	def get_upnp_service(self):
	#
		"""
Sets the requested action.

:return: (object) UPnP service
:since:  v0.1.00
		"""

		return self.upnp_service
	#

	def get_soap_request(self, timeout = 30):
	#
		"""
Sets the requested action.

:return: (object) UPnP service
:since:  v0.1.00
		"""

		_return = None

		request_body = RequestBody()
		request_body = self.wsgi_request.configure_request_body(request_body, "text/xml")

		soap_action = self.get_header("SoapAction")
		if (soap_action != None): soap_action = soap_action.strip("\"").split("#", 1)

		if (request_body != None and soap_action != None):
		#
			urn = soap_action[0]
			soap_action = soap_action[1]

			post_data = request_body.get(timeout)

			xml_data = Binary.str(post_data.read())
			xml_parser = XmlWriter()
			xml_parser.ns_register("soap", "http://schemas.xmlsoap.org/soap/envelope/")
			xml_parser.ns_register("upnpsns", urn)

			if (xml_parser.xml2dict(xml_data)):
			#
				soap_arguments = { }
				xml_node = xml_parser.node_get("soap:Envelope soap:Body upnpsns:{0}".format(soap_action))

				if (xml_node != False):
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

	def set_request(self, http_wsgi_request, control_point, device, request_data):
	#
		"""
Sets the requested action.

:since: v0.1.00
		"""

		self.headers = http_wsgi_request.get_headers()
		self.module = "upnp"
		self.upnp_control_point = control_point
		self.upnp_device = device
		self.wsgi_request = http_wsgi_request
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

				self.set_dsd("src", Binary.str(b64decode(Binary.utf8_bytes(request_data[1]))))
			#
			elif (request_data[1] == "desc"):
			#
				self.service = "xml"
				self.action = "get_device"
			#
			elif (device != None):
			#
				self.upnp_service = device.service_get(request_data[1])

				self.service = "identity"
				self.action = "service"
			#
		#
		elif (device != None):
		#
			self.upnp_service = device.service_get(request_data[1])

			if (request_data[2] == "control"):
			#
				self.service = "control"
				self.action = "request"
				self.output_format = "http_upnp"
			#
			elif (request_data[2] == "eventsub"):
			#
				self.service = "events"
				self.action = http_wsgi_request.get_type().lower()
				self.output_format = "http_upnp"
			#
			else:
			#
				self.service = "xml"
				self.action = "get_service"
			#
		#
	#

	def supports_accepted_formats(self):
	#
		"""
Sets false if accepted formats can not be identified.

:return: (bool) True accepted formats are supported.
:since:  v0.1.00
		"""

		return True
	#

	def supports_headers(self):
	#
		"""
Sets false if the script name is not needed for execution.

:return: (bool) True if the request contains headers.
:since:  v0.1.00
		"""

		return True
	#
#

##j## EOF