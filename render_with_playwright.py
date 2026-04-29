#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import os

os.makedirs("/root/.openclaw/workspace/slides_png_v2", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    for i in range(1, 26):
        html_path = f"/root/.openclaw/workspace/slides_html/slide_{i:02d}.html"
        png_path = f"/root/.openclaw/workspace/slides_png_v2/slide_{i:02d}.png"
        
        page.goto(f"file://{html_path}", wait_until="networkidle")
        page.wait_for_timeout(500)  # доп. ожидание для шрифтов
        page.screenshot(path=png_path, full_page=False)
        
        size = os.path.getsize(png_path)
        print(f"✓ slide_{i:02d}.png — {size/1024:.0f} KB")
    
    browser.close()

print("Все слайды отрендерены через Playwright")
