head	1.2;
access;
symbols;
locks; strict;
comment	@# @;


1.2
date	2006.08.31.21.43.28;	author schwilk;	state Exp;
branches;
next	1.1;

1.1
date	2006.08.03.19.56.48;	author schwilk;	state Exp;
branches;
next	;


desc
@@


1.2
log
@Alan's changes.
@
text
@#File: default.py
"""
Provides a default style for bib4txt.py
Produces a list of citations that to be included in a reStructuredText document.
(In very simple documents, can also provide citation reference formatting
by substituting in the document text for the citation references.)

A style includes:

- citation template 
- CitationManager class
- sortkey for make_text_output
  (often based on a field list)

:note: you will often want to override these
:note: shared.py holds defintions common to most styles
:note: see the examples (e.g., example_numbered.py) of different styles

:author: Alan G Isaac
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006 by Alan G Isaac
:license: MIT (see `license.txt`_)
:date: 2006-08-01

.. _license.txt: ./license.txt
"""
__docformat__ = "restructuredtext en"
__author__  =   "Alan G. Isaac"
__version__ = "$Revision 0.5$"
__needs__ = '2.4'

###################  IMPORTS  ##########################
# from standard library
import logging
style_logger = logging.getLogger('bibstuff_logger')
#shared_logger = logging.getLogger('bibstuff_logger')

# imports from bibstuff
#TODO: change to relative imports (requires Python 2.5)
# :IMPORTANT: every style must import shared!
import shared
# most styles with start with the default templates:
import default_templates
########################################################



	

##########################################################################
###################  CITEREF FORMATTING  #################################
##########################################################################
CITEREF_TEMPLATE = default_templates.DEFAULT_CITEREF_TEMPLATE.copy()


##########################################################################
##################  CITATION FORMATTING  #################################
##########################################################################
"""
Every style must have a CITATION_TEMPLATE, a CitationManager, and a ref_list_sort_key.
Crucial formatting decisions are made int the CITATION_TEMPLATE.
The CITATION_TEMPLATE provides default reference formatting (may also be used by BibStyle) 

:TODO:

	- provide graceful handling of missing fields
	- allow different formatting of first and other names
	- allow different initial line and subsequent line indenting
"""

#here we simply use the default citation template in default_templates.py
CITATION_TEMPLATE = default_templates.DEFAULT_CITATION_TEMPLATE.copy()


class CitationManager(shared.CitationManager):

	################### CITEREF FORMATTING #########################
	#we set the 'format_inline_cite' method equal to the below 'format_inline_cite' function
	def format_inline_cite(self, cite_key_list):
		"""
		Usually you will need to write a 'format_inline_cite' function
		that the CiteRefProcessor will use to substitute inline for citation references.
		"""
		#:note: need entry to be None if cite_key not found, so discard=False
		entry_list = self.find_entries(cite_key_list,discard=False)
		return format_inline_cite(entry_list, self)

	################### CITATION FORMATTING ########################
	def get_citation_label(self,entry,citation_template=None):
		return '.. ['+entry.citekey+']\n'  #:TODO: ? allow use of key in place of citekey ?

	#sort_key for sorting list of references
	# (choice of field_list is a formatting decision)
	def sortkey(self,bibentry):
		return make_sort_key(bibentry,['Author','Year'])

def format_inline_cite(entry_list, citation_manager):
	"""Format in-text citations, allowing for multiple citations.
	`entry_list` is a list of entries

	:note: need the entry formatter bc its determines the field of the names for the cite
	:note: much of the following functionality was in Bibstyle's formatCitation() method
	:TODO: rewrite
	:TODO: ? entries shd be more featureful ? (conflicts with core goal of BibEntry class)
	"""
	style_logger.debug("Entering format_inline_cite.")
	name_date_sep = ' '
	formatted_list = []
	for entry in entry_list:
		if not entry:
			formatted_list.append('?')
		else:
			year = entry['year']
			entry_formatter = citation_manager.entry_formatter
			last_names = entry.get_names(entry_formatter).get_last_names() #:note: ignores "von" part
			if len(last_names) < 3:
				last_names = ' and '.join(last_names)
			else:
				last_names = last_names[0] + ' et al.'
			formatted_list.append( ('%s' + name_date_sep +  '%s')%(last_names, year) )
			#to cite by number can use this instead:
			#formatted_list.append('%d'%entry.citation_rank)
	style_logger.debug("Exiting format_inline_cite.")
	return '(' + CITEREF_TEMPLATE['citeref_sep'].join(formatted_list)+')'

