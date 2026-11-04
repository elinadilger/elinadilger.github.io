# Copies the latest posts from The Eurostar into writing.html and index.html.
# GitHub runs this every morning (see .github/workflows/substack.yml).
import html, re, sys, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

req = urllib.request.Request('https://theeurostar.substack.com/feed', headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8'})
try:
    feed = urllib.request.urlopen(req, timeout=30).read()
except Exception as e:
    sys.exit(f'Could not download the Substack feed: {e}')

cards = []
for item in ET.fromstring(feed).iter('item'):
    enc = item.find('enclosure')
    img = f'<img src="{enc.get("url")}" alt="" loading="lazy">' if enc is not None else '<i class="noimg"></i>'
    date = parsedate_to_datetime(item.findtext('pubDate')).strftime('%b %Y')
    cards.append(f'<a class="post" href="{item.findtext("link")}">{img}<time>{date}</time>'
                 f'<strong>{html.escape(item.findtext("title") or "")}</strong></a>')
if not cards:
    sys.exit('The Substack feed downloaded but contained no posts.')

for path, tag, n in [('writing.html', 'POSTS', 50), ('index.html', 'LATEST', 4)]:
    page = open(path, encoding='utf-8').read()
    if f'<!-- {tag} -->' not in page:
        sys.exit(f'{path} is missing the <!-- {tag} --> marker, so there is nowhere to put the posts.')
    new = f'<!-- {tag} -->\n' + '\n'.join(cards[:n]) + f'\n<!-- /{tag} -->'
    open(path, 'w', encoding='utf-8').write(re.sub(f'<!-- {tag} -->.*?<!-- /{tag} -->', lambda m: new, page, flags=re.S))
print(f'Updated {len(cards)} posts.')
