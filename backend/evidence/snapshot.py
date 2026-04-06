from playwright.sync_api import sync_playwright
import hashlib, time

def capture(url, path):
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page()
        page.goto(url)
        page.screenshot(path=path, full_page=True)
        browser.close()
    h=hashlib.sha256(open(path,'rb').read()).hexdigest()
    return {'url':url,'file':path,'hash':h,'ts':time.time()}
