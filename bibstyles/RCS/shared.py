head	1.3;
access;
symbols;
locks; strict;
comment	@# @;


1.3
date	2006.08.31.00.04.43;	author schwilk;	state Exp;
branches;
next	1.2;

1.2
date	2006.08.03.20.10.07;	author schwilk;	state Exp;
branches;
next	1.1;

1.1
date	2006.08.03.20.06.20;	author schwilk;	state Exp;
branches;
next	;


desc
@@


1.3
log
@Alan Isaac's changes.
@
text
@#File: shared.py
"""
Utilities and formatting classes for BibStuff,
especially for bib4txt.py.

:author: Alan G Isaac
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006 by Alan G. Isaac
:license: MIT (see `license.txt`_)
:date: 2006-08-01

.. _license.txt: ./license.txt
"""
__docformat__ = "restructuredtext en"
__version__ = "$Revision: 1.2 $"

###################  IMPORTS  ##################################################
#import from standard library
import simpleparse
import logging
shared_logger = logging.getLogger('bibstuff_logger')
################################################################################

#allow for a single citation reference to have keys for multiple citations
#ordinarily, you do not override this
CITE_SEP = ','

def append_sep(s,sep):
	"""return s+sep after removing duplicate punctuation at the join
	`s`: string
	`sep`: string
	TODO? restrict characters removed
	"""
	if s[-1]==sep[0]:
		sep = sep[1:]
	return s+sep

def reformat_para(para='',left=0,right=72,just='LEFT'):
	"""Simple paragraph reformatter.  Allows specification
	of left and right margins, and of justification style
	(using constants defined in module).
	:note: Adopted by Schwilk from David Mertz's example in TPiP
	:see:  Mertz, David,  *Text Processing in Python* (TPiP)
	"""
	LEFT,RIGHT,CENTER = 'LEFT','RIGHT','CENTER'
	words = para.split()
	lines = []
	line  = ''
	word = 0
	end_words = 0
	while not end_words:
		if len(words[word]) > right-left: # Handle very long words
			line = words[word]
			word +=1
			if word >= len(words):
				end_words = 1
		else:							 # Compose line of words
			while len(line)+len(words[word]) <= right-left:
				line += words[word]+' '
				word += 1
				if word >= len(words):
					end_words = 1
					break
		lines.append(line)
		line = ''
	if just.upper() == CENTER:
		r, l = right, left
		return '\n'.join([' '*left+ln.center(r-l) for ln in lines])
	elif just.upper() == RIGHT:
		return '\n'.join([line.rjust(right) for line in lines])
	else: # left justify
		return '\n'.join([' '*left+line for line in lines])

