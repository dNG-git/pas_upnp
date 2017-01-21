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

from dNG.runtime.instance_lock import InstanceLock

class PasUpnpVersionMixin(object):
    """
This class contains a generic SSDP message implementation. Its based on HTTP
for UDP.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    DLNADOC_VERSION_SUPPORTED = "1.51"
    """
DLNADOC version used for HTTP/SSDP headers.
    """
    UPNP_HEADER_QUIRK_OS_LINUX = 1
    """
Quirk mode replaces the OS string from the SERVER header with "Linux".
    """
    UPNP_HEADER_QUIRK_OS_VERSION = 1 << 1
    """
Quirk mode replaces the OS version from the SERVER header with "0.0".
    """
    UPNP_HEADER_QUIRK_OS_WINDOWS = 1 << 2
    """
Quirk mode replaces the OS string from the SERVER header with "Windows".
    """
    UPNP_HEADER_QUIRK_HTTP_1_1 = 1 << 4
    """
Quirk mode adds HTTP/1.1 to newer HTTP headers or replaces them if needed.
    """
    UPNP_HEADER_QUIRK_HTTP_1_1_FORCED = 1 << 5
    """
Quirk mode replaces newer HTTP headers with HTTP/1.1.
    """
    UPNP_HEADER_QUIRK_HTTP_HIDDEN = 1 << 6
    """
Quirk mode to not add the HTTP version to the SERVER header at all.
    """
    UPNP_HEADER_QUIRK_UPNP_1_0 = 1 << 7
    """
Quirk mode adds UPnP/1.0 to the SERVER header.
    """
    UPNP_HEADER_QUIRK_UPNP_1_0_FORCED = 1 << 8
    """
Quirk mode replaces newer UPnP versions with UPnP/1.0.
    """
    UPNP_HEADER_QUIRK_UPNP_1_1 = 1 << 9
    """
Quirk mode adds UPnP/1.1 to the SERVER header.
    """
    UPNP_HEADER_QUIRK_UPNP_1_1_FORCED = 1 << 10
    """
Quirk mode replaces newer UPnP versions with UPnP/1.1.
    """

    _os_uname = uname()
    """
OS uname data
    """
    _pas_upnp_lock = InstanceLock()
    """
Thread safety lock
    """
    _pas_upnp_quirks_mode = 0
    """
The quirks mode adds non-standard behaviour to SSDP headers and messages.
    """

    @staticmethod
    def add_pas_upnp_quirks_mode(mode):
        """
Adds the defined quirks mode to the already activated ones.

:since: v0.2.00
        """

        if (type(mode) is str): mode = PasUpnpVersionMixin.get_pas_upnp_quirks_mode(mode)
        with PasUpnpVersionMixin._pas_upnp_lock: PasUpnpVersionMixin._pas_upnp_quirks_mode |= mode
    #

    @staticmethod
    def get_pas_upnp_http_header_string(distinct_version_required = False):
        """
Returns the supported HTTP specification string based on the currently
active quirks mode.

:param distinct_version_required: Returns exactly one supported HTTP version only

:return: (str) HTTP specification string
:since:  v0.2.00
        """

        _return = "HTTP/2.0"

        if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1 == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1):
            _return += " HTTP/1.1"
        #

        if (distinct_version_required):
            if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1 == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1
                or PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1_FORCED == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1_FORCED
               ): _return = "HTTP/1.1"
        elif (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_HIDDEN == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_HIDDEN):
            _return = ""
        elif (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1_FORCED == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1_FORCED):
            _return = "HTTP/1.1"
        #

        return _return
    #

    @staticmethod
    def get_pas_upnp_http_client_identifier_string():
        """
Returns the PAS UPnP HTTP client identifier string.

:return: (str) HTTP client identifier string
:since:  v0.2.00
        """

        _return = "pasUPnP/#echo(pasUPnPIVersion)# {0} DLNADOC/{1}"

        return _return.format(PasUpnpVersionMixin._get_pas_upnp_spec_string(),
                              PasUpnpVersionMixin.DLNADOC_VERSION_SUPPORTED
                             )
    #

    @staticmethod
    def get_pas_upnp_http_identifier_string():
        """
