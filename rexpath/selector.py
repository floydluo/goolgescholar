"""
XPath selectors based on lxml
"""

import warnings
from parsel import Selector as _ParselSelector
from .utils import object_ref, to_bytes, deprecated

__all__ = ['Selector', 'SelectorList']


class SelectorList(_ParselSelector.selectorlist_cls, object_ref):
    @deprecated(use_instead='.extract()')
    def extract_unquoted(self):
        return [x.extract_unquoted() for x in self]

    @deprecated(use_instead='.xpath()')
    def x(self, xpath):
        return self.select(xpath)

    @deprecated(use_instead='.xpath()')
    def select(self, xpath):
        return self.xpath(xpath)


class Selector(_ParselSelector, object_ref):

    __slots__ = ['response']
    selectorlist_cls = SelectorList

    def __init__(self, response=None, text=None, type=None, root=None, **kwargs):

        st = self._default_type

        if response is not None:
            text = response.text
            kwargs.setdefault('base_url', response.url)

        self.response = response
        super(Selector, self).__init__(text=text, type=st, root=root, **kwargs)

    @deprecated(use_instead='.xpath()')
    def select(self, xpath):
        return self.xpath(xpath)

    @deprecated(use_instead='.extract()')
    def extract_unquoted(self):
        return self.extract()