class NamesFormatter(object):
	"""Provides a formatter for BibName instances.

	:see: documentation for the `NameFormatter` class
	:note: 2006-08-03 add initials keyword to ``__init__``
	"""
	def __init__(self, citation_template=None, template_list=None, initials=''):
		shared_logger.debug("NamesFormatter.__init__ args: "+str((citation_template,template_list,initials)))
		assert(template_list or citation_template,"Must provide formatting templates.")
		if citation_template:
			self.citation_template = citation_template
			self.template_list = [citation_template['name_first'], citation_template['name_other']]
			self.initials = citation_template['initials']
			self.etal = citation_template['etal']
			self.max_citation_names = citation_template['max_citation_names']
			self.name_name_sep = citation_template['name_name_sep']
		else: #set defaults
			self.template_list = template_list
			self.initials = initials
			self.etal = "et al."
			self.max_citation_names = 99
			self.name_name_sep = (', ', ', and ')
		self.formatters = [ NameFormatter(template,self.initials) for template in self.template_list ]

	"""
	def get_formatted(self,names):
		shared_logger.warn("NamesFormatter.get_formatted is deprecated; use 'format_names'")
		return self.format_names(names)
	"""
	#get all names, formatted as a string
	def format_names(self,names):
		"""Return `names` as a formatted string.

		Formats `names` according to the `NamesFormatter` template.

		`NAME FORMATTING TEMPLATES`_ are explained in some detail
		in the doc string for the NameFormatter class.  Briefly:

		Template sections are separated by ``|``.
		Name parts are referred to by first letter: (v)on, (l)last, (j)r or (f)irst.
		These letters may be followed by token separator enclosed in curly braces.
		Any other characters are included as is.

		:type `names`: BibName object
		:note: 2006-07-25 radically refactored from bibname.py's FormatName() function

		.. _`NAME FORMATTING TEMPLATES`: bibstyles/shared.py
		"""
		shared_logger.debug("NamesFormatter.format: Type of names data is "+str(type(names)))
		#get the list of name_dicts from the BibName instance
		names_dicts = names.get_names_dicts()
		num_names = len(names_dicts)

		#now make a list of formatted names
		#the first name formatted with the first formatter no matter what
		formatted_name_list = [ self.formatters[0].format_name(names_dicts[0]) ]
		#any additional names are formatted with the second formatter (unless too many -> etal)
		if num_names > 1 and num_names <= self.max_citation_names:
			for name_dict in names_dicts[1:]:  #for each name ...
				formatted_name_list.append( self.formatters[1].format_name(name_dict) )
		shared_logger.debug("NamesFormatter.format_names: formatted_name_list: "+str(formatted_name_list))

		#formatted_name_list = [' '.join(names_dicts[0]['last'])]

		#now concatenate the formatted names into the desired result
		result = formatted_name_list.pop(0)
		#first concatenate all but the last
		while len(formatted_name_list) > 1:
			result = append_sep(result,self.name_name_sep[0]) + formatted_name_list.pop(0)
		#finally, add on the last (with the different name_name_sep)
		if formatted_name_list:
			final_name = formatted_name_list.pop(0)
			if final_name != "others":
				result = append_sep(result,self.name_name_sep[1]) + final_name
			else:
				result = append_sep(result,self.etal)
		assert(len(formatted_name_list) == 0)  #obviously
		if num_names > self.max_citation_names:
			result = append_sep(result,self.etal)
		return result


