import re


class BaseError(Exception):
    pass


class NestingNotValidError(BaseError):
    pass


class Node(object):
    '''Base class of all node'''
    def __init__(self, parent=None, br=''):
        self.type_ = self.__class__.__name__
        self.children = []
        self.parent = parent
        self.br = br

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.type_ + '(' + ' '.join(str_children) + ')'

    def append(self, child):
        if isinstance(child, str):
            child = Text(child)
        self.children.append(child)
        child.parent = self

    def html(self):
        '''Get HTML'''
        inner = ''.join([child.html() for child in self.children])
        return self.br.join([self._get_open(), inner,  self._get_close()])

    def _get_open(self):
        '''returns HTML open tag str'''
        raise NotImplementedError

    def _get_close(self):
        '''returns HTML close tag str'''
        raise NotImplementedError


class TerminalNode(object):
    '''Base class of all terminal node'''
    regexps = {
        'link': re.compile(r'\[\[(?P<url>https?://.+?)\](?:\[(?P<subject>.+?)\])?\]'),
        'image': re.compile(r'\[\[(?P<image>.+?)\](?:\[(?P<alt>.+?)\])?\]'),
        'bold': re.compile(r'\*(?P<text>.+?)\*'),
        'italic': re.compile(r'/(?P<text>.+?)/'),
        'underlined': re.compile(r'_(?P<text>.+?)_'),
        'linethrough': re.compile(r'\+(?P<text>.+?)\+'),
        'code': re.compile(r'=(?P<text>.+?)='),
        'monospace': re.compile(r'~(?P<text>.+?)~')
    }

    def __init__(self, value, parent=None):
        self.type_ = self.__class__.__name__
        self.values = self._parse_value(value)
        self.parent = parent

    def _parse_value(self, value):
        if value is None:
            return ''
        if self.regexps['link'].search(value):
            before, url, subject, after = self.regexps['link'].split(value, maxsplit=1)
            parsed = Link(url, subject)
        elif self.regexps['image'].search(value):
            before, src, alt, after = self.regexps['image'].split(value, maxsplit=1)
            parsed = Image(src, alt)
        elif self.regexps['bold'].search(value):
            before, text, after = self.regexps['bold'].split(value, maxsplit=1)
            parsed = BoldText(text)
        elif self.regexps['italic'].search(value):
            before, text, after = self.regexps['italic'].split(value, maxsplit=1)
            parsed = ItalicText(text)
        elif self.regexps['underlined'].search(value):
            before, text, after = self.regexps['underlined'].split(value, maxsplit=1)
            parsed = UnderlinedText(text)
        elif self.regexps['linethrough'].search(value):
            before, text, after = self.regexps['linethrough'].split(value, maxsplit=1)
            parsed = LinethroughText(text)
        elif self.regexps['code'].search(value):
            before, text, after = self.regexps['code'].split(value, maxsplit=1)
            parsed = InlineCodeText(text)
        elif self.regexps['monospace'].search(value):
            before, text, after = self.regexps['monospace'].split(value, maxsplit=1)
            parsed = MonospaceText(text)
        else:
            before = after = None
            parsed = value
        return (self._parse_value(before) or []) + [parsed] + (self._parse_value(after) or [])

    def __str__(self):
        return self.type_

    def html(self, br=''):
        content = ''
        for value in self.values:
            if isinstance(value, str):
                content += value.strip()
            else:
                content += value.html()
        return self._get_open() + content + self._get_close() + br

    def _get_open(self):
        '''returns HTML open tag str'''
        raise NotImplementedError

    def _get_close(self):
        '''returns HTML close tag str'''
        raise NotImplementedError


class Paragraph(Node):
    '''Paragraph Class'''
    def _get_open(self):
        return '<p>'

    def _get_close(self):
        return '</p>'


class Text(TerminalNode):
    '''Text Class'''
    def get_text(self):
        return ''.join([str(value) for value in self.values])

    def _get_open(self):
        return ''

    def _get_close(self):
        return ''


class BoldText(Text):
    '''Bold Text Class'''
    def _get_open(self):
        return '<span style="font-weight: bold;">'

    def _get_close(self):
        return '</span>'


class ItalicText(Text):
    '''Italic Text Class'''
    def _get_open(self):
        return '<span style="text-style: italic;">'

    def _get_close(self):
        return '</span>'


class UnderlinedText(Text):
    '''Underlined Text Class'''
    def _get_open(self):
        return '<span style="text-decoration: underlined;">'

    def _get_close(self):
        return '</span>'


