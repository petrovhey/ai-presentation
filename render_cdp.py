#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import os

os.makedirs("/root/.openclaw/workspace/slides_final", exist_ok=True)

ws_url = "ws://127.0.0.1:18800/devtools/page/8F6B2799CEAD7D856C246B6BA82B288B"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    for i in range(1, 26):
        html_url = f"http://localhost:8888/slide_{i:02d}.html"
        png_path = f"/root/.openclaw/workspace/slides_final/slide_{i:02d}.png"
        
        page.goto(html_url, wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=png_path, full_page=False)
        
        size = os.path.getsize(png_path)
        print(f"✓ slide_{i:02d}.png — {size/1024:.0f} KB")
    
    browser.close()

print("Все слайды отрендерены через CDP")
