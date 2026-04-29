#!/usr/bin/env python3
"""
Склеиваем 25 HTML-слайдов в один PDF через weasyprint.
Каждый слайд на отдельной странице 1920x1080.
"""
import os
from weasyprint import HTML, CSS

# Читаем CSS из первого HTML (он внутри <style>)
with open("/root/.openclaw/workspace/slides_html/slide_01.html", encoding="utf-8") as f:
    first_html = f.read()

# Извлекаем CSS
import re
css_match = re.search(r'<style>(.*?)</style>', first_html, re.DOTALL)
base_css = css_match.group(1) if css_match else ""

# Добавляем стили для page-break
page_css = f"""
{base_css}
@page {{
    size: 1920px 1080px;
    margin: 0;
}}
.slide-page {{
    page-break-after: always;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    position: relative;
}}
.slide-page:last-child {{
    page-break-after: auto;
}}
"""

# Собираем HTML
full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>{page_css}</style>
</head>
<body>
"""

for i in range(1, 26):
    with open(f"/root/.openclaw/workspace/slides_html/slide_{i:02d}.html", encoding="utf-8") as f:
        html = f.read()
    
    # Извлекаем содержимое между <body> и </body>
    body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    body_content = body_match.group(1) if body_match else ""
    
    # Убираем внешний .slide div, заменяем на .slide-page
    body_content = re.sub(r'<div class="slide no-header">', '<div class="slide-page">', body_content)
    body_content = re.sub(r'<div class="slide">', '<div class="slide-page">', body_content)
    
    full_html += body_content + "\n"

full_html += "</body></html>"

# Сохраняем временный HTML для отладки
with open("/root/.openclaw/workspace/presentation_all.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("HTML собран, запускаем weasyprint...")

# Рендерим PDF
HTML(string=full_html).write_pdf("/root/.openclaw/workspace/AI_Presentation_Weasy.pdf")

size = os.path.getsize("/root/.openclaw/workspace/AI_Presentation_Weasy.pdf")
print(f"✅ PDF сохранён: AI_Presentation_Weasy.pdf — {size/1024:.0f} KB")
print(f"   Страниц: 25")