Returns the PAS UPnP identifier string used for the HTTP "Server" and
"User-Agent" headers.

:return: (str) HTTP header string
:since:  v0.2.00
        """

        _return = "{0}/{1} {2}"

        return _return.format(PasUpnpVersionMixin._get_pas_upnp_os_name(),
                              PasUpnpVersionMixin._get_pas_upnp_os_version(),
                              PasUpnpVersionMixin.get_pas_upnp_http_client_identifier_string()
                             )
    #

    @staticmethod
    def _get_pas_upnp_os_name():
        """
Returns the OS name based on the currently active quirks mode.

:return: (str) OS name
:since:  v0.2.00
        """

        if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_LINUX == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_LINUX): _return = "Linux"
        elif (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_WINDOWS == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_WINDOWS): _return = "Windows"
        else: _return = PasUpnpVersionMixin._os_uname[0]

        return _return
    #

    @staticmethod
    def _get_pas_upnp_os_version():
        """
Returns the OS version based on the currently active quirks mode.

:return: (str) OS version
:since:  v0.2.00
        """

        return ("1.0"
                if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_VERSION == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_VERSION) else
                PasUpnpVersionMixin._os_uname[2]
               )
    #

    @staticmethod
    def get_pas_upnp_quirks_mode(mode):
        """
Parses the given quirks mode string.

:param mode: String mode

:return: (int) Internal mode
:since:  v0.2.00
        """

        mode_set = mode.split("+")

        _return = 0

        for mode in mode_set:
            if (mode == "quirk_os_linux"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_LINUX
            elif (mode == "quirk_os_version"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_VERSION
            elif (mode == "quirk_os_windows"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_OS_WINDOWS
            elif (mode == "quirk_http_1_1"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1
            elif (mode == "quirk_http_1_1_forced"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_1_1_FORCED
            elif (mode == "quirk_http_hidden"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_HTTP_HIDDEN
            elif (mode == "quirk_upnp_1_0"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0
            elif (mode == "quirk_upnp_1_0_forced"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0_FORCED
            elif (mode == "quirk_upnp_1_1"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1
            elif (mode == "quirk_upnp_1_1_forced"): _return |= PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1_FORCED
        #

        return _return
    #

    @staticmethod
    def get_pas_upnp_sddp_identifier_string():
        """
Returns the PAS UPnP identifier string used for the SSDP "Server" header.

:return: (str) SSDP header string
:since:  v0.2.00
        """

        _return = "{0} {1}"

        _return = _return.format(PasUpnpVersionMixin.get_pas_upnp_http_identifier_string(),
                                 PasUpnpVersionMixin.get_pas_upnp_http_header_string()
                                )

        return _return.strip()
    #

    @staticmethod
    def _get_pas_upnp_spec_string():
        """
Returns the supported UPnP specification string based on the currently
active quirks mode.

:return: (str) UPnP specification string
:since:  v0.2.00
        """

        _return = "UPnP/2.0"

        if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1 == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1):
            _return += " UPnP/1.1"
        #

        if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0 == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0):
            _return += " UPnP/1.0"
        #

        if (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0_FORCED == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_0_FORCED):
            _return = "UPnP/1.0"
        elif (PasUpnpVersionMixin._pas_upnp_quirks_mode & PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1_FORCED == PasUpnpVersionMixin.UPNP_HEADER_QUIRK_UPNP_1_1_FORCED):
            _return = "UPnP/1.1"
        #

        return _return
    #

    @staticmethod
    def remove_pas_upnp_quirks_mode(mode):
        """
Removes the defined quirks mode from the activated ones.

:since: v0.2.00
        """

        with PasUpnpVersionMixin._pas_upnp_lock: PasUpnpVersionMixin._pas_upnp_quirks_mode &= ~mode
    #
#