class NameFormatter(object):
	"""Create a NameFormatter object based on a template string.
	
	NAME FORMATTING TEMPLATES
	-------------------------

	The name template takes some explanation.
	Name parts are referred to by part-designator, which is just the part's first letter:
	(v)on, (l)last, (j)r or (f)irst.
	Each name part may have one associated section in a name formatting template.
	Sections are separated by '|' and must include a part-designator (one of 'fvlj').
	The presumption is that part-designators will be the only alphabetic characters in a name template.
	A section will generate output iff the name part for that section exists.
	Each section may have a partsep
	(in curly braces, immediately following the part-designator)
	and other characters
	(which may not be any of 'fvlj').
	The partsep indicates what should separate multiple tokens of the same part
	(e.g., two part last names, or 'van der' for the (v)on part).
	A part separator will replace the default space to separate multiple tokens in a part.
	Any other characters are included as is.

	For example::

		   "v{~}~|l,| j,| f{. }." with initials=True produces:
		   "McFeely, J. W." or "van~der~Stadt, jr, C. M."

	:note: has a property -> must be new style class, inherit carefully
	"""
	def __init__(self, template, initials=''):
		shared_logger.debug("NameFormatter.__init__ args: "+str((template,initials)))
		#set a default partsep
		#:note: not planning to parameterize this default (e.g., in the citation template)
		self.default_partsep = ' '
		#self.partdict = {}  #this will be set by set_template
		self.initials = initials
		self.set_template(template)

	"""
	def get_formatted(self,name_data):
		shared_logger.warn("NameFormatter.get_formatted is deprecated; use 'format_name'")
		return self.format_name(name_data)
	"""
	#get one name, formatted
	def format_name(self,name_data):
		"""Return one name (stored in `name_data`) as a formatted string.

		Formats `name_data` according to the `NameFormatter` template.

		:param `name_data`: list of name_parts or name as string
		:type `name_data`: list or string
		"""
		shared_logger.debug("NameFormatter.format_name:\nType of name_data is: "+str(type(name_data)))
		if isinstance( name_data, (list,tuple) ):
			shared_logger.debug("Assume list is a name_parts list.")
			result = self.name_parts2formatted(name_data)  #TODO: currently commented out for testing dicts
		elif isinstance(name_data, dict):
			shared_logger.debug("Assume dict is a name_dict.")
			result = self.name_dict2formatted(name_data)
		elif isinstance(name_data, str):
			result = name_data
		else:
			raise ValueError("Unrecognized name_data type.")
		shared_logger.debug("NameFormatter.format_name result: '"+result+"'")
		return result

	'''
	def name_parts2formatted(self,name_parts):
		"""Returns one fully formatted name, based on a name_parts tuple.
		"""
		shared_logger.debug("name_parts2formatted: name_parts is "+str(name_parts))
		partdict = self.partdict
		shared_logger.debug("name_parts2formatted: partdict is "+str(partdict))
		result = ''
		#name_parts have a fixed order, and each part is a list (e.g., of one person's last names)
		map_names_parts = dict(f=0, v=1, l=2, j=3)
		if self.initials:
			f,v,l,j = name_parts
			name_parts = ([s[0] for s in f],v,l,j)
		for partcode in partdict['parts_order']:
			partsep = partdict[partcode]['partsep']
			part = partsep.join(name_parts[map_names_parts[partcode]])
			if part:
				result += partdict[partcode]['pre'] + part + partdict[partcode]['post']
			shared_logger.debug("%s: %s"%(partcode,result))
		return result
	'''

	def name_dict2formatted(self,name_dict):
		"""Returns one fully formatted name, based on a name_dict.
		"""
		assert( len(name_dict['last'][0]) > 0 )
		if name_dict['last'][0] == "others":
			return "others"
		shared_logger.debug("name_dict2formatted: name_dict is "+str(name_dict))
		partdict = self.partdict
		shared_logger.debug("name_dict2formatted: partdict is "+str(partdict))
		result = ''
		#name_dict has keys, and each value is a list (e.g., of one person's last names)
		map_names_parts = dict(f='first', v='von', l='last', j='jr')
		if self.initials:
			name_dict = name_dict.copy()
			for partcode in self.initials:
				part_key = map_names_parts[partcode]
				name_dict[part_key] = [s[0] for s in name_dict[part_key]]
		for partcode in partdict['parts_order']:  #keep the parts in the template determined order
			partsep = partdict[partcode]['partsep']
			part = partsep.join(name_dict[map_names_parts[partcode]])
			if part:
				result += partdict[partcode]['pre'] + part + partdict[partcode]['post']
			shared_logger.debug("%s: %s"%(partcode,result))
		return result

	def get_template(self):
		return self._template
	def set_template(self,template):
		"""
		sets the name formatting template *and* sets the associated partdict used for actual formatting

		"""
		shared_logger.debug("NameFormatter.set_template args: "+str(template))
		assert(isinstance(template,str),"Must provide a name-template string to make a NameFormatter object.")
		self._template = template
		self.partdict = self.template2dict(template)
	template = property(get_template,set_template,None,"template property")

	def template2dict(self,template):
		"""
		parse the name formatting template into a partdict to be used for actual formatting

		:note: parsing a name template into a partdict is too trivial to turn to simpleparse, so just do it here
		"""
		#to keep track of the order of the parts...
		parts_order = ''
		template_parts = template.split('|')
		partdict = {}
		for part in template_parts:
			for partid in 'fvlj':
				if partid in part:
					parts_order += partid
					pre, temp = part.split(partid)
					if temp and temp[0] == '{':   #found a partsep
						partsep,post = temp[1:].split('}')
					else:
						post = temp
						partsep = self.default_partsep
					partdict[partid] = dict(pre=pre,post=post,partsep=partsep)
					break
		shared_logger.debug("template2dict: name formatting template parsed to:\n"+str(partdict))
		partdict['parts_order'] = parts_order
		return partdict


