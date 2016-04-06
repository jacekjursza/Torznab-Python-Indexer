from base import Base
import time
import re


class PirateBay(Base):
    url = 'https://thepiratebay.se/%s'
    new_shows_qs = 'tv/latest/'
    search_qs = 'search/%s/0/99/205'
    elem_path = '//*[@id="searchResult"]/tr[*]'
    r_date = re.compile('(?:(?i)Uploaded (\d\d)\-(\d\d).(\d\d):(\d\d),)')
    r_date_year = re.compile('(?:(?i)Uploaded (\d\d)-(\d\d).(\d\d\d\d),)')
    r_size_mb = re.compile('(?:(?i)Size (.*?).MiB)')
    r_size_gb = re.compile('(?:(?i)Size (.*?).GiB)')

    def get_new_shows(self):
        items = self.get_items(self.new_shows_qs, self.elem_path)
        return self.parse_results(items)

    def get_search(self, phrase):
        items = self.get_items(self.search_qs % phrase, self.elem_path)
        return self.parse_results(items)

    def handle_request(self, request):
        q = request.GET.get('q')
        if q:
            #   doing regular query, where 'q' is the search phrase
            search_query = q
            if request.GET.get('season'):
                search_query += ' S' + request.GET.get('season').zfill(2)
                if request.GET.get('ep'):
                    search_query += 'E' + request.GET.get('ep').zfill(2)
            elements = self.get_search(search_query)
        else:
            if not request.GET.get('rid'):
                #   we need to handle query without params 'q' and 'rid'
                #   it is required by Sonarr test and for RSS checks
                elements = self.get_new_shows()
            else:
                #   it's important to return empty list if query is via 'rid' as we don't support it
                #   Sonarr will do another request, this time with string query 'q'
                elements = []

        return elements

    def parse_results(self, items):
        result = []
        for item in items:
            desc = item.cssselect('td > font.detDesc')
            if desc:
                desc = desc[0]
            else:
                continue
            seeders = item.cssselect('td')[2]
            peers = item.cssselect('td')[3]
            date_a = self.r_date.findall(desc.text)
            date_b = self.r_date_year.findall(desc.text)
            size_a = self.r_size_mb.findall(desc.text)
            size_b = self.r_size_gb.findall(desc.text)

            result.append({
                'title': item.cssselect('div > a')[0].text,
                'permlink': self.url % item.cssselect('div > a')[0].get('href', default="k"),
                'magnet': item.cssselect('td > a')[0].get('href'),
                'date': self.__format_date(date_a, date_b),  #Sun, 06 Jun 2010 17:29:23 +0100
                'seeders': seeders.text,
                'peers': peers.text,
                'size': self.__format_size(size_a, size_b)
            })
        return result

    @staticmethod
    def __format_date(a, b):
        input_date_format = '%Y-%m-%d %H:%M'
        output_date_format = '%a, %d %b %Y %H:%M:00 +0100'
        a = a[0] if len(a) == 1 else a
        b = b[0] if len(b) == 1 else b
        if a:
            date_string = time.strftime('%Y', time.gmtime()) + '-' + a[0] + '-' + a[1] + ' ' + a[2] + ':' + a[3]
        elif b:
            date_string = b[2] + '-' + b[0] + '-' + b[1] + ' 00:00'
        else:
            date_string = time.strftime(input_date_format, time.gmtime())

        output = time.strftime(output_date_format, time.strptime(date_string, input_date_format))
        return output

    @staticmethod
    def __format_size(a, b):
        if len(a) == 1:
            a = a[0]
        if len(b) == 1:
            b = b[0]
        if a:
            return int(float(a) * 1024 * 1024)
        if b:
            return int(float(b) * 1024 * 1024 * 1024)
        return 0


if __name__ == '_main__':
    tpb = PirateBay()
    res = tpb.get_search('Arrow')

