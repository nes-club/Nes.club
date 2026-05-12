import logging
from collections import namedtuple
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from django.utils.html import strip_tags
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 "
                  "Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}
DEFAULT_REQUEST_TIMEOUT = 10
MAX_PARSABLE_CONTENT_LENGTH = 15 * 1024 * 1024  # 15Mb

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
log = logging.getLogger(__name__)

ParsedURL = namedtuple("ParsedURL", ["url", "domain", "title", "favicon", "summary", "image", "description"])


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.image = ""
        self.favicon = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            prop = attrs.get("property", "").lower()
            if name == "description" or prop == "og:description":
                self.description = attrs.get("content", "")
            elif prop == "og:image":
                self.image = attrs.get("content", "")
        elif tag == "link" and "icon" in attrs.get("rel", ""):
            self.favicon = attrs.get("href", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse_url_preview(url: str) -> Optional[ParsedURL]:
    real_url, content_type, _ = resolve_url(url)
    if not real_url or not content_type or not content_type.startswith("text/"):
        return None

    try:
        response = requests.get(
            url=real_url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers=DEFAULT_REQUEST_HEADERS,
            stream=True,
        )
        html = response.raw.read(MAX_PARSABLE_CONTENT_LENGTH, decode_content=True).decode("utf-8", errors="ignore")
    except RequestException:
        return None

    parser = _MetaParser()
    try:
        parser.feed(html)
    except Exception:
        return None

    canonical_url = real_url
    return ParsedURL(
        url=canonical_url,
        domain=urlparse(canonical_url).netloc,
        title=strip_tags(parser.title.strip()),
        favicon=strip_tags(urljoin(canonical_url, parser.favicon)),
        summary="",
        image=parser.image,
        description=parser.description,
    )


def resolve_url(entry_link):
    url = str(entry_link)
    content_type = None
    content_length = MAX_PARSABLE_CONTENT_LENGTH + 1
    depth = 10
    while depth > 0:
        depth -= 1
        try:
            response = requests.head(url, timeout=DEFAULT_REQUEST_TIMEOUT, verify=False, stream=True)
        except RequestException:
            log.warning(f"Failed to resolve URL: {url}")
            return None, content_type, content_length

        if 300 < response.status_code < 400:
            url = response.headers.get("location", url)
        else:
            content_type = response.headers.get("content-type")
            content_length = int(response.headers.get("content-length") or 0)
            break

    return url, content_type, content_length
