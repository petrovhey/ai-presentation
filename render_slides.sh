#!/bin/bash
cd /root/.openclaw/workspace/slides_html
mkdir -p ../slides_png
for i in $(seq -w 1 25); do
    google-chrome --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars --screenshot=../slides_png/slide_${i}.png "file:///root/.openclaw/workspace/slides_html/slide_${i}.html" 2>/dev/null
    echo "✓ slide_${i}.png"
done
echo "Все слайды отрендерены"
