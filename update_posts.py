# Copies the latest posts from The Eurostar into writing.html and index.html.
# GitHub runs this every morning (see .github/workflows/substack.yml).
# Substack often blocks requests from GitHub's servers, so if the direct feed fails
# the script asks rss2json.com (a free feed-reading service) to fetch it instead.
import html, json, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

FEED = 'https://theeurostar.substack.com/feed'
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'}
get = lambda url: urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
card = lambda link, img, date, title: (f'<a class="post" href="{link}">' + (f'<img src="{img}" alt="" loading="lazy">' if img else '<i class="noimg"></i>')
                                        + f'<time>{date:%b %Y}</time><strong>{html.escape(title)}</strong></a>')
try:
    items = ET.fromstring(get(FEED)).iter('item')
    cards = [card(i.findtext('link'), (i.find('enclosure').get('url') if i.find('enclosure') is not None else ''),
                  parsedate_to_datetime(i.findtext('pubDate')), i.findtext('title') or '') for i in items]
    print('Read the feed directly from Substack.')
except Exception as e:
    print(f'Direct feed failed ({e}); trying rss2json.com instead.')
    try:
        data = json.loads(get('https://api.rss2json.com/v1/api.json?rss_url=' + urllib.parse.quote(FEED, safe='')))
    except Exception as e2:
        sys.exit(f'rss2json.com failed too: {e2}')
    if data.get('status') != 'ok':
        sys.exit(f'rss2json.com could not read the feed: {data.get("message")}')
    cards = [card(i['link'], i.get('enclosure', {}).get('link') or i.get('thumbnail') or '',
                  datetime.strptime(i['pubDate'], '%Y-%m-%d %H:%M:%S'), i['title']) for i in data['items']]
if not cards:
    sys.exit('The feed was read but contained no posts.')

for path, tag, n in [('writing.html', 'POSTS', 50), ('index.html', 'LATEST', 4)]:
    try:
        page = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        sys.exit(f'{path} is not at the top level of the repository.')
    if f'<!-- {tag} -->' not in page:
        sys.exit(f'{path} is missing the <!-- {tag} --> marker, so there is nowhere to put the posts.')
    new = f'<!-- {tag} -->\n' + '\n'.join(cards[:n]) + f'\n<!-- /{tag} -->'
    open(path, 'w', encoding='utf-8').write(re.sub(f'<!-- {tag} -->.*?<!-- /{tag} -->', lambda m: new, page, flags=re.S))
print(f'Updated {len(cards)} posts.')
