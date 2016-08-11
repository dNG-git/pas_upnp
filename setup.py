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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
setup.py
"""

def get_versions():
#
	"""
Returns the version currently in development.

:return: (tuple) Tuple of version string and internal version value
:since:  v0.1.03
	"""

	return ( "v0.2.00", "0.00200" )
#

from dNG.distutils.command.build_py import BuildPy
from dNG.distutils.command.install_data import InstallData
from dNG.distutils.temporary_directory import TemporaryDirectory

from distutils.core import setup
from os import path

with TemporaryDirectory(dir = ".") as build_directory:
#
	versions = get_versions()

	parameters = { "install_data_plain_copy_extensions": "json",
	               "pasUPnPVersion": versions[0], "pasUPnPIVersion": versions[1]
	             }

	InstallData.add_install_data_callback(InstallData.plain_copy, [ "data" ])
	InstallData.set_build_target_path(build_directory)
	InstallData.set_build_target_parameters(parameters)

	_build_path = path.join(build_directory, "src")

	setup(name = "pas_upnp",
	      version = versions[0],
	      description = "Python Application Services",
	      long_description = """"pas_upnp" provides the infrastructure to build UPnP client and / or server applications.""",
	      author = "direct Netware Group et al.",
	      author_email = "web@direct-netware.de",
	      license = "GPLv2+",
	      url = "https://www.direct-netware.de/redirect?pas;upnp",

	      platforms = [ "any" ],

	      package_dir = { "": _build_path },
	      packages = [ "dNG" ],

	      data_files = [ ( "docs", [ "LICENSE", "README" ]) ],

	      # Override build_py to first run builder.py over all PAS modules
	      cmdclass = { "build_py": BuildPy,
	                   "install_data": InstallData
	                 }
	)
#

##j## EOF