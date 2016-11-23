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

from dNG.runtime.type_exception import TypeException
from dNG.runtime.value_exception import ValueException

class CriteriaDefinition(object):
    """
"CriteriaDefinition" is an abstracted definition of UPnP search criteria
applied to an UPnP search interface instance for execution.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: upnp
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    AND = 1
    """
AND criteria concatenation
    """
    OR = 2
    """
OR criteria concatenation
    """
    TYPE_CASE_INSENSITIVE_MATCH = 3
    """
Matches if the property value matches the case insensitive criteria.
    """
    TYPE_CASE_INSENSITIVE_NO_MATCH = 4
    """
Matches if the property value does not match the case sensitive criteria.
    """
    TYPE_DEFINED_MATCH = 5
    """
Matches if the property is defined.
    """
    TYPE_DERIVED_CRITERIA = 11
    """
Matches if the property (upnp:class) is derived from the value.
    """
    TYPE_EXACT_MATCH = 1
    """
Matches if the property value matches the criteria exactly.
    """
    TYPE_EXACT_NO_MATCH = 2
    """
Matches if the property value does not match the criteria exactly.
    """
    TYPE_GREATER_THAN_MATCH = 9
    """
Matches if the property value is greater than the criteria.
    """
    TYPE_GREATER_THAN_OR_EQUAL_MATCH = 10
    """
Matches if the property value is greater than or equals the criteria.
    """
    TYPE_LESS_THAN_MATCH = 7
    """
Matches if the property value is less than the criteria.
    """
    TYPE_LESS_THAN_OR_EQUAL_MATCH = 8
    """
Matches if the property value is less than or equals the criteria.
    """
    TYPE_NOT_DEFINED_MATCH = 6
    """
Matches if the property is not defined.
    """
    TYPE_SUB_CRITERIA = 12
    """
Criteria contains a sub criteria definition.
    """

    def __init__(self, concatenation = OR):
        """
Constructor __init__(CriteriaDefinition)

:since: v0.2.00
        """

        self.concatenation = None
        """
Type of criteria concatenation
        """
        self.criteria = [ ]
        """
List of criteria
        """

        self.set_concatenation(concatenation)
    #

    def add_case_insensitive_match_criteria(self, _property, value):
        """
Adds a case insensitive criteria to match the given value.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_CASE_INSENSITIVE_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_case_insensitive_no_match_criteria(self, _property, value):
        """
Adds a case insensitive criteria to not match the given value.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_CASE_INSENSITIVE_NO_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_derived_match_criteria(self, _property, value):
        """
Adds a criteria to match if the property is derived from the given value.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_DERIVED_CRITERIA,
                               "property": _property,
                               "value": value
                             })
    #

    def add_exact_match_criteria(self, _property, value):
        """
Adds a criteria to match the given value exactly.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_EXACT_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_exact_no_match_criteria(self, _property, value):
        """
Adds a criteria to not match the given value exactly.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_EXACT_NO_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_is_defined_criteria(self, _property):
        """
Adds a criteria to match the given value exactly.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_DEFINED_MATCH,
                               "property": _property
                             })
    #

    def add_is_not_defined_criteria(self, _property):
        """
Adds a criteria to not match the given value exactly.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_NOT_DEFINED_MATCH,
                               "property": _property
                             })
    #

    def add_greater_than_match_criteria(self, _property, value):
        """
Adds a criteria to match values greater than the given one.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_GREATER_THAN_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_greater_than_or_equal_match_criteria(self, _property, value):
        """
Adds a criteria to match values greater than or equal the given one.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_GREATER_THAN_OR_EQUAL_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_less_than_match_criteria(self, _property, value):
        """
Adds a criteria to match values less than the given one.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_LESS_THAN_MATCH,
                               "_property": property,
                               "value": value
                             })
    #

    def add_less_than_or_equal_match_criteria(self, _property, value):
        """
Adds a criteria to match values less than or equal the given one.

:param _property: UPnP property
:param value: Criteria value

:since: v0.2.00
        """

        self.criteria.append({ "type": CriteriaDefinition.TYPE_LESS_THAN_OR_EQUAL_MATCH,
                               "property": _property,
                               "value": value
                             })
    #

    def add_sub_criteria(self, criteria_definition):
        """
Adds the given criteria definition as a sub criteria.

:param criteria_definition: CriteriaDefinition instance

:since: v0.2.00
        """

        if (not isinstance(criteria_definition, CriteriaDefinition)): raise TypeException("Given criteria definition type is invalid")

        if (criteria_definition.get_criteria_count() > 0):
            self.criteria.append({ "type": CriteriaDefinition.TYPE_SUB_CRITERIA,
                                   "criteria_definition": criteria_definition
                                 })
            #
    #

    def clear(self):
        """
Clears the current criteria list.

:since: v0.2.00
        """

        self.criteria = [ ]
    #

    def get_concatenation(self):
        """
Returns the concatenation used for this criteria definition.

:retrun: (int) Concatenation type
:since:  v0.2.00
        """

        return self.concatenation
    #

    def get_criteria(self):
        """
Returns the list of defined criteria.

:return: (list) List of criteria dictionaries
:since:  v0.2.00
        """

        return self.criteria
    #

    def get_criteria_count(self):
        """
Returns the number of defined criteria.

:return: (int) Criteria count
:since:  v0.2.00
        """

        return len(self.criteria)
    #

    def set_concatenation(self, concatenation):
        """
Sets the concatenation used for this criteria definition.

:param concatenation: Concatenation

:since: v0.2.00
        """

        if (concatenation not in ( CriteriaDefinition.AND, CriteriaDefinition.OR )): raise ValueException("Given criteria concatenation is invalid")
        self.concatenation = concatenation
    #
#
