"""Browser integration checks. Install playwright and its Chromium browser first."""
from pathlib import Path
import functools
import http.server
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


handler=functools.partial(QuietHandler,directory=str(ROOT))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'

try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        for file in ROOT.glob('*.html'):
            page.goto(base+'/'+file.name)
            assert page.locator('h1').count()==1,file.name
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Desktop overflow: {file.name}'
        page.goto(base+'/index.html')
        page.keyboard.press('/')
        page.locator('#site-search').fill('contamination')
        assert page.locator('.search-result').count()>0
        page.locator('#site-search').fill('qzxnoresults')
        assert 'No matching' in page.locator('#search-results').inner_text()
        page.keyboard.press('Escape')
        page.locator('dialog').wait_for(state='hidden')
        assert not page.locator('dialog').is_visible()
        page.goto(base+'/foundations.html')
        page.locator('[data-complete]').click()
        page.reload()
        assert page.locator('[data-complete]').get_attribute('aria-pressed')=='true'
        assert '1 of 18' in page.locator('#progress-label').inner_text()
        page.locator('summary').click()
        assert page.locator('details').get_attribute('open') is not None
        page.goto(base+'/benchmarks.html')
        page.locator('#benchmark-category').select_option('Code')
        assert page.locator('.benchmark-card:visible').count()==2
        page.locator('#benchmark-search').fill('qzx')
        assert page.locator('#benchmark-empty').is_visible()
        page.goto(base+'/playground.html')
        assert '80.0%' in page.locator('#wilson-output').inner_text()
        assert '71.1% to 86.7%' in page.locator('#wilson-output').inner_text()
        assert '72.7%' in page.locator('#f1-output').inner_text()
        assert '$9.00' in page.locator('#cost-output').inner_text()
        page.locator('#successes').fill('101')
        assert 'cannot exceed' in page.locator('#wilson-output').inner_text()
        page.locator('#total').fill('0')
        assert page.locator('#wilson-output').evaluate("el => el.classList.contains('error')")
        for name in ('tp','fp','fn'):page.locator('#'+name).fill('0')
        assert 'undefined' in page.locator('#f1-output').inner_text()
        page.goto(base+'/glossary.html')
        page.locator('#glossary-search').fill('LoRA')
        assert page.locator('.glossary-entry:visible').count()==1
        page.set_viewport_size({'width':390,'height':844})
        for file in ROOT.glob('*.html'):
            if file.name=='404.html':continue
            page.goto(base+'/'+file.name)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Mobile overflow: {file.name}'
        page.goto(base+'/index.html')
        page.locator('.menu-toggle').click()
        assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='true'
        page.locator('.side-nav a[href="foundations.html"]').click()
        assert page.url.endswith('foundations.html')
        assert not errors,errors
        context=browser.new_context(java_script_enabled=False)
        static=context.new_page()
        static.goto(base+'/foundations.html')
        assert 'evaluation' in static.locator('article').inner_text().lower()
        context.close();browser.close()
        print('PASS: browser navigation, search, progress, filters, calculators, mobile layout, and no-JS reading.')
finally:
    server.shutdown()
