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

import re

from dNG.runtime.value_exception import ValueException

from .criteria_definition import CriteriaDefinition

class CriteriaParser(object):
    """
The UPnP "CriteriaParser" parses a string to generate the
"CriteriaDefinition" instance.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    RE_ESCAPED = re.compile("(\\\\+)$")
    """
RegExp to find escape characters
    """
    VALID_OPERATORS = ( "=",
                        "!=",
                        "<",
                        "<=",
                        ">",
                        ">=",
                        "contains",
                        "doesNotContain",
                        "derivedfrom",
                        "derivedFrom",
                        "startsWith",
                        "exists"
                      )
    """
Valid UPnP search criteria operators
    """

    def parse(self, criteria):
        """
Parse the given search criteria string.

:param criteria: UPnP criteria definition to be parsed

:return: (object) CriteriaDefinition instance
:since:  v0.2.00
        """

        return (CriteriaDefinition()
                if (criteria.strip() == "*") else
                self._parse_conditions_walker(criteria)[0]
               )
    #

    def _parse_concatenation_operator(self, data):
        """
Parses data for the concatenation operator.

:param data: Data to be parsed

:return: (tuple) Concatenation mode (None if last) and remaining data
:since:  v0.2.00
        """

        _return = None

        data = data.lstrip()

        if (data[:2] == "or"):
            data = data[2:]
            _return = CriteriaDefinition.OR
        elif (data[:3] == "and"):
            data = data[3:]
            _return = CriteriaDefinition.AND
        elif (data != ""): raise ValueException("UPnP search criteria definition is not well formed")

        if (data != ""): data = data.lstrip()

        return ( _return, data )
    #

    def _parse_conditions_walker(self, data, sub_level = 0):
        """
Parses the conditions recursively and adds it to the given criteria
definition instance.

:param data: Data to be parsed
:param sub_level: Criteria nesting level

:return: (tuple) CriteriaDefinition instance and remaining data
:since:  v0.2.00
        """

        _return = CriteriaDefinition()

        and_criteria_definition = None
        concatenation = None
        data = data.lstrip()
        is_sub_level_closed = False

        while (data != ""):
            next_concatenation = None
            sub_criteria_definition = None

            if (data[:1] == "("):
                ( sub_criteria_definition, data ) = self._parse_conditions_walker(data[1:], 1 + sub_level)
            else:
                data_splitted = data.split(maxsplit = 1)
                if (len(data_splitted) < 2): raise ValueException("UPnP search criteria definition is not well formed")

                data = data_splitted[1]
                _property = data_splitted[0].lower()

                data_splitted = data.split(maxsplit = 1)
                data = ("" if (len(data_splitted) < 2) else data_splitted[1].lstrip())
                operator = data_splitted[0]

                if (operator not in CriteriaParser.VALID_OPERATORS): raise ValueException("UPnP search criteria definition is not well formed")

                ( value, data ) = self._parse_value(data)
            #

            if (data != ""):
                if (data[:1] != ")"): ( next_concatenation, data ) = self._parse_concatenation_operator(data)
                elif (sub_level > 0):
                    data = data[1:]
                    is_sub_level_closed = True
                else: raise ValueException("UPnP search criteria definition is not well formed")
            #

            if (concatenation is None
                and next_concatenation is not None
               ): concatenation = next_concatenation

            if (concatenation == CriteriaDefinition.AND):
                if (and_criteria_definition is None): and_criteria_definition = CriteriaDefinition(CriteriaDefinition.AND)
                criteria_definition = and_criteria_definition
            else:
                if (and_criteria_definition is not None):
                    _return.add_sub_criteria(and_criteria_definition)
                    and_criteria_definition = None
                #

                criteria_definition = _return
            #

            if (sub_criteria_definition is not None):
                if (sub_criteria_definition.get_criteria_count() > 0): criteria_definition.add_sub_criteria(sub_criteria_definition)
            elif (operator == "="): criteria_definition.add_exact_match_criteria(_property, value)
            elif (operator == "!="): criteria_definition.add_exact_no_match_criteria(_property, value)
            elif (operator == "<"): criteria_definition.add_less_than_match_criteria(_property, value)
            elif (operator == "<="): criteria_definition.add_less_than_or_equal_match_criteria(_property, value)
            elif (operator == ">"): criteria_definition.add_greater_than_match_criteria(_property, value)
            elif (operator == ">="): criteria_definition.add_greater_than_or_equal_match_criteria(_property, value)
            elif (operator == "contains"): criteria_definition.add_case_insensitive_match_criteria(_property, value)
            elif (operator == "doesNotContain"): criteria_definition.add_case_insensitive_no_match_criteria(_property, value)
            elif (operator in ( "derivedfrom", "derivedFrom" )): criteria_definition.add_derived_match_criteria(_property, value)
            elif (operator == "startsWith"): criteria_definition.add_case_insensitive_match_criteria(_property, "{0}*".format(value))
            elif (operator == "exists"):
                if (value == "true"): criteria_definition.add_is_defined_criteria(_property)
                else: criteria_definition.add_is_not_defined_criteria(_property)
            #

            data = data.lstrip()

            if (next_concatenation is not None
                and concatenation != next_concatenation
               ): concatenation = next_concatenation

            if (is_sub_level_closed): break
        #

        if (and_criteria_definition is not None):
            if (_return.get_criteria_count() < 1): _return = and_criteria_definition
            else: _return.add_sub_criteria(and_criteria_definition)
        #

        return ( _return, data )
    #

    def _parse_value(self, data):
        """
Parses data for the value.

:param data: Data to be parsed

:return: (tuple) Value and remaining data
:since:  v0.2.00
        """

        _return = ""

        data = data.lstrip()

        if (data[:1] == "\""):
            value_list = [ ]

            while (data != ""):
                data_splitted = data[1:].split("\"", 1)
                if (len(data_splitted) < 2): raise ValueException("UPnP search criteria definition is not well formed")

                re_result = CriteriaParser.RE_ESCAPED.search(data_splitted[0])

                value_list.append(data_splitted[0])
                data = data_splitted[1]

                if (re_result is None or (len(re_result.group(1)) % 2) == 0): break
            #

            _return = " ".join(value_list)
        else:
            data_splitted = data.split(maxsplit = 1)

            data = ("" if (len(data_splitted) < 2) else data_splitted[1])

            if (data_splitted[0][-1:] == ")"):
                data = ")" + data
                _return = data_splitted[0][:-1]
            else: _return = data_splitted[0]
        #

        if (data != ""): data = data.lstrip()

        return ( _return, data )
    #
#
