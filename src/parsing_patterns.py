#!/usr/bin/env python
# -*- coding: utf-8 -*-


# standard libraries
import re

# third party libraries (allow variable length lookarounds)
import regex as re_


# identification of filing type and name in index file
PAT_10K = re.compile(r'(?!.*?/A)\|10-?K(SB|SB40|405)?\|', re.I)
PAT_10KA = re.compile(r'(\|10-?K(SB|SB40|405)?(/A))\|', re.I)
PAT_10Q = re.compile(r'(?!.*?/A)\|10-?Q(SB|SB40|405)?\|', re.I)
PAT_10QA = re.compile(r'(\|10-?Q(SB|SB40|405)?(/A))\|', re.I)
PAT_8K = re.compile(r'\|8.?K\|', re.I)
PAT_FNAME = re.compile(r'\|(edgar/data.*\/([\d-]+\.txt))', re.I)


# identification of filing metadata
PAT_HEADER_END = re.compile(r'</(SEC|IMS)-HEADER>', re.I)
PAT_META = {
    'fname': re.compile(r'<(?:SEC|IMS)-DOCUMENT>.*?(\d{10}-\d{2}-\d{6}\.txt)', re.I),
    'cik': re.compile(r'^\s*CENTRAL\s*INDEX\s*KEY:\s*(\d{10})', re.I),
    'comp_name': re.compile(r'^\s*COMPANY\s*CONFORMED\s*NAME:\s*(.+)', re.I),
    'sic': re.compile(r'^\s*STANDARD\s*INDUSTRIAL\s*CLASSIFICATION:.*?(\d{4})', re.I),
    'form_type': re.compile(r'^\s*CONFORMED\s*SUBMISSION\s*TYPE:\s(.+)', re.I),
    'street': re.compile(r'^\s*STREET\s*1?:\s(.+)', re.I),
    'city': re.compile(r'^\s*CITY:\s(.+)', re.I),
    'state': re.compile(r'^\s*STATE:\s(.+)', re.I),
    'zip': re.compile(r'^\s*ZIP:\s(.+)', re.I),
    'phone': re.compile(r'^\s*(BUSINESS)?\s*PHONE(\sNUMBER)?:\s(.+)', re.I),
    'date_report': re.compile(r'^\s*CONFORMED\s*PERIOD\s*OF\s*REPORT:\s*(\d{8})', re.I),
    'date_filing': re.compile(r'^\s*FILED\s*AS\s*OF\s*DATE:\s*(\d{8})', re.I),
    'hlink': re.compile(r'(.*?(([0]*(\d+))\-(\d{2})\-(\d{6})))', re.I)
}


# identification of markup tags
PAT_MU1 = {
    'ascii': re.compile(r'(<DOCUMENT>)?(\n)?(<TYPE>)(GRAPHIC|ZIP|EXCEL|JSON|PDF|XML|EX)(.|\n)*?(</DOCUMENT>)', re.I),
    'ascii_alt': re.compile(r'\n(<GRAPHIC>(.|\n)*?</GRAPHIC>)|(<ZIP>(.|\n)*?</ZIP>)|(<EXCEL>(.|\n)*?</EXCEL>)|(<JSON>(.|\n)*?</JSON>)|(<PDF>(.|\n)*?</PDF>)|(<XML>(.|\n)*?</XML>)|(<EX.*?>(.|\n)*?</EX.*?>)', re.I),
    'header_footer': re.compile(r'(^(.|\n)*?(</SEC-HEADER>)|(-----END PRIVACY-ENHANCED MESSAGE-----))', re.I),
    'html_tags': re.compile(r'((<div|<font|<tr|<td|<p)(.|\n)*?(>)|(</font>|</div>|</tr>|</td>|</p>))', re.I),
}
PAT_MU2 = re.compile(r'<.*?>|<.*?\n.*?>|</.*?>', re.I)
PAT_TAB1 = re.compile(r'((<TABLE)(.|\n)*?(</TABLE>))', re.I)
PAT_TAB2 = re.compile(r'(\[TABLE\]|\[/TABLE\])', re.I)
PAT_TOC1 = re.compile(r'\nTable\s*?of\s*?Contents\n', re.I)
PAT_TOC2 = re.compile(r'\nReturn\s*?to\s*?Table\s*?of\s*?Contents\n', re.I)