class CitationManager(object):
	"""
	:TODO: possibly useful for bibsearch.py
	"""
	def __init__(self, biblist, keys=None, citation_template=None, sortkey=None):
		self.biblist = biblist
		#:alert: use citekeys property -> self._entries created!
		self.citekeys = keys
		self.citation_template = citation_template
		self.entry_formatter=EntryFormatter(citation_template)
		self.sortkey = sortkey
		if self.sortkey:
			self._entries.sort(key=sortkey)
		self.citeref_processor = None

	def __str__(self):
		if self.citation_template and "citation_sep" in self.citation_template:
			citation_sep = self.citation_template['citation_sep']
		else:
			citation_sep = "\n\n"
		return citation_sep.join( [str(entry)  for entry in self._entries] )

	def set_citeref_processor(self,processor):
		self.citeref_processor = processor
	def format_inline_cite(self, cite_key_list):
		"""Returns a formatted inline citation reference.
		Usually used by a CiteRefProcessor object during processing. 
		Usually styles need to override this method.
		"""
		#substitute formatted citation reference into document text
		self.result.append( self.citation_manager.format_inline_cite(entry_list,cite_key_list) )
		return '**[' + ','.join(cite_key_list) + ']_'


	def get_citekeys(self):
		return self._keys
	def set_citekeys(self,keys):
		"""set self._keys to keys **and** make associated entries
		"""
		self._keys = keys
		if keys:
			self._entries = self.find_entries(keys,discard=True)
		else:
			self._entries = []
	citekeys = property(get_citekeys,set_citekeys,None,"citekeys property")


	def find_entries(self,citekeys=None,discard=True):
		"""return all entries if citekeys==None else matching entries
		"""
		if citekeys is None:
			citekeys = self.citekeys
		result = []
		#TODO: check for reuse of citekeys in different BibFile objects
		for bib in self.biblist:
			result.extend(bib.get_entrylist(citekeys,discard=discard))
		return result
	def get_entries(self,citekeys=None):
		if not citekeys:
			return self._entries[:]
		else:
			return self.find_entries(citekeys)
	#note: citation_rank uses unit-based indexing (so styles don't have to offset it)
	def get_citation_rank(self,entry,keys=None):
		if keys is None:
			keys = self._keys
		if entry.citekey not in keys:
			rank = None
			shared_logger.error("Entry key not in keys; citation_rank set to None.")
		else: # found the key in the cite-key list
			rank = 1 + self._keys.index(entry.citekey)
		return rank

	def sortkey(self,entry):
		"""
		:note:the sort key is a style consideration and so must be provided by the style;
		      therefore, you must usually OVERRIDE this default sort key
		"""
		result = entry.get_names().get_last_names()
		result.append(entry['year'])
		return result
	def sort(self,sortkey=None):
		if sortkey:
			self.sortkey = sortkey  # NB!
		if self.sortkey:
			self._entries.sort(key=sortkey) #2.4 dependency (implements stable Schwartzian transform or better)
			shared_logger.debug("Entries are sorted.")

	#citation_label handling can make be style dependent
	# e.g., for numbered citations, see example_numbered.py
	def get_citation_label(self,entry,citation_template=None):
		return ''

	def make_citations(self, entries=None, citation_template=None):
		"""return formatted citations based on list of entries

		:note: called by ../bib4txt.py in make_text_output
		:note: citation order based on order of entries (so must sort ahead of time)
		:note: related functionality was in the old CitationFormatter's FormatReferences() method
		"""
		shared_logger.debug("make_citations: args are:"+str((entries,citation_template)))
		if entries is None:
			if not self._entries:
				self._entries = self.find_entries(self.citeref_processor.all_citekeys)
			entries = self._entries
			shared_logger.debug("make_citations: entries are:"+str(self._entries))
		if citation_template is None:
			citation_template = self.citation_template
		citation_sep = citation_template['citation_sep']
		#:note: in 2.4 join will accept generators; why is the list necessary?
		result = citation_sep.join( [self.format_citation(entry)  for entry in entries] )
		shared_logger.debug("Exiting make_citations.")
		return result

	def format_citation(self, entry):
		citation_template = self.citation_template
		formatter = self.entry_formatter
		result = formatter.format_entry(entry)
		citation_label = self.get_citation_label(entry,citation_template)
		#result = citation_label + reformat_para( append_sep(names,sep)+details, left=citation_template['indent_left'] )
		result = citation_label + reformat_para( result, left=citation_template['indent_left'] )
		return result






