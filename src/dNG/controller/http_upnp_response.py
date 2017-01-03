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

from collections import OrderedDict
from platform import uname
from time import time

from dNG.data.binary import Binary
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.data.text.l10n import L10n
from dNG.data.upnp.client_settings_mixin import ClientSettingsMixin
from dNG.data.upnp.upnp_exception import UpnpException
from dNG.data.xml_resource import XmlResource

from .abstract_http_response import AbstractHttpResponse

class HttpUpnpResponse(ClientSettingsMixin, AbstractHttpResponse):
    """
This response class returns UPnP compliant responses.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self):
        """
Constructor __init__(HttpUpnpResponse)

:since: v0.2.00
        """

        AbstractHttpResponse.__init__(self)
        ClientSettingsMixin.__init__(self)
    #

    def init(self, cache = False, compress = True):
        """
Important headers will be created here. This includes caching, cookies, the
compression setting and information about P3P.

:param cache: Allow caching at client
:param compress: Send page GZip encoded (if supported)

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.init()- (#echo(__LINE__)#)", self, context = "pas_http_site")

        client_settings = self.get_client_settings()

        AbstractHttpResponse.init(self, cache, client_settings.get("upnp_http_compression_supported", True))
        os_uname = uname()

        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.set_header("Date", RfcBasics.get_rfc5322_datetime(time()))
        self.set_header("Server", "{0}/{1} UPnP/2.0 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.51".format(os_uname[0], os_uname[2]))
    #

    def handle_result(self, urn, action, result):
        """
Returns a UPNP response for the given URN and SOAP action.

:param urn: UPnP URN called
:param action: SOAP action called
:param result: UPnP result arguments

:since: v0.2.00
        """

        if (isinstance(result, Exception)):
            if (isinstance(result, UpnpException)): self.send_error(result.get_upnp_code(), "{0:l10n_message}".format(result))
            else: self.send_error(501, L10n.get("errors_core_unknown_error"))
        else:
            xml_resource = XmlResource(node_type = OrderedDict)

            client_settings = self.get_client_settings()
            if (not client_settings.get("upnp_xml_cdata_encoded", False)): xml_resource.set_cdata_encoding(False)

            xml_resource.add_node("s:Envelope", attributes = { "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/", "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })

            xml_base_path = "s:Envelope s:Body u:{0}Response".format(action)
            xml_resource.add_node(xml_base_path, attributes = { "xmlns:u": urn })
            xml_resource.set_cached_node(xml_base_path)

            for result_value in result: xml_resource.add_node("{0} {1}".format(xml_base_path, result_value['name']), result_value['value'])

            self.data = Binary.utf8_bytes("<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_resource.export_cache(True)))
        #
    #

    def send(self):
        """
Sends the prepared response.

:since: v0.2.00
        """

        if (self.data is not None):
            if (not self.initialized): self.init()
            self.send_headers()

            self.stream_response.send_data(self.data)
            self.data = None
        elif (not self.are_headers_sent()):
            self.set_header("HTTP", "HTTP/2.0 500 Internal Server Error", True)

            if (self.errors is None): self.send_error(501, L10n.get("errors_core_unknown_error"))
            else: self.send_error(self.errors[0].get("code", 501), self.errors[0]['message'])
        #
    #

    def send_error(self, code, description):
        """
Returns a UPNP response for the requested SOAP action.

:param code: UPnP error code
:param description: UPnP error description

:since: v0.2.00
        """

        xml_resource = XmlResource()

        xml_resource.add_node("s:Envelope", attributes = { "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/", "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/" })

        xml_resource.add_node("s:Envelope s:Body s:Fault faultcode", "Client")
        xml_resource.set_cached_node("s:Envelope s:Body")

        xml_resource.add_node("s:Envelope s:Body s:Fault faultstring", "UPnPError")
        xml_resource.add_node("s:Envelope s:Body s:Fault detail UPnPError", attributes = { "xmlns": "urn:schemas-upnp-org:control-1.0" })
        xml_resource.set_cached_node("s:Envelope s:Body s:Fault detail UPnPError")

        xml_resource.add_node("s:Envelope s:Body s:Fault detail UPnPError errorCode", code)
        xml_resource.add_node("s:Envelope s:Body s:Fault detail UPnPError errorDescription", description)

        self.data = Binary.utf8_bytes("<?xml version='1.0' encoding='UTF-8' ?>{0}".format(xml_resource.export_cache(True)))
        self.send()
    #
#
