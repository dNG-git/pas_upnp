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

class DlnaHeadersMixin(object):
#
	"""
Mixin to handle DLNA headers.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def _add_dlna_headers(request, response, resource):
	#
		"""
Adds DLNA headers of the given resource and stream resource if requested.

:param request: Request instance
:param response: Response instance
:param resource: UPnP resource instance

:since: v0.2.00
		"""

		if (response.is_supported("headers")):
		#
			if (request.get_header("getcontentFeatures.dlna.org") == "1"
			    and resource.is_supported("dlna_content_features")
			   ):
			#
				response.set_header("contentFeatures.dlna.org",
				                    resource.get_dlna_content_features()
				                   )
			#

			upnp_transfer_mode = request.get_header("transferMode.dlna.org")

			if (upnp_transfer_mode == "Background"
			    or upnp_transfer_mode == "Interactive"
			    or upnp_transfer_mode == "Streaming"
			   ): response.set_header("transferMode.dlna.org", upnp_transfer_mode)
		#
	#
#

##j## EOF