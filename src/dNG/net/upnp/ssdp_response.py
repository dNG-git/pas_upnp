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

from platform import uname

from dNG.data.binary import Binary
from dNG.runtime.operation_not_supported_exception import OperationNotSupportedException

from .abstract_ssdp import AbstractSsdp

class SsdpResponse(AbstractSsdp):
    """
This class contains the UPnP SSDP message implementation. Its based on HTTP
for UDP.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def __init__(self, target, port = 1900, source_port = None):
        """
Constructor __init__(SsdpResponse)

:since: v0.2.00
        """

        AbstractSsdp.__init__(self, target, port, source_port)

        self.http_status = "200 OK"
        """
HTTP status code of the response
        """
    #

    def request(self, method, data = None):
        """
Call a given request method on the connected HTTP server.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (mixed) Response data; Exception on error
:since:  v0.2.00
        """

        raise OperationNotSupportedException()
    #

    def send(self, data = None):
        """
Invoke an SSDP M-SEARCH method on the unicast or multicast recipient.

:return: (bool) Request result
:since:  v0.2.00
        """

        if (data is not None): data = Binary.utf8_bytes(data)
        os_uname = uname()

        headers = self.headers.copy()
        headers['SERVER'] = "{0}/{1} UPnP/2.0 pasUPnP/#echo(pasUPnPIVersion)# DLNADOC/1.51 HTTP/1.1".format(os_uname[0], os_uname[2])
        headers['CONTENT-LENGTH'] = (0 if (data is None) else len(data))

        ssdp_header = "HTTP/1.1 {0}\r\n".format(self.http_status)

        for header_name in headers:
            if (type(headers[header_name]) is list):
                for header_value in headers[header_name]: ssdp_header += "{0}: {1}\r\n".format(header_name, header_value)
            else: ssdp_header += "{0}: {1}\r\n".format(header_name, headers[header_name])
        #

        ssdp_header = Binary.utf8_bytes("{0}\r\n".format(ssdp_header))

        data = (ssdp_header if (data is None) else ssdp_header + data)
        return self._write_data(data)
    #
#
