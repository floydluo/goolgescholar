"""
This module implements the TextResponse class which adds encoding handling and
discovering (through HTTP headers) to base Response class.

See documentation in docs/topics/request-response.rst
"""

import six
from six.moves.urllib.parse import urljoin

from w3lib.encoding import html_to_unicode, \
                           resolve_encoding, \
                           html_body_declared_encoding, \
                           http_content_type_encoding

from .utils import get_base_url, \
                  memoizemethod_noargs, \
                  to_native_str, \
                  object_ref, \
                  obsolete_setter

from .headers import Headers


class Response(object_ref):

    def __init__(self, url, status=200, headers=None, body=b'', flags=None, request=None):
        self.headers = Headers(headers or {})
        self.status = int(status)
        self._set_body(body)
        self._set_url(url)
        self.request = request
        self.flags = [] if flags is None else list(flags)

    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"
            )

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        if isinstance(url, str):
            self._url = url
        else:
            raise TypeError('%s url must be str, got %s:' % (type(self).__name__,
                type(url).__name__))

    url = property(_get_url, obsolete_setter(_set_url, 'url'))

    def _get_body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        elif not isinstance(body, bytes):
            raise TypeError(
                "Response body must be bytes. "
                "If you want to pass unicode body use TextResponse "
                "or HtmlResponse.")
        else:
            self._body = body

    body = property(_get_body, obsolete_setter(_set_body, 'body'))

    def __str__(self):
        return "<%d %s>" % (self.status, self.url)

    __repr__ = __str__

    def urljoin(self, url):
        return urljoin(self.url, url)


class TextResponse(Response):

    _DEFAULT_ENCODING = 'ascii'

    def __init__(self, *args, **kwargs):
        self._encoding = kwargs.pop('encoding', None)
        self._cached_benc = None
        self._cached_ubody = None
        self._cached_selector = None
        super(TextResponse, self).__init__(*args, **kwargs)

    def _set_url(self, url):
        if isinstance(url, six.text_type):
            if six.PY2 and self.encoding is None:
                raise TypeError("Cannot convert unicode url - %s "
                                "has no encoding" % type(self).__name__)
            self._url = to_native_str(url, self.encoding)
        else:
            super(TextResponse, self)._set_url(url)

    def _set_body(self, body):
        self._body = b''  # used by encoding detection
        if isinstance(body, six.text_type):
            if self._encoding is None:
                raise TypeError('Cannot convert unicode body - %s has no encoding' %
                    type(self).__name__)
            self._body = body.encode(self._encoding)
        else:
            super(TextResponse, self)._set_body(body)

    def replace(self, *args, **kwargs):
        kwargs.setdefault('encoding', self.encoding)
        return Response.replace(self, *args, **kwargs)

    @property
    def encoding(self):
        return self._declared_encoding() or self._body_inferred_encoding()

    def _declared_encoding(self):
        return self._encoding or self._headers_encoding() \
            or self._body_declared_encoding()

    def body_as_unicode(self):
        """Return body as unicode"""
        return self.text

    @property
    def text(self):
        """ Body as unicode """
        # access self.encoding before _cached_ubody to make sure
        # _body_inferred_encoding is called
        benc = self.encoding
        if self._cached_ubody is None:
            charset = 'charset=%s' % benc
            self._cached_ubody = html_to_unicode(charset, self.body)[1]
        return self._cached_ubody

    def urljoin(self, url):
        """Join this Response's url with a possible relative url to form an
        absolute interpretation of the latter."""
        return urljoin((self), url)

    @memoizemethod_noargs
    def _headers_encoding(self):
        content_type = self.headers.get(b'Content-Type', b'')
        return http_content_type_encoding(to_native_str(content_type))

    def _body_inferred_encoding(self):
        if self._cached_benc is None:
            content_type = to_native_str(self.headers.get(b'Content-Type', b''))
            benc, ubody = html_to_unicode(content_type, self.body,
                    auto_detect_fun=self._auto_detect_fun,
                    default_encoding=self._DEFAULT_ENCODING)
            self._cached_benc = benc
            self._cached_ubody = ubody
        return self._cached_benc

    def _auto_detect_fun(self, text):
        for enc in (self._DEFAULT_ENCODING, 'utf-8', 'cp1252'):
            try:
                text.decode(enc)
            except UnicodeError:
                continue
            return resolve_encoding(enc)

    @memoizemethod_noargs
    def _body_declared_encoding(self):
        return html_body_declared_encoding(self.body)

    @property
    def selector(self):
        from .selector import Selector
        if self._cached_selector is None:
            self._cached_selector = Selector(self)
        return self._cached_selector

    def xpath(self, query, **kwargs):
        return self.selector.xpath(query, **kwargs)