class LinethroughText(Text):
    '''Linethrough Text Class'''
    def _get_open(self):
        return '<span style="text-decoration: line-through;">'

    def _get_close(self):
        return '</span>'


class InlineCodeText(Text):
    '''Inline Code Text Class'''
    def _get_open(self):
        return '<code>'

    def _get_close(self):
        return '</code>'


class MonospaceText(Text):
    '''Monospace Text Class'''
    def _get_open(self):
        return '<span style="font-family: monospace;">'

    def _get_close(self):
        return '</span>'


class Blockquote(Node):
    '''Blockquote Class'''
    def __init__(self, cite=None):
        self.cite = cite
        super().__init__()

    def _get_open(self):
        if self.cite:
            return '<blockquote cite="{}">'.format(self.cite)
        else:
            return '<blockquote>'

    def _get_close(self):
        return '</blockquote>'


class Heading(Node):
    '''Heading Class'''
    def __init__(self, depth, title):
        self.depth = depth
        self.title = title
        super().__init__(br='')
        self.type_ = 'Heading{}'.format(self.depth)

    def html(self):
        heading = self._get_open() + self.title + self._get_close()
        content = ''.join([child.html() for child in self.children])
        return heading + content

    def _get_open(self):
        return '<h{}>'.format(self.depth)

    def _get_close(self):
        return '</h{}>'.format(self.depth)


class List(Node):
    '''List Class'''
    def __init__(self, depth, ordered, definition, start=1):
        self.depth = depth
        self.ordered = ordered
        self.definition = definition
        if self.ordered:
            self.start = start
        super().__init__()


class ListItem(TerminalNode):
    '''List Item Class'''
    def _get_open(self):
        return '<li>'

    def _get_close(self):
        return '</li>'


class OrderedList(List):
    '''Shortcut Class of Ordered List'''
    def __init__(self, depth, start=1):
        super().__init__(depth, True, False, start)

    def _get_open(self):
        return '<ol>'

    def _get_close(self):
        return '</ol>'


class UnOrderedList(List):
    '''Shortcut Class of UnOrdered List'''
    def __init__(self, depth):
        super().__init__(depth, False, False)

    def _get_open(self):
        return '<ul>'

    def _get_close(self):
        return '</ul>'


class DefinitionList(List):
    '''Shortcut Class of Definition List'''
    def __init__(self, depth):
        super().__init__(depth, False, True)

    def _get_open(self):
        return '<dl>'

    def _get_close(self):
        return '</dl>'


class DefinitionListItem(Node):
    '''Definition List Item Class'''
    def __init__(self, title, description):
        super().__init__()
        self.children.append(DefinitionListItemTitle(title))
        self.children.append(DefinitionListItemDescription(description))

    def _get_open(self):
        return ''

    def _get_close(self):
        return ''


class DefinitionListItemTitle(TerminalNode):
    def _get_open(self):
        return '<dt>'

    def _get_close(self):
        return '</dt>'


class DefinitionListItemDescription(TerminalNode):
    def _get_open(self):
        return '<dd>'

    def _get_close(self):
        return '</dd>'


class Table(Node):
    '''Table Class'''
    def _get_open(self):
        return '<table>'

    def _get_close(self):
        return '</table>'


class TableRow(Node):
    '''Table Row Class'''
    def _get_open(self):
        return '<tr>'

    def _get_close(self):
        return '</tr>'


class TableCell(Node):
    '''Table Cell Class'''
    def _get_open(self):
        return '<td>'

    def _get_close(self):
        return '</td>'


class Link(TerminalNode):
    '''Link Class'''
    def __init__(self, href, title):
        self.href = href
        if title is None:
            title = href
        super().__init__(title)

    def _get_open(self):
        return '<a href="{}">'.format(self.href)

    def _get_close(self):
        return '</a>'


class Image(TerminalNode):
    '''Image Class'''
    def __init__(self, src, alt=""):
        self.src = src
        super().__init__(alt)

    def html(self):
        if self.values:
            return '<img src="{}" alt="{}">'.format(self.src, self.values[0])
        else:
            return '<img src="{}">'.format(self.src)


