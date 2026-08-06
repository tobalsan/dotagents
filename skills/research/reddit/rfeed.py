import sys, re, html, xml.etree.ElementTree as ET
N = {'a': 'http://www.w3.org/2005/Atom'}
for e in ET.parse(sys.argv[1]).getroot().findall('a:entry', N):
    g = lambda p: (e.find(p, N).text or '') if e.find(p, N) is not None else ''
    body = re.sub(r'<[^>]+>', '', html.unescape(g('a:content')))
    body = re.sub(r'\s*submitted by\s*/u/\S+\s*\[link\]\s*\[comments\]\s*$', '', body).strip()
    print(f"## {g('a:title')}\n{e.find('a:link', N).get('href')}\n{g('a:updated')[:10]} | {g('a:author/a:name')}\n{body}\n")