#KEEP! currently used by bibstyle!
#TODO: ? enhance and put in 'shared' ??
def make_sort_key(bibentry, field_list):
	"""create a string for sorting.
	Function returns tuple: (sort_string, bibentry key)

	:note: this is essentially what was Bibstyle's makeSortKey method
	"""
	style_logger.debug("Entering make_sort_key.")
	result = []
	for field in field_list:
		# some special cases
		if field.lower() in [ 'author','editor','names']:
			result.append(' '.join(bibentry.get_names().get_last_names()).lower())
		elif field.lower == "year":
			result.append(int(year))
		else :
			w = bibentry[field]
			if w :
				result.append(w)
	style_logger.debug("Exiting make_sort_key.")
	return result


@


1.1
log
@Initial revision
@
text
@d3 4
a6 5
A default style for bib4txt.py
Produces a list of citations that to be included in
a reStructuredText document.  (In very simple
documents, can also substitute in the text
for the citation references.)
d10 2
a11 2
- citation template
- citeref template
a13 1
- name formatting template (e.g., ``'v |l,| j,| f{. }.'``)
d30 1
a30 1
__needs__ = '2.3'
d48 8
d57 1
a57 1
################### CITEREF FORMATTING ###################################
d60 9
a68 3
Every style must create a CiteRefFormatter.
Usually you will first need to write a 'format_inline_cite' function
that the CiteRefFormatter will use to substitute inline for citation references.
a69 3
# define separator for multiple keys in one inline citation reference
#here we simply use the default citeref template in default_templates.py
CITEREF_TEMPLATE = default_templates.DEFAULT_CITEREF_TEMPLATE.copy()
d71 28
a98 6
#:note: most of the following functionality was in Bibstyle's formatCitation() method
#TODO: rewrite
# lots of evidence that entries shd be more featureful
def format_inline_cite(entry_list,cite_key_list) :
	"""
        Format in-text citations, allowing for multiple citations.
d100 5
d114 2
a115 1
			last_names = entry.get_names().get_last_names() #TODO: misses "von" part
a125 49



class CiteRefFormatter( shared.CiteRefProcessor ):
	"""
	Each style must inlcude a CiteRefFormatter class,
	which must define methods for each production
	(see the help for simpleparse.dispatchprocessor).
	Often these methods are adequately defined by the CiteRefProcessor superclass,
	and you only need to override 'format_inline_cite' method.
	"""
	
	#next we set the 'format_inline_cite' method equal to the above 'format_inline_cite' function
	def format_inline_cite(self, entry_list, cite_key_list):
		return format_inline_cite(entry_list, cite_key_list)



##########################################################################
################### CITATION FORMATTING ##################################
##########################################################################
"""
Every style must have a CITATION_TEMPLATE, a CitationManager, and a
ref_list_sort_key.  Crucial formatting decisions are made int the
CITATION_TEMPLATE.  The CITATION_TEMPLATE provides default reference
formatting (may also be used by BibStyle)

TODO:
- provide graceful handling of missing fields
- allow different formatting of first and other names
- allow different initial line and subsequent line indenting

"""

#here we simply use the default citation template in default_templates.py
CITATION_TEMPLATE = default_templates.DEFAULT_CITATION_TEMPLATE.copy()


class CitationManager(shared.CitationManager):
	def get_citation_label(self,entry,template=None):
		return '.. ['+entry.key+']\n'

	#sort_key for sorting list of references
	# (choice of field_list is a formatting decision)
	def sortkey(self,bibentry):
		return make_sort_key(bibentry,['Author','Year'])

#:note: this is essentially what was Bibstyle's makeSortKey method
# currently retained for the default style
d127 1
a127 1
#TODO: probably shd enhance and put in 'shared'
d130 4
a133 1
	Function returns tuple: (sort_string, bibentry key)"""
a148 1
	
@