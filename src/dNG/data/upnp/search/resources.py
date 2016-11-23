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

from dNG.data.settings import Settings
from dNG.data.supports_mixin import SupportsMixin
from dNG.data.upnp.client_settings_mixin import ClientSettingsMixin
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook
from dNG.runtime.exception_log_trap import ExceptionLogTrap
from dNG.runtime.io_exception import IOException
from dNG.runtime.type_exception import TypeException
from dNG.runtime.value_exception import ValueException

from .criteria_definition import CriteriaDefinition

class Resources(ClientSettingsMixin, SupportsMixin):
    """
The "Resources" search instance is used to execute UPnP searches.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    SORT_ASCENDING = "+"
    """
Ascending sort direction
    """
    SORT_DESCENDING = "-"
    """
Descending sort direction
    """

    def __init__(self):
        """
Constructor __init__(Resources)

:since: v0.2.00
        """

        ClientSettingsMixin.__init__(self)
        SupportsMixin.__init__(self)

        self.criteria_definition = None
        """
UPnP search criteria definition instance
        """
        self.executed = False
        """
True if search has been executed and results are ready
        """
        self.limit = 50
        """
UPnP resource search results limit
        """
        self.limit_max = int(Settings.get("pas_upnp_resource_search_limit_max", 50))
        """
UPnP resource search results limit
        """
        self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self.offset = 0
        """
UPnP resource search results offset
        """
        self.resources = [ ]
        """
UPnP resources matching the criteria definition
        """
        self.total = 0
        """
UPnP resource search results count from all segments
        """
        self.root_resource = None
        """
UPnP root resource for searching matches
        """
        self.sort_tuples = [ ]
        """
Sort list to be applied
        """

        self.supported_features['sortable'] = self._supports_sortable
    #

    def add_sort_definition(self, _property, direction):
        """
Adds a sort definition.

:param _property: UPnP property to sort
:param direction: Sort direction

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_sort_definition({1}, {2})- (#echo(__LINE__)#)", self, _property, direction, context = "pas_upnp")

        if (direction not in ( Resources.SORT_ASCENDING, Resources.SORT_DESCENDING )): raise TypeException("Sort direction given is invalid")
        self.sort_tuples.append(( _property, direction ))
    #

    def _execute(self):
        """
Executes the search to calculate the total number of matches and the UPnP
resource search results list as defined by "offset" and "limit".

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._execute()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (self.criteria_definition is None): raise ValueException("UPnP search criteria instance is not defined")
        if (self.executed): raise IOException("UPnP resource search should not be executed twice")

        segments = self._get_segments()
        self.executed = True

        if (type(segments) is list and len(segments) > 0):
            offset = self.offset
            limit = self.limit

            for segment in segments:
                with ExceptionLogTrap("pas_upnp"):
                    segment.set_criteria_definition(self.criteria_definition)
                    resources_count = segment.get_count()

                    self.total += resources_count

                    if (offset >= resources_count): offset -= resources_count
                    elif (resources_count > 0
                          and (limit is None or len(self.resources) < self.limit)
                         ):
                        segment.set_sort_tuples(self.sort_tuples)

                        segment.set_offset(offset)
                        if (limit is not None): segment.set_limit(limit)

                        resources_list = segment.get_list()
                        resources_list_count = len(resources_list)

                        if (offset > 0):
                            if (offset > resources_list_count): offset -= resources_list_count
                            else: offset = 0
                        #

                        if (limit is not None): limit -= resources_list_count

                        self.resources += resources_list
                    #
                #
            #
        #
    #

    def get(self, position):
        """
Returns the UPnP resource search result at the given position.

:param position: Position of the UPnP resource search result to be returned

:return: (object) UPnP resource; None if position is undefined
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get({1:d})- (#echo(__LINE__)#)", self, position, context = "pas_upnp")

        results_list = self.get_list()

        return (results_list[position]
                if (position >= 0 and len(results_list) > position) else
                None
               )
    #

    def get_count(self):
        """
Returns the total number of matches.

:return: (int) Number of matches
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_count()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (not self.executed): self._execute()
        return self.total
    #

    def get_list(self):
        """
Returns the list of UPnP resource search results as defined by "offset" and
"limit".

:return: (list) List of search results
:since:  v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_list()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (not self.executed): self._execute()
        return self.resources
    #

    def _get_segments(self):
        """
Returns the search segment instances.

:return: (list) List of search segments; None if not registered
:since:  v0.2.00
        """

        return (Hook.call("dNG.pas.upnp.Resource.getSearchSegments",
                          criteria_definition = self.criteria_definition
                         )
                if (self.root_resource is None) else
                Hook.call("dNG.pas.upnp.Resource.getSearchSegments",
                          id = self.root_resource.get_resource_id(),
                          criteria_definition = self.criteria_definition
                         )
               )
    #

    def set_criteria_definition(self, criteria_definition):
        """
Sets the UPnP search criteria definition used.

:param criteria_definition: Criteria definition instance

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_criteria_definition()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (not isinstance(criteria_definition, CriteriaDefinition)): raise TypeException("UPnP search criteria instance given is invalid")
        if (self.executed): raise IOException("UPnP resource search can not be modified after execution")

        self.criteria_definition = criteria_definition
    #

    def set_limit(self, limit):
        """
Sets the UPnP resource search results limit.

:param limit: Results limit

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_limit({1:d})- (#echo(__LINE__)#)", self, limit, context = "pas_upnp")

        if (self.executed): raise IOException("UPnP resource search can not be modified after execution")
        self.limit = (limit if (limit < self.limit_max) else self.limit_max)
    #

    def set_offset(self, offset):
        """
Sets the UPnP resource search results offset.

:param offset: Results offset

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_offset({1:d})- (#echo(__LINE__)#)", self, offset, context = "pas_upnp")

        if (self.executed): raise IOException("UPnP resource search can not be modified after execution")
        self.offset = offset
    #

    def set_root_resource(self, resource):
        """
Sets the UPnP root resource for searching matches.

:param resource: UPnP search root resource

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_root_resource()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        if (self.executed): raise IOException("UPnP resource search can not be modified after execution")
        self.root_resource = resource
    #

    def set_sort_criteria(self, criteria_list):
        """
Sets the UPnP sort criteria for search matches.

:param criteria_list: UPnP search sort criteria list

:since: v0.2.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_sort_criteria()- (#echo(__LINE__)#)", self, context = "pas_upnp")

        self.sort_tuples = [ ]

        for criteria in criteria_list:
            criteria_first_char = criteria[:1]
            if (criteria_first_char == "+" or criteria_first_char == "-"): criteria = criteria[1:]
            direction = (Resources.SORT_ASCENDING if (criteria_first_char == "+") else Resources.SORT_DESCENDING)

            self.sort_tuples.append(( criteria, direction ))
        #
    #

    def _supports_sortable(self):
        """
Returns false if sorting is not supported.

:return: (bool) True if sorting of search results is supported
:since:  v0.2.00
        """

        segments = self._get_segments()
        return (type(segments) is list and len(segments) == 1)
    #
#