# identification of MD&A
PAT_10K_MDA1 = re_.compile(
    # search for 'Part 2' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(\s“|\w“|\s"|\w"|\s>|"Part\s*?\w*?\s*?-?|PART\s*?\w*?\s*?-?)\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 7.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\.?\s*?((NO\.|NUMBER)\s*?)?7\s*?(\.|:|-|–|—|--|\||\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?'
    # search for 'Management's Discussion' or 'Management's Narrative' string
    r'M\n*?A\n*?N\n*?A\n*?G\n*?E\n*?M\n*?E\n*?N\n*?T\n*?.?\n*?S?.?\s*?((D\n*?I\n*?S\n*?C\n*?U\n*?S\n*?S\n*?I\n*?O\n*?N)|(N\n*?A\n*?R\n*?R\n*?A\n*?T\n*?I\n*?V\n*?E))'
    # search for an arbitrarily long text block (i.e. the section content)
    r'(.|\n)*?'
    # search for 'Part 2' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(“|"|,) ?\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 7A.' or 'TEM 8.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\.?\s*?((NO\.|NUMBER)\s*?)?(7A|7\.A|8)\s*?(\.|:|-|–|—|--|\||\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?',
    re_.I
)
PAT_10K_MDA2 = re_.compile(
    # search for 'Part 2' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n\s*?I)'
    r'(?<!(\s“|\w“|\s"|\w"|\s>|"PART\s*?\w*?\s*?-?|PART\s*?\w*?\s*?-)\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 6.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\.?\s*?((NO\.|NUMBER)\s*?)?6\s*?(\.|:|-|–|—|--|\||\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?'
    # search for various string variants that identify the MD&A in older filings
    r'((M\n*?A\n*?N\n*?A\n*?G\n*?E\n*?M\n*?E\n*?N\n*?T\n*?.?\n*?S?.?\s*?((D\n*?I\n*?S\n*?C\n*?U\n*?S\n*?S\n*?I\n*?O\n*?N)|(N\n*?A\n*?R\n*?R\n*?A\n*?T\n*?I\n*?V\n*?E)))|(M\n*?A\n*?N\n*?A\n*?G\n*?E\n*?M\n*?E\n*?N\n*?T\n*?.?\n*?S?.?\s*?P\n*?L\n*?A\n*?N)|(PLAN\s*?OF\s*?OPERATION)|(SELECTED\s*?FINANCIAL\s*?DATA;))'
    # search for an arbitrarily long text block (i.e. the section content)
    r'(.|\n)*?'
    # search for 'Part 2' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(“|"|,) ?\n(PART\s*?(2|II)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 7.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\.?\s*?((NO\.|NUMBER)\s*?)?7\s*?(\.|:|-|–|—|--|\||\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?',
    re_.I
)
PAT_10Q_MDA = re_.compile(
    # search for 'Part 1' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART *?(1|I) *?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n\n(PART *?(1|I) *?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(\s“|\w“|\s"|\w"|\s>)\n(PART *?(1|I) *?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 2.' or 'TEM 6.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\.?\s*?((NO\.|NUMBER)\s*?)?(2|II|6)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?'
    # search for various string variants that identify the MD&A in older filings
    r'((M\n*?A\n*?N\n*?A\n*?G\n*?E\n*?M\n*?E\n*?N\n*?T\n*?.?\n*?S?\s*?((D\n*?I\n*?S\n*?C\n*?U\n*?S\n*?S\n*?I\n*?O\n*?N)|(N\n*?A\n*?R\n*?R\n*?A\n*?T\n*?I\n*?V\n*?E)))|(M\n*?A\n*?N\n*?A\n*?G\n*?E\n*?M\n*?E\n*?N\n*?T\n*?.?\n*?S?\s*?P\n*?L\n*?A\n*?N)|(PLAN\s*?OF\s*?OPERATION))'
    # search for an arbitrarily long text block (i.e. the section content)
    r'(.|\n)*?'
    # search for 'Part 1' or 'Part 2' string that can optionally precede 'I' and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(I|1|II|2)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under|of) ?\n(PART\s*?(I|1|II|2)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(“|"|,) ?\n(PART\s*?(I|1|II|2)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for any other item that may entail the MD&A while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M(\n*?s)?\.?\s*?((NO\.|NUMBER)\s*?)?(?!(1A|i[a-z]))(1|I|3|4|5|6)\s*?(\.|,|:|-|–|—|--|\||\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?',
    re_.I
)


# identification of item1
PAT_ITEM1 = re_.compile(
    # search for 'Part 1' string that can optionally precede the 'Item' string and is itself preceded by a line-break (necessary condition)
    r'\n(PART\s*?(1|I)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?'
    # search for 'I' preceded by a line-break and optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under) ?\n(PART\s*?(1|I)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    r'(?<!(\s“|\w“|\s"|\w"|\s>|"Part\s*?\w*?\s*?-?|“Part\s*?\w*?\s*?-?)\n(PART\s*?(1|I)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?)?\s*?I)'
    # search for 'TEM 1.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\n*?s?\.?\s*?((NO\.|NUMBER)\s*?)?(1|I|l)\s*?(\.|:|-|–|—|--|\||\.\s-|\.\s–|.\s—|\.\s--)?\s*?(a\s*?n\s*?d\s*?2\s*?)?(\.|:|-|–|—|--|\.\s-|\.\s–|.\s—|\.\s--)?\s*?'
    # search for 'Our Business', 'Business' or 'Description' string
    r'(((O\n*?U\n*?R\s*?)?B\n*?U\n*?S\n*?I\n*?N\n*?E\n*?S\n*?S)|(D\n*?E\n*?S\n*?C\n*?R\n*?I\n*?P\n*?T\n*?I\n*?O\n*?N))'
    # search for an arbitrarily long text block (i.e. the section content)
    r'(.|\n)*?'
    # search for 'Part 1' string that can optionally precede 'I' and is itself preceded by a line-break (necessary condition)
    r'\n(Part\s*?(I|1)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?)?'
    # search for 'I' preceded by optional white space characters
    r'\s*?I'
    # negative lookbehind to ensure that 'I' is not preceded by certain referrals
    r'(?<!(in|to|see|and|under) ?\n(Part\s*?(I|1)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?)?\s*?I)'
    r'(?<!(“|"|,) ?\n(Part\s*?(I|1)\s*?(\.|,|:|-|–|—|--|\.\s*?-|\.\s*?–|\.\s*?—|\.\s*?--)?\s*?)?\s*?I)'
    # search for 'TEM 1A.', 'TEM 2.' or 'TEM 3.' string while accounting for numerous spelling variations
    r'\n*?T\n*?E\n*?M\n*?s?\.?\s*?((NO\.|NUMBER)\s*?)?(1\s*?A|1\.\s*?A|I\s*?A|I\.\s*?A|2|3)\s*?(\.|:|-|–|—|--|\||\.\s-|\.\s–|.\s—|\.\s--)?',
    re_.I
)