class CiteRefProcessor( simpleparse.dispatchprocessor.DispatchProcessor ):
	"""Formats inline citations and substitutes them into text.
	Stores all cite keys in `all_citekeys` (a list, to record citaiton order).
	Can store `result` as original text with substituted citation references.

	:note: based on the defunct addrefs CitationFormatter class
	"""
	def __init__(self, citation_manager):
		"""
		param `parsed_bibfile`: a dispatch processor holding parsed .bib file
		"""
		#associate with citation manager
		citation_manager.set_citeref_processor(self)
		self.citation_manager = citation_manager
		#self.bib = parsed_bibfile
		# result holds the entire processed file, reformatted for inline citation
		self.result = []
		self.all_citekeys = []  #order matters! unique citekeys added as encountered: see `cite`

	def __repr__(self):
		return ''.join(self.result)

	#set up debug message logging
	def log_msg(self,msg):
		shared_logger.debug(msg)

	#PRODUCTION FUNCTIONS
	# define method for EACH production (see the help for DispatchProcessor)

	def cite(self, (tag,start,stop,subtags), buffer ):
		"""Return everything.

		Alternative default def:
		self.result.append( buffer[start:stop])
		"""
		self.log_msg("The following is parsed as cite:\n" + buffer[start:stop])
		"Process cites and format in text citation according to current style"
		# list because allow for a single citation reference to have keys for multiple citations
		cite_key_list = [s.strip() for s in buffer[start+1:stop-2].split(CITE_SEP)]
		#include current cite keys in set of all cite keys
		#  keep track of order of citation (used by some styles)
		for cite_key in cite_key_list:
			if cite_key not in self.all_citekeys:
				self.all_citekeys.append(cite_key)
		#make (ordered) list of entries for the current cite key(s)
		#:note: need entry to be None if cite_key not found, so discard=False
		entry_list = self.citation_manager.find_entries(cite_key_list,discard=False)
		#substitute formatted citation reference into document text
		self.result.append( self.citation_manager.format_inline_cite(cite_key_list) )
		self.log_msg("The following is parsed as cite:\n" + buffer[start:stop])

	def inline_literal(self, (tag,start,stop,subtags), buffer ):
		"Return everything."
		self.result.append( buffer[start:stop] )
		self.log_msg("The following is parsed as inline_literal:\n" + buffer[start:stop])

	def fn(self, (tag,start,stop,subtags), buffer ):
		"Return everything."
		self.result.append( buffer[start:stop])
		self.log_msg("The following is parsed as fn:\n" + buffer[start:stop])

	def plain(self, (tag,start,stop,subtags), buffer ):
		"Return everything."
		self.result.append( buffer[start:stop])
		self.log_msg("The following is parsed as plain:\n" + buffer[start:stop])
	

