import nose
from nose.tools import eq_, raises
from unittest import TestCase

from org import NestingNotValidError
from org import Org, org_to_html

class TestOrg(TestCase):
    def test_org(self):
        text = ''''''
        o = Org(text)
        eq_(str(o), 'Org()')

    def test_paragraph(self):
        text = '''line1
line2'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text Text))')

    def test_new_paragraph(self):
        text = '''para1-1
para1-2

para2-1
para2-2'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text Text) Paragraph(Text Text))')

    def test_heading(self):
        text = '''* Heading1
** Heading2
*** Heading3
**** Heading4
***** Heading5-1
****** Heading6
***** Heading5-2'''
        o = Org(text)
        eq_(str(o), 'Org(Heading1(Heading2(Heading3(Heading4(Heading5(Heading6()) Heading5())))))')

    def test_slided_heading(self):
        text = '''* Heading2
** Heading3'''
        o = Org(text, default_heading=2)
        eq_(str(o), 'Org(Heading2(Heading3()))')

    def test_blockquote(self):
        text = '''#BEGIN_QUOTE: http://exapmle.com
quoted line1
quoted line2
#END_QUOTE'''
        o = Org(text)
        eq_(str(o), 'Org(Blockquote(Text Text))')

    @raises(NestingNotValidError)
    def test_openless_blockquote(self):
        text = '''#END_QUOTE'''
        Org(text)

    @raises(NestingNotValidError)
    def test_endless_blockquote(self):
        text = '''#BEGIN_QUOTE'''
        Org(text)

    def test_orderedlist(self):
        text = '''1. listitem1
2. listitem2
3) listitem3
4) listitem4'''
        o = Org(text)
        eq_(str(o), 'Org(OrderedList(ListItem ListItem ListItem ListItem))')

    def test_nested_orderedlist(self):
        text = '''1. listitem1
2. listitem2
  1. shallowitem1
  2. shallowitem2
     1. deepitem1
     2. deepitem2
  3. shallowitem3
3. listitem3'''
        o = Org(text)
        eq_(str(o), 'Org(OrderedList(ListItem ListItem OrderedList(ListItem ListItem OrderedList(ListItem ListItem) ListItem) ListItem))')

    def test_unorderedlist(self):
        text = '''- listitem1
- listitem2
+ listitem3
+ listitem4'''
        o = Org(text)
        eq_(str(o), 'Org(UnOrderedList(ListItem ListItem ListItem ListItem))')

    def text_nested_unorderedlist(self):
        text = '''- listitem1
- listitem2
  + shallowitem1
  + shallowitem2
     - deepitem1
     - deepitem2
  + shallowitem3
- listitem3'''
        o = Org(text)
        eq_(str(o), 'Org(UnOrderedList(ListItem ListItem UnOrderedList(ListItem ListItem UnOrderedList(ListItem ListItem) ListItem) ListItem))')

    def test_definitionlist(self):
        text = '''- listtitle1:: listdescription1
- listtitle2::listdescription2
- listtitle3 :: listdescription3
- listtitle4::listdescription4
+ listtitle5:: listdescription5
+ listtitle6::listdescription6
+ listtitle7 :: listdescription7
+ listtitle8::listdescription8'''
        o = Org(text)
        eq_(str(o), 'Org(DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)))')

    def text_nested_definitionlist(self):
        text = '''- listitem1:: desc1
- listitem2 ::desc2
  + shallowitem1 :: shallowdesc1
  + shallowitem2::shallowdesc2
     - deepitem1::deepdesc1
     - deepitem2 :: deepdesc2
  + shallowitem3:: shallowdesc3
- listitem3 :: desc3'''
        o = Org(text)
        eq_(str(o), 'Org(DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)))')

    def test_table(self):
        text = '''| col1-1 | col2-1|col3-1 |col4-1|
| col1-2|col2-2 |col3-2| col4-2 |
|col1-3 |col2-3| col3-3 | col4-3|
|col1-4| col2-4 | col3-4|col4-4 |'''
        o = Org(text)
        eq_(str(o), 'Org(Table(TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text))))')

    def test_link(self):
        text = '''[[http://example.com]]'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'Link')
        text = '''[[http://example.com][example]]'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'Link')
        text = '''hoge[[http://example.com]]fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeLinkfuga')

    def test_image(self):
        text = '''[[picture.png]]'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'Image')

    def test_link_and_image(self):
        text = '''hoge[[http://example.com]]fuga[[picture]]piyo'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeLinkfugaImagepiyo')
        text = '''hoge[[picture]]fuga[[http://example.com]]piyo'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeImagefugaLinkpiyo')

    def test_bold(self):
        text = '''hoge*bold*fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeBoldTextfuga')

    def test_italic(self):
        text = '''hoge/italic/fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeItalicTextfuga')

    def test_underlined(self):
        text = '''hoge_underlined_fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeUnderlinedTextfuga')

    def test_linethrough(self):
        text = '''hoge+linethrough+fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeLinethroughTextfuga')

    def test_inlinecode(self):
        text = '''hoge=code=fuga'''
        o = Org(text)
        eq_(str(o), 'Org(Paragraph(Text))')
        eq_(o.children[0].children[0].get_text(), 'hogeInlineCodeTextfuga')

    def test_mix(self):
        text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#BEGIN_QUOTE
quoted
- hoge
- fuga
#END_QUOTE'''
        o = Org(text)
        eq_(str(o), 'Org(Heading1(Paragraph(Text) Heading2(Paragraph(Text Text)) Heading2(Table(TableRow(TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text))) Heading3(Blockquote(Text UnOrderedList(ListItem ListItem))))))')


class TestOrgToHTML(TestCase):
    def test_html(self):
        text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#BEGIN_QUOTE
quoted
#END_QUOTE'''
        o = Org(text)
        eq_(o.html(), '<h1>header1</h1><p>paraparapara</p><h2>header2-1</h2><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h2>header2-2</h2><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h3>header3</h3><blockquote>quoted</blockquote>')

    def test_slide_heading_html(self):
        text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#BEGIN_QUOTE
quoted
#END_QUOTE'''
        o = Org(text, default_heading=2)
        eq_(o.html(), '<h2>header1</h2><p>paraparapara</p><h3>header2-1</h3><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h3>header2-2</h3><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h4>header3</h4><blockquote>quoted</blockquote>')


class TestOrgToHTMLFunction(TestCase):
    def test_html(self):
        text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#BEGIN_QUOTE
quoted
#END_QUOTE'''
        eq_(org_to_html(text), '<h1>header1</h1><p>paraparapara</p><h2>header2-1</h2><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h2>header2-2</h2><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h3>header3</h3><blockquote>quoted</blockquote>')

    def test_slide_heading_html(self):
        text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#BEGIN_QUOTE
quoted
#END_QUOTE'''
        eq_(org_to_html(text, default_heading=2), '<h2>header1</h2><p>paraparapara</p><h3>header2-1</h3><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h3>header2-2</h3><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h4>header3</h4><blockquote>quoted</blockquote>')



if __name__ == '__main__':
    unittest.main()
