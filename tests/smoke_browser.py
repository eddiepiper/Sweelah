"""Local browser smoke test. Creates a screenshot inside outputs/ for internal QA."""
from pathlib import Path
import subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
root=Path(__file__).parents[1]
proc=subprocess.Popen([sys.executable,'-m','uvicorn','retirepilot.api:app','--host','127.0.0.1','--port','8769','--log-level','warning'],cwd=str(root),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(30):
        try:
            urllib.request.urlopen('http://127.0.0.1:8769/',timeout=1).read();break
        except Exception:time.sleep(.2)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path="/usr/bin/chromium",args=["--no-sandbox"])
        page=browser.new_page(viewport={'width':1440,'height':950},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8769',wait_until='networkidle')
        page.locator('#personas .score').first.wait_for(timeout=15000)
        print('title:',page.title())
        print('metrics:',page.locator('#metrics').inner_text().replace('\n',' | ')[:250])
        print('personas:',page.locator('#personas .score').count())
        page.locator('button[data-q="How is my cash flow?"]').click()
        page.get_by_text('7200.00',exact=False).first.wait_for(timeout=10000)
        page.screenshot(path=str(root/'outputs/browser-desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.screenshot(path=str(root/'outputs/browser-mobile.png'),full_page=True)
        print('errors:',errors)
        assert not errors
        browser.close()
finally:
    proc.terminate();proc.wait(timeout=5)