class EntryFormatter(object):
	def __init__(self, citation_template):
		self.citation_template = citation_template
		self.names_formatter=NamesFormatter(citation_template)

	def format_entry(self,entry,citation_template=None):
		"""Format an entry (e.g., as a citation, i.e., a single bibliography reference).
		Note that a BibEntry object acts like a dict for Bib fields
		*except* no KeyError (returns None instead).
		`citation_template` holds templates for entry types

		:note: something related to this method was formerly Bibstyle's formatRef method
		:note: called by make_citations (and currently nothing else)
		"""
		shared_logger.debug("Entering format_citation.")
		if citation_template is None:
			citation_template = self.citation_template
		#:note: a BibEntry object will return None if field is missing
		#get the other (not name) fields
		names = self.format_citation_names(entry, citation_template)
		details = self.format_citation_details(entry, citation_template)
		sep = citation_template['names_details_sep']
		result = append_sep(names,sep)+details
		shared_logger.debug("EntryFormatter.format_citation: result = "+result)
		return result
	def format_citation_names(self, entry, citation_template=None):
		if citation_template is None:
			citation_template = self.citation_template
		#get the names from the entry (as a BibName object)
		names = entry.make_names(self)  #use this entry formatter (self) to make the names
		#use own names_formatter (based on citation_template) to format the names
		result = self.names_formatter.format_names(names)
		#shared_logger.debug("name_name_sep: "+str(template['name_name_sep']))
		#shared_logger.debug("format_citation_names: result = "+result)
		return result
	#TODO: this deserves substantial enhancement
	def format_citation_details(self, entry, citation_template=None):
		if citation_template is None:
			citation_template = self.citation_template
		try:
			type_template = citation_template[entry.type]  #:note: recall type was stored as lowercase
		except KeyError:  #no template exists for this type -> use default
			type_template = citation_template['default_type']
			shared_logger.warning("Unknown entry type: "+entry.type+". Using default format.")
		#:note: entry will return None instead of KeyError
		result = type_template%entry
		return result
	def pick_raw_names(self, entry, fields=None):
		""" return BibName-object if possible else string
		(from "raw" names).
		
		:type `field`: str
		:note: 2006-08-02 altered to return BibName instance and not set _names
		:note: self returns None if field missing (-> no KeyError)
		:TODO: return BibName instance for each available name field??
		"""
		names_source = dict(
		article = ['author','organization'],
		book = ['author','editor','organization']
		)
		if fields:
			for field in fields:
				raw_names = entry['field']
				if raw_names:
					break
			if not raw_names:
				shared_logger.warning("EntryFormatter.make_names: empty field -> empty BibName object.")
		#raw_names = self['author'] or self['editor'] #TODO: distinguish author and editor
		elif entry.type in names_source:
			for field in names_source[entry.type]:
				raw_names = entry[field]
				if raw_names:
					break
		else: # default formatting
			for field in ['author','editor','organization']:
				raw_names = entry[field]
				if raw_names:
					break
		if not raw_names:
			shared_logger.warning("No raw names for bib citekey "+entry.citekey)
			raw_names = "Anonymous"  #TODO: shd be a formatting choice (use None?)
			field = None
		#return  bibname.BibName(raw_names,from_field=field)  #names are in a BibName object
		return  raw_names, field
	
@


1.2
log
@Refactoring and changes by Alan Isaac.
@
text
@d3 2
a4 2
Utilities and formatting classes for BibStuff, especially for
bib4txt.py.
d15 1
a15 2
__author__ = "Alan G. Isaac"
__version__ = "$Revision: 1.1 $"
d39 5
a43 7
	"""
        Simple paragraph reformatter.

        Allows specification of left and right margins, and of
        justification style (using constants defined in module).
        :note: Adopted by Schwilk from David Mertz's example in TPiP
        :see: Mertz, David, *Text Processing in Python* (TPiP)
d75 8
a82 3
	def __init__(self, citation_template=None, template_list=None):
		shared_logger.debug("NamesFormatter.__init__ args: "+str((citation_template,template_list)))
		assert(template_list or citation_template)
d92 1
a92 1
			self.initials = False
d96 1
a96 1
		self.formatters = [NameFormatter(template,self.initials) for template in self.template_list]
d98 5
d104 17
a120 1
	def get_formatted(self,names):
d122 4
a125 10
                Returns the names in a formatted string.
                
		`names`: a BibName object
		"""
		shared_logger.debug("NamesFormatter.get_formatted: Type of names data is "+str(type(names)))
		#TODO? use the name_dicts
		names_parts = names.get_names_parts()
		if isinstance( names_parts, (list,tuple) ):
			shared_logger.debug("NamesFormatter.get_names_parts: Assume returned list is a names_parts list:"+str(names_parts))
		num_names = len(names_parts)
