#!/usr/bin/env python3
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

for i in range(1, 26):
    slide = prs.slides.add_slide(blank)
    png_path = f"/root/.openclaw/workspace/slides_png/slide_{i:02d}.png"
    pic = slide.shapes.add_picture(png_path, 0, 0, width=Inches(13.333))
    # Центрируем по вертикали если высота не совпадает
    if pic.height > Inches(7.5):
        pic.height = Inches(7.5)
        pic.width = Inches(7.5 * 1920 / 1080)
    print(f"✓ Слайд {i} добавлен")

prs.save('/root/.openclaw/workspace/AI_Presentation_HLD.pptx')
print(f"✅ PowerPoint сохранён: AI_Presentation_HLD.pptx")
print(f"   Слайдов: {len(prs.slides)}")
