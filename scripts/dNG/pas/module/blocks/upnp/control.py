# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.upnp.xml
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

from dNG.pas.controller.upnp_request import direct_upnp_request
from dNG.pas.data.translatable_exception import direct_translatable_exception
from dNG.pas.data.upnp.services.abstract_service import direct_abstract_service
from .module import direct_module

class direct_control(direct_module):
#
	"""
Service for "m=upnp;s=control"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	def execute_request(self):
	#
		"""
Action for "request"

:since: v0.1.00
		"""

		if (not isinstance(self.request, direct_upnp_request)): raise direct_translatable_exception("pas_http_error_400")
		upnp_service = self.request.get_upnp_service()
		if (not isinstance(upnp_service, direct_abstract_service)): raise direct_translatable_exception("pas_http_error_400")

		soap_request = self.request.get_soap_request()

		if (soap_request != None): self.response.send_result(soap_request['action'], upnp_service.handle_soap_call(soap_request['action'], soap_request['arguments']))
		else: raise direct_translatable_exception("pas_http_error_500")
	#
#

##j## EOF