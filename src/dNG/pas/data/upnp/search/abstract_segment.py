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

from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from dNG.pas.runtime.type_exception import TypeException
from .criteria_definition import CriteriaDefinition

class AbstractSegment(object):
#
	"""
"AbstractSegment" is the abstract UPnP search segment class.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractSegment)

:since: v0.1.03
		"""

		self.criteria_definition = None
		"""
UPnP search criteria definition instance
		"""
		self.limit = 50
		"""
UPnP resource search segment results limit
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.offset = 0
		"""
UPnP resource search segment results offset
		"""
	#

	def get(self, position):
	#
		"""
Returns the UPnP search segment result at the given position.

:param position: Position of the UPnP search segement result to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.1.01
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get({1:d})- (#echo(__LINE__)#)", self, position, context = "pas_upnp")

		results_list = self.get_list()

		return (results_list[position]
		        if (position >= 0 and len(results_list) > position) else
		        None
		       )
	#

	def get_count(self):
	#
		"""
Returns the total number of matches in this UPnP search segment.

:return: (int) Number of matches
:since:  v0.1.03
		"""

		raise NotImplementedException()
	#

	def get_list(self):
	#
		"""
Returns the list of UPnP resource search segment results as defined by
"offset" and "limit".

:return: (list) List of search segment results
:since:  v0.1.03
		"""

		raise NotImplementedException()
	#

	def set_criteria_definition(self, criteria_definition):
	#
		"""
Sets the UPnP search criteria definition used.

:param criteria_definition: Criteria definition instance

:since: v0.1.03
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_criteria_definition()- (#echo(__LINE__)#)", self, context = "pas_upnp")

		if (not isinstance(criteria_definition, CriteriaDefinition)): raise TypeException("UPnP search criteria instance given is invalid")
		self.criteria_definition = criteria_definition
	#

	def set_limit(self, limit):
	#
		"""
Sets the UPnP resource search segment results limit.

:param limit: Results limit

:since: v0.1.03
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_limit({1:d})- (#echo(__LINE__)#)", self, limit, context = "pas_upnp")
		self.limit = limit
	#

	def set_offset(self, offset):
	#
		"""
Sets the UPnP resource search segment results offset.

:param offset: Results offset

:since: v0.1.03
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_offset({1:d})- (#echo(__LINE__)#)", self, offset, context = "pas_upnp")
		self.offset = offset
	#
#

##j## EOF