d129 8
a136 5
		formatted_name_list = [ self.formatters[0].get_formatted(names_parts[0]) ]
		if num_names > 1 and num_names < self.max_citation_names:
			for name_parts in names_parts[1:]:
				formatted_name_list.append( self.formatters[1].get_formatted(name_parts) )
		shared_logger.debug("NamesFormatter.get_formatted: formatted_name_list: "+str(formatted_name_list))
d140 1
d143 1
d145 5
a149 1
			result = append_sep(result,self.name_name_sep[1]) + formatted_name_list.pop(0)
a153 5
	def make_etal(self,num):
		if num <= self.max_citation_names:
			return ''
		else:
			return self.etal
d157 1
a157 2
	"""
        Create a NameFormatter object based on a template string.
d182 2
d185 1
a185 1
	def __init__(self,template,initials=False):
d187 2
a188 1
		#TODO: parameterize this default:
d190 1
a190 1
		#self.partdict = {}
d194 5
d200 9
a208 2
	def get_formatted(self,name_data):
		shared_logger.debug("NameFormatter.get_formatted:\nType of name_data is: "+str(type(name_data)))
d211 4
a214 1
			result = self.name_parts2formatted(name_data)
d219 1
d222 1
d224 1
a224 2
		"""Returns one fully formatted name, based on a
		name_parts tuple.
d227 2
a228 1
		shared_logger.debug("name_parts2formatted: self.partdict is "+str(self.partdict))
d235 2
a236 2
		for partcode in self.parts_order:
			partsep = self.partdict[partcode]['partsep']
d239 27
a265 1
				result += self.partdict[partcode]['pre'] + part + self.partdict[partcode]['post']
a270 2
	#sets the name formatting template *and* makes the associated
	#partdict for actual formatting
d272 4
d277 1
a277 2
		assert(isinstance(template,str),
                       "Must provide a template to make a NameFormatter object.")
d279 9
d289 1
a289 1
		self.parts_order = ''
d291 1
a291 1
		self.partdict = {}
d295 1
a295 1
					self.parts_order += partid
d302 1
a302 1
					self.partdict[partid] = dict(pre=pre,post=post,partsep=partsep)
d304 3
a306 3
		shared_logger.debug("name formatting template parsed to:\n"+str(self.partdict))
	template = property(get_template,set_template,None,"template property")
	#remember: properties require new style classes to work right
a308 1
#TODO: possibly useful for bibsearch.py
d310 4
a313 1
	def __init__(self, biblist, keys=None, template=None, sortkey=None):
d315 1
a315 1
		#use citekeys property -> self._entries created!
d317 2
a318 1
		self.template = template
d322 2
d325 2
a326 2
		if self.template and "citation_sep" in self.template:
			citation_sep = self.template['citation_sep']
d330 15
d346 2
d349 4
a352 3
		self._entries = self.make_entries(keys)
	def get_citekeys(self):
		return self._keys
d354 3
a356 1
	def make_entries(self,citekeys=None):
d362 1
d364 1
a364 1
			result.extend(bib.get_entrylist(citekeys))
d370 1
a370 1
			return self.make_entries(citekeys)
d375 1
a375 1
		if entry.key not in keys:
d379 1
a379 1
			rank = 1 + self._keys.index(entry.key)
d381 1
a381 2
	#:note: remember, the sort key is a style consideration and so must be provided by the style
	#:note: usually OVERRIDE this default sort key
d383 4
d399 1
a399 1
	def get_citation_label(self,entry,template=None):
d409 1
a409 1
		shared_logger.debug("Entering make_citations.")
d411 2
d414 1
d416 1
a416 1
			citation_template = self.template
d418 2
a419 3
		#:note: in 2.4 join will not accept generators
		result = citation_sep.join( [self.format_citation(entry,template=citation_template)
                                             for entry in entries] )
