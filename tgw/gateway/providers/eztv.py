import re
import time
from base import Base

class EZTV(Base):
    url = 'http://eztv.ag/%s'
    search_qs = 'search/?q1={search}&q2={id}&search=Search'
    elem_path = '//table[@class="forum_header_border"]/tr'
    show_id = ''
    max_cache_age = 21600 #6hours
    cache_updated = 0
    shows_dict = {}
    fake_seeders = True

    def __init__(self):
        self._ref_cache()

    def _ref_cache(self):
        show_list_elem_path = '//select[@class="tv-show-search-select"]/option'
        shows_html_opts = self.get_items('', show_list_elem_path)
        for o in shows_html_opts:
            t=o.text.encode('ascii','replace')
            #Strip out Years
            sname = ''.join(re.split('\([0-9]{4,4}\)',t))
            #Strip off the "The" portion of show names
            if ', The' in sname:
                m = re.search(', The ',sname)
                sname = ''.join([ sname[:m.start()], sname[m.end():] ])
            #Strip out other parenthesised bits for generic show names.
            sname = ''.join(re.split('\([A-Z &]+\)',sname))
            #Remove various puncuation
            sname = re.sub(r"[,\.']","",sname)
            #Strip remaining whitespace and lower case the show names
            sname = sname.strip().lower()
            self.shows_dict[sname] = o.attrib['value']
        self.cache_updated = time.time()

    def _age_to_date(self, age):
        import datetime
        increm_dict = {
            'hours': ('hours',1),
            'days': ('days',1),
            'weeks': ('weeks',1),
            'week': ('weeks',1),
            'mo': ('weeks',4),
            'year': ('weeks',52),
            'years': ('weeks',52)
            }
        #Create datetime format
        datetime_format = '%a, %d %b %Y %H:%M:00 %z'
        
        cur_num=0
        tdelay_args={}
        
        #Clean up some shortened time units
        age = age.replace('h',' hours')
        age = age.replace('d',' days')
        for i in age.split():
            try:
                #Test if it is a number
                n = int(i)
                cur_num = n
            except ValueError:
                #Not a number, so is a time unit.
                try:
                    #If we don't recognize the time increment, then default to day.
                    increm = increm_dict[i]
                except KeyError:
                    increm = ('days',1)
                    #Add the number with proper unit to our timedelay args.
                tdelay_args[increm[0]] = cur_num * increm[1]
                #reset
                cur_num = 0
        date=datetime.datetime.now() - datetime.timedelta(**tdelay_args)
        return date.strftime(datetime_format)

    def _size_to_bytes(self, size):
        size_conversion = {
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024
        }
        if size:
            size_split=size.split()
            #Convert the size from MB/GB to Bytes
            try:
                size_bytes = int(float(size_split[0]) * size_conversion[size_split[1]])
            except KeyError:
                try:
                    size_bytes = int(size_split[0])
                except ValueError:
                    size_bytes = 1
        else:
            size_bytes = 1
        return size_bytes

    def get_search(self, show_title='', title_filter=''):
        search_params={
            'id': '',
            'search': ''
        }

        if time.time() - self.cache_updated > self.max_cache_age:
            self._ref_cache()

        #Try and look up torrents for known shows, if we can't find the show
        #then default back to a text search.
        if show_title:
            try:
                search_params['id'] = self.shows_dict[show_title.lower()]
            except KeyError:
                search_params['search'] = show_title

        items = self.get_items(self.search_qs.format(**search_params), self.elem_path)
        shows = self.parse_items(items, title_filter)
        #If EZTV doesn't find anything for a text search, it return 'latest'
        #which are garbage for our purpose. So only count shows that actually
        #have the text for what was searched for contained in the title.
        if search_params['search']:
            real_matches = []
            for s in shows:
                if show_title.lower() in s['title'].lower():
                    real_matches.append(s)
            shows = real_matches
        return shows

    def parse_items(self, items, title_filter=''): 
        results = []

        for e in items:
            res_d = {}
            if e.values():
                try:
                    cells = e.cssselect('td[class=forum_thread_post]')
                    res_d['title'] = cells[1].cssselect('a')[0].text
                    if title_filter:
                        if title_filter.upper() not in res_d['title'].upper():
                            continue
                    res_d['permlink'] = self.url % '' + cells[1].cssselect('a')[0].get('href')
                    res_d['magnet'] = cells[2].cssselect('a[class=magnet]')[0].values()[0]
                    res_d['size'] = self._size_to_bytes(cells[3].text)
                    res_d['date'] = self._age_to_date(cells[4].text)
                    if self.fake_seeders:
                        #EZTV doesn't offer seeder/peer data, even though the torrents are heavily shared.
                        #Faking the seeders allows sonarr to prioritize by file size
                        #Formula is basically 1 fake seeder per 1 MB
                        res_d['seeders'] = res_d['size'] / 1024 / 1024 / 10
                        res_d['peers'] = res_d['seeders']
                except IndexError:
                    continue
                results.append(res_d)
        return results

    def handle_request(self, request):
        title_filter = ''
        show_title = ''
        q = request.GET.get('q')
        if q:
            #   doing regular query, where 'q' is the search phrase
            show_title = q
            if request.GET.get('season'):
                title_filter += 'S' + request.GET.get('season').zfill(2)
                if request.GET.get('ep'):
                    title_filter += 'E' + request.GET.get('ep').zfill(2)
        else:
            if request.GET.get('rid'):
                #   it's important to return empty list if query is via 'rid' as we don't support it
                #   Sonarr will do another request, this time with string query 'q'
                return []

        show_results = self.get_search(show_title, title_filter)
        return show_results

if __name__ == '__main__':
    import json
    ezt = EZTV()
    res = ezt.get_search('Arrow')
    print(json.dumps(res,indent=4))
