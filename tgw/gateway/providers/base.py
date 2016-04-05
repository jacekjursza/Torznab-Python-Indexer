import requests
from lxml import html


class Base:
    url = ''

    def fetch_body(self, data):
        query_url = self.url % data
        resp = requests.get(query_url)
        if resp.status_code != 200:
            raise ScrapError()
        return resp.text

    def get_items(self, qs, xpath):
        body = self.fetch_body(qs)
        tree = html.fromstring(body)
        elems = tree.xpath(xpath)
        return elems


class ScrapError(Exception):
    pass