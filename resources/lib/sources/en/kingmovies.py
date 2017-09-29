# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import re,urllib,urlparse,json,base64,time

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import directstream

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['kingmovies.to']
        self.base_link = 'https://kingmovies.to'
        self.search_link = '/search?q=%s'
        self.token_link = 'https://embed.streamdor.co/token.php?episode=%s'
        self.source_link = 'https://embed.streamdor.co/api/video/%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            cltitle = cleantitle.get(title+'season'+season)
            search = '%s Season %01d' % (title, int(season))
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))
            r = client.request(url, timeout='15')
            r = [i[0] for i in re.findall(r"<li\s+class='movie-item'\s+data-url='([^']+)'\s+data-title=\"([^\"]+)\">",r, re.IGNORECASE) if cleantitle.get(i[1]) == cltitle]
            for u in r:
                try:
                    result = client.request(urlparse.urljoin(self.base_link, u), timeout=10)
                    result = json.loads(result)['html']
                    match = re.findall(r'Season\s+%s.*?class="jtip-bottom"><a\s+href="([^"]+)"' % season, result, re.DOTALL)[0]
                    if not match == None: break
                except:
                    pass
            if match == None: return
            else: url = match

            #r = client.parseDOM(r, 'div', attrs={'class': 'item-detail'})
            #r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            #r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
            #r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
            #url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
            url = '%s/watching.html' % url
            return url
        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            cltitle = cleantitle.get(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = client.request(url, timeout='15')
            r = [i[0] for i in re.findall(r"<li\s+class='movie-item'\s+data-url='([^']+)'\s+data-title=\"([^\"]+)\">",r, re.IGNORECASE) if cleantitle.get(i[1]) == cltitle]
            for u in r:
                try:
                    result = client.request(urlparse.urljoin(self.base_link, u), timeout=10)
                    result = json.loads(result)['html']
                    match = re.findall(r'Year<\/span><span\s+class="jb-bot">%s<\/span>.*?class="jtip-bottom"><a\s+href="([^"]+)"'%year, result, re.DOTALL)[0]
                    if not match == None: break
                except:
                    pass
            if match == None: return
            else: url = match

            #r = [client.parseDOM(r, 'li', attrs={'class': 'movie-item'}, ret='data-url') for i in r if re.search(r'data-title="%s"'%title, i)]
            #r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            #results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
            #try:
            #    r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
            #    url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
            #except:
            #    url = None
            #    pass

            #if (url == None):
            #    url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]

            url = '%s/watching.html' % url
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                year = re.compile('(\d{4})-(\d{2})-(\d{2})').findall(data['premiered'])[0][0]
                episode = '%01d' % int(data['episode'])
                url = '%s/tv-series/%s-season-%01d/watch/' % (self.base_link, cleantitle.geturl(data['tvshowtitle']), int(data['season']))
                url = client.request(url, headers=headers, timeout='10', output='geturl')

                if url == None:
                    url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)

            else:
                episode = None
                year = data['year']
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            referer = url
            r = client.request(url)
            if episode == None:
                y = re.findall('Released\s*:\s*.+?\s*(\d{4})', r)[0]
                if not year == y: raise Exception()

            r = client.parseDOM(r, 'div', attrs = {'class': 'sli-name'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))

            if not episode == None:
                r = [i[0] for i in r if i[1].lower().startswith('episode %02d:' % int(data['episode']))]
            else:
                r = [i[0] for i in r]

            for u in r:
                try:
                    p = client.request(u, headers=headers, referer=referer, timeout='10')
                    src = re.findall('src\s*=\s*"(.*streamdor.co/video/\d+)"', p)[0]
                    if src.startswith('//'):
                        src = 'http:'+src
                    episodeId = re.findall('.*streamdor.co/video/(\d+)', src)[0]
                    p = client.request(self.token_link % episodeId, referer=src)
                    #script = self.aadecode(p)
                    token = re.search('''token\s*:\s*['"]([^"']+)''', p).group(1).encode('utf-8')
                    post = {'type': 'sources', 'token': token, 'ref': urllib.quote_plus(referer)}
                    p = client.request(self.source_link % episodeId, post=post, referer=src, XHR=True)
                    js = json.loads(p)

                    try:
                        u = js['playlist'][0]['sources']
                        u = [i['file'] for i in u if 'file' in i]

                        for i in u:
                            try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                            except: pass
                    except:
                        pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return directstream.googlepass(url)
