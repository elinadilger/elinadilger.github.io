# Copies the latest posts from The Eurostar into writing.html and index.html.
# GitHub runs this every morning (see .github/workflows/substack.yml).
import html, re, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

req = urllib.request.Request('https://theeurostar.substack.com/feed', headers={'User-Agent': 'Mozilla/5.0'})
cards = []
for item in ET.fromstring(urllib.request.urlopen(req).read()).iter('item'):
    enc = item.find('enclosure')
    img = f'<img src="{enc.get("url")}" alt="" loading="lazy">' if enc is not None else '<i class="noimg"></i>'
    date = parsedate_to_datetime(item.findtext('pubDate')).strftime('%b %Y')
    cards.append(f'<a class="post" href="{item.findtext("link")}">{img}<time>{date}</time>'
                 f'<strong>{html.escape(item.findtext("title") or "")}</strong></a>')

for path, tag, n in [('writing.html', 'POSTS', 50), ('index.html', 'LATEST', 4)]:
    page = open(path, encoding='utf-8').read()
    new = f'<!-- {tag} -->\n' + '\n'.join(cards[:n]) + f'\n<!-- /{tag} -->'
    open(path, 'w', encoding='utf-8').write(re.sub(f'<!-- {tag} -->.*?<!-- /{tag} -->', lambda m: new, page, flags=re.S))
