"""Validate static links, anchors, generated output, and diagram XML without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.refs=[];self.ids=set();self.duplicates=[];self.h1=0;self.title=0
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs)
        if 'id' in attr:
            if attr['id'] in self.ids:self.duplicates.append(attr['id'])
            self.ids.add(attr['id'])
        for key in ('href','src'):
            if attr.get(key):self.refs.append(attr[key])
        if tag=='h1':self.h1+=1
        if tag=='title':self.title+=1


def main():
    pages={p:Page(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
    errors=[]
    for path,page in pages.items():
        if page.h1!=1:errors.append(f'{path.name}: expected one h1')
        if page.duplicates:errors.append(f'{path.name}: duplicate ids {page.duplicates}')
        for ref in page.refs:
            parsed=urlsplit(ref)
            if parsed.scheme or parsed.netloc:continue
            raw=unquote(parsed.path)
            if raw.startswith('/ai-evals-atlas/'):raw=raw[len('/ai-evals-atlas/'):]
            target=(path.parent/raw).resolve() if raw else path
            if target.is_dir():target=target/'index.html'
            if not target.exists():errors.append(f'{path.name}: missing {ref}')
            if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{path.name}: missing anchor {ref}')
    for diagram in (ROOT/'assets/diagrams').glob('*.svg'):
        try:ET.parse(diagram)
        except ET.ParseError as error:errors.append(f'{diagram.name}: {error}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(pages)} pages; all local links, anchors, IDs, and SVG files validated.')


if __name__=='__main__':main()
