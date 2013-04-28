# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.upnp_request
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

from dNG.data.xml_writer import direct_xml_writer
from dNG.pas.data.http.request_body import direct_request_body
from dNG.pas.net.http.request_headers_mixin import direct_request_headers_mixin
from dNG.pas.pythonback import direct_str
from .abstract_inner_request import direct_abstract_inner_request

class direct_upnp_request(direct_abstract_inner_request, direct_request_headers_mixin):
#
	"""
"direct_upnp_request" implements UPnP request types to get XML files, invoke
SOAP methods or retrieve data.

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
Constructor __init__(direct_upnp_request)

:since: v0.1.00
		"""

		direct_abstract_inner_request.__init__(self)
		direct_request_headers_mixin.__init__(self)

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

:return: (direct_control_point) UPnP ControlPoint
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

		var_return = None

		request_body = direct_request_body()
		request_body = self.wsgi_request.configure_request_body(request_body, "text/xml")

		soap_action = self.get_header("soapaction")
		if (soap_action != None): soap_action = soap_action.strip("\"").split("#", 1)

		if (request_body != None and soap_action != None):
		#
			urn = soap_action[0]
			soap_action = soap_action[1]

			post_data = request_body.get(timeout)

			xml_data = direct_str(post_data.read())
			xml_parser = direct_xml_writer()

			if (xml_parser.xml2dict(xml_data)):
			#
				xml_parser.ns_register("soap", "http://schemas.xmlsoap.org/soap/envelope/")
				xml_parser.ns_register("upnpsns", urn)

				xml_base_path = "soap:Envelope soap:Body upnpsns:{0}".format(soap_action)
				xml_parser.node_set_cache_path(xml_base_path)

				arguments_count = xml_parser.node_count("{0} argumentName".format(xml_base_path))
				soap_arguments = [ ]

				if (arguments_count > 0):
				#
					for position in range(0, arguments_count):
					#
						xml_node = xml_parser.node_get("{0} argumentName#{1:d}".format(xml_base_path, position))
						soap_arguments.append(xml_node['value'])
					#
				#

				var_return = { "urn": urn, "action": soap_action, "arguments": soap_arguments }
			#
		#

		return var_return
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

		if (len(request_data) == 2):
		#
			self.service = "xml"
			self.action = "get_device"
		#
		else:
		#
			self.upnp_service = device.service_get(request_data[1])

			if (request_data[2] == "control"):
			#
				self.service = "control"
				self.action = "request"
				self.output_format = "upnp"
			#
			elif (request_data[2] == "eventsub"):
			#
				self.service = "events"
				self.action = http_wsgi_request.get_type().lower()
				self.output_format = "upnp"
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