class Org(object):
    '''The org-mode object'''
    regexps = {
        'whiteline': re.compile(r'\s*$'),
        'heading': re.compile(r'(?P<level>\*+)\s+(?P<title>.+)$'),
        'blockquote_begin': re.compile(r'#BEGIN_QUOTE(?P<c>:)?(?(c)\s+(?P<cite>.+)|)$'),
        'blockquote_end': re.compile(r'#END_QUOTE$'),
        'orderedlist': re.compile(r'(?P<depth>\s*)\d+(\.|\))\s+(?P<item>.+)$'),
        'unorderedlist': re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+)$'),
        'definitionlist': re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+?)\s*::\s*(?P<description>.+)$'),
        'tablerow': re.compile(r'\s*\|(?P<cells>(.+\|)+)s*$'),
    }

    def __init__(self, text):
        self.text = text
        self.children = []
        self.parent = self
        self.current = self
        self.bquote_flg = False
        self._parse(self.text)

    def __str__(self):
        return 'Org(' + ' '.join([str(child) for child in self.children]) + ')'

    def _parse(self, text):
        text = text.splitlines()
        for line in text:
            if self.regexps['heading'].match(line):
                m = self.regexps['heading'].match(line)
                while not (isinstance(self.current, Heading) or isinstance(self.current, Org)):
                    self.current = self.current.parent
                self._add_heading_node(Heading(
                    depth=len(m.group('level')),
                    title=m.group('title')))
            elif self.regexps['blockquote_begin'].match(line):
                self.bquote_flg = True
                m = self.regexps['blockquote_begin'].match(line)
                node = Blockquote(cite=m.group('cite'))
                self.current.append(node)
                self.current = node
            elif self.regexps['blockquote_end'].match(line):
                if not self.bquote_flg:
                    raise NestingNotValidError
                self.bquote_flg = False
                while not isinstance(self.current, Blockquote):
                    if isinstance(self.current, Org):
                        raise NestingNotValidError
                    self.current = self.current.parent
                self.current = self.current.parent
            elif self.regexps['orderedlist'].match(line):
                m = self.regexps['orderedlist'].match(line)
                self._add_olist_node(m)
            elif self.regexps['definitionlist'].match(line):
                m = self.regexps['definitionlist'].match(line)
                self._add_dlist_node(m)
            elif self.regexps['unorderedlist'].match(line):
                m = self.regexps['unorderedlist'].match(line)
                self._add_ulist_node(m)
            elif self.regexps['tablerow'].match(line):
                m = self.regexps['tablerow'].match(line)
                self._add_tablerow(m)
            elif not line:
                if isinstance(self.current, Paragraph):
                    self.current = self.current.parent
            elif not isinstance(self.current, Heading) and isinstance(self.current, Node):
                self.current.append(Text(line))
            else:
                node = Paragraph()
                self.current.append(node)
                self.current = node
                self.current.append(Text(line))
        if self.bquote_flg:
            raise NestingNotValidError


    def _add_heading_node(self, heading):
        while isinstance(self.current, Heading) and self.current.depth >= heading.depth:
            self.current = self.current.parent
        self.current.append(heading)
        self.current = heading

    def _add_list_node(self, m, listclass=List):
        if ((isinstance(self.current, listclass) and len(m.group('depth')) > self.current.depth) or
            not isinstance(self.current, listclass)):
            listnode = listclass(depth=len(m.group('depth')))
            self.current.append(listnode)
            self.current = listnode
        while isinstance(self.current, listclass) and len(m.group('depth')) < self.current.depth:
            self.current = self.current.parent
        self.current.append(ListItem(m.group('item')))

    def _add_olist_node(self, m):
        self._add_list_node(m, listclass=OrderedList)

    def _add_ulist_node(self, m):
        self._add_list_node(m, listclass=UnOrderedList)

    def _add_dlist_node(self, m):
        if ((isinstance(self.current, DefinitionList) and len(m.group('depth')) > self.current.depth) or
            not isinstance(self.current, DefinitionList)):
            listnode = DefinitionList(depth=len(m.group('depth')))
            self.current.append(listnode)
            self.current = listnode
        while isinstance(self.current, DefinitionList) and len(m.group('depth')) < self.current.depth:
            self.current = self.current.parent
        self.current.append(DefinitionListItem(m.group('item'), m.group('description')))

    def _add_tablerow(self, m):
        cells = [c for c in m.group('cells').split('|') if c!='']
        if not isinstance(self.current, Table):
            tablenode = Table()
            self.current.append(tablenode)
            self.current = tablenode
        rownode = TableRow()
        self.current.append(rownode)
        self.current = rownode
        for cell in cells:
            cellnode = TableCell()
            self.current.append(cellnode)
            self.current = cellnode
            self._parse(cell)
            self.current = self.current.parent
        self.current = self.current.parent

    def append(self, child):
        if isinstance(child, str):
            child = Text(child)
        self.children.append(child)
        child.parent = self

    def html(self):
        return '\n'.join([child.html() for child in self.children])


def org_to_html(text):
    return Org(text).html()