d423 7
a429 44
	#:note: something related to this was formerly Bibstyle's formatRef method
	#:note: called by make_citations (and currently nothing else)
	def format_citation(self,entry,template=None):
		"""
                Format a citation (i.e., a single bibliography reference).
                
		Note that a BibEntry object acts like a dict for Bib
		fields *except* no KeyError (returns None instead).
		`citation_template` holds templates for entry types
		"""
		shared_logger.debug("Entering format_citation.")
		if template is None:
			template = self.citation_template
		#:note: a BibEntry object will return None if field is missing
		#get the other (not name) fields
		names = self.format_citation_names(entry, template)
		details = self.format_citation_details(entry, template)
		sep = template['names_details_sep']
		citation_label = self.get_citation_label(entry,template)
		result = citation_label + reformat_para( append_sep(names,sep)+details, left=template['indent_left'] )
		shared_logger.debug("Exiting format_citation.")
		return result
	def format_citation_names(self, entry, citation_template=None):
		if citation_template is None:
			citation_template = self.citation_template
		#get the formatted names from the entry (provided there by a BibName object)
		formatter=NamesFormatter(citation_template)
		#entry will as its BibName object to format the names, which gets the formatter to do it
		#so currently: result=formatter.get_formatted(entry.get_names())
		result = entry.format_names(formatter)
		#shared_logger.debug("name_name_sep: "+str(template['name_name_sep']))
		#shared_logger.debug("result: "+result)
		return result
	#TODO: this deserves substantial enhancement
	def format_citation_details(self, entry, citation_template=None):
		if citation_template is None:
			citation_template = self.citation_template
		try:
			type_template = citation_template[entry.type]  #:note: recall type was stored as lowercase
		except KeyError:  #no template exists for this type -> use default
			type_template = citation_template['default_type']
			shared_logger.warning("Unknown entry type: "+entry.type+". Using default format.")
		#:note: entry will return None instead of KeyError
		result = type_template%entry
d435 2
a436 1
#:note: based on the addrefs CitationFormatter class
d439 1
a439 1
	Stores all cite keys in `all_cite_keys`
d441 2
d444 8
a451 2
	def __init__(self, parsed_bibfile_dispatch_processor) :
		self.bib = parsed_bibfile_dispatch_processor
d454 1
a454 1
		self.all_cite_keys = []
a459 3
	def format_inline_cite(self, entry_list, cite_key_list):
		return '**[' + ','.join(cite_key_list) + ']_'

d463 2
a464 1
	#define method for EACH production (see the help for DispatchProcessor)
a467 1
		Usually you need to override this method.
d477 1
a477 1
		#keep track of order of citation (used by some styles)
d479 5
a483 11
			if cite_key not in self.all_cite_keys:
				self.all_cite_keys.append(cite_key)
		#make (ordered) list of entries for the current cite keys
		#entry will be None if cite_key not found
		entry_list = [self.bib.returnByKey(cite_key) for cite_key in cite_key_list]
		"""
		#entries keep track of their citation_rank (i.e., order cited), used by some styles
		for entry in entry_list:
			if entry is not None:
				entry.set_citation_rank(self.all_cite_keys)
		"""
d485 1
a485 1
		self.result.append( self.format_inline_cite(entry_list,cite_key_list) )
d504 10
d515 74
@


1.1
log
@Initial revision
@
text
@d16 1
a16 1
__version__ = "$Revision: 0.4.3$"
d40 7
a46 5
	"""Simple paragraph reformatter.  Allows specification
	of left and right margins, and of justification style
	(using constants defined in module).
	:note: Adopted by Schwilk from David Mertz's example in TPiP
	:see:  Mertz, David,  *Text Processing in Python* (TPiP)
d98 3
a100 1
		"""Returns the names in a formatted string.
d136 2
a137 1
	"""Create a NameFormatter object based on a template string.
d184 2
a185 1
		"""Returns one fully formatted name, based on a name_parts tuple.
d205 2
a206 1
	#sets the name formatting template *and* makes the associated partdict for actual formatting
d209 2
a210 1
		assert(isinstance(template,str),"Must provide a template to make a NameFormatter object.")
d311 2
a312 1
		result = citation_sep.join( [self.format_citation(entry,template=citation_template)  for entry in entries] )
d319 5
a323 3
		"""Format a citation (i.e., a single bibliography reference).
		Note that a BibEntry object acts like a dict for Bib fields
		*except* no KeyError (returns None instead).
a360 2


@