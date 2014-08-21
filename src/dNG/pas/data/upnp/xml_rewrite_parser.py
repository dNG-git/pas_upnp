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

import re

from dNG.pas.data.text.tag_parser.abstract import Abstract as AbstractTagParser
from dNG.pas.data.text.tag_parser.xml_if_condition_mixin import XmlIfConditionMixin
from dNG.pas.data.text.tag_parser.xml_rewrite_mixin import XmlRewriteMixin
from dNG.pas.module.named_loader import NamedLoader

class XmlRewriteParser(AbstractTagParser, XmlIfConditionMixin, XmlRewriteMixin):
#
	"""
The "XmlRewriteParser" takes a template string to render data based on XML
node values.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: core
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Parser)

:since: v0.1.00
		"""

		AbstractTagParser.__init__(self)

		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.xml_node_path = None
		"""
XML node path containing value nodes
		"""
		self.xml_parser = None
		"""
XML parser containing replacements
		"""
	#

	def _change_match(self, tag_definition, data, tag_position, data_position, tag_end_position):
	#
		"""
Change data according to the matched tag.

:param tag_definition: Matched tag definition
:param data: Data to be parsed
:param tag_position: Tag starting position
:param data_position: Data starting position
:param tag_end_position: Starting position of the closing tag

:return: (str) Converted data
:since:  v0.1.00
		"""

		_return = data[:tag_position]

		data_closed = data[self._find_tag_end_position(data, tag_end_position):]

		if (tag_definition['tag'] == "if"):
		#
			re_result = re.match("^\\[if:(.+?)(\\!=|==)(.*?)\\]", data[tag_position:data_position])

			xml_value_path = (None if (re_result == None) else re_result.group(1).strip())

			if (xml_value_path != None):
			#
				operator = re_result.group(2)
				value = re_result.group(3).strip()

				_return += self.render_xml_if_condition(self.xml_parser, self.xml_node_path, xml_value_path, operator, value, data[data_position:tag_end_position])
			#
		#
		elif (tag_definition['tag'] == "rewrite"):
		#
			xml_value_path = data[data_position:tag_end_position]
			_return += self.render_xml_rewrite(self.xml_parser, self.xml_node_path, xml_value_path)
		#

		_return += data_closed

		return _return
	#

	def _check_match(self, data):
	#
		"""
Check if a possible tag match is a false positive.

:param data: Data starting with the possible tag

:return: (dict) Matched tag definition; None if false positive
:since:  v0.1.00
		"""

		_return = None

		i = 0
		tags = [ "if", "rewrite" ]
		tags_length = len(tags)

		while (_return == None and i < tags_length):
		#
			tag = tags[i]
			data_match = data[1:1 + len(tag)]

			if (data_match == "if"):
			#
				re_result = re.match("^\\[if:.+?(\\!=|==).*?\\]", data)
				if (re_result != None): _return = { "tag": "if", "tag_end": "[/if]", "type": "top_down" }
			#
			elif (data_match == "rewrite"):
			#
				re_result = re.match("^\\[rewrite\\]", data)
				if (re_result != None): _return = { "tag": "rewrite", "tag_end": "[/rewrite]" }
			#

			i += 1
		#

		return _return
	#

	def render(self, template_data, xml_parser, xml_node_path):
	#
		"""
Renders content with the given template.

:param template_data: Template data
:param xml_parser: XML parser instance
:param xml_node_path: XML base path

:return: (str) Rendered content
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.render({1})- (#echo(__LINE__)#)", self, xml_node_path, context = "pas_upnp")

		self.xml_node_path = xml_node_path
		self.xml_parser = xml_parser

		return self._parse(template_data)
	#
#

##j## EOF