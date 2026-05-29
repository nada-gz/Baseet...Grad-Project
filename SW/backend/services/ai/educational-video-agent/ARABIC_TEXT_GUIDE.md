# Arabic Text Support in Manim

## Overview
This project currently uses **English text** in Manim animations with **Arabic audio narration**. 

If you want to add Arabic text to the animations, here are your options:

---

## Option 1: ManimArabic (Recommended for Full Arabic Support)

**ManimArabic** is a dedicated extension for Manim that provides:
- ✅ Right-to-Left (RTL) text rendering
- ✅ Arabic mathematical notation
- ✅ Proper ligature handling
- ✅ Arabic-specific animations

### Installation:
```bash
pip install manim-arabic
```

### GitHub Repository:
https://github.com/MoaydShagaf/ManimArabic

### Usage Example:
```python
from manim import *
from manim_arabic import ArabicText

class ArabicScene(Scene):
    def construct(self):
        # Arabic text with RTL support
        text = ArabicText("مرحباً بكم في الرياضيات")
        self.play(Write(text))
        self.wait(2)
```

---

## Option 2: Built-in Pango Support (Basic Arabic)

Manim's `Text` class uses Pango, which has basic Arabic support:

```python
from manim import *

class BasicArabicScene(Scene):
    def construct(self):
        # Simple Arabic text (may have RTL issues)
        text = Text("النص العربي", font="Arial")
        self.play(Write(text))
        self.wait(2)
```

**Limitations:**
- ⚠️ RTL direction may not work correctly with Write() animation
- ⚠️ Ligatures might cause issues
- ⚠️ Limited control over Arabic-specific typography

---

## Option 3: LaTeX with XeLaTeX (For Math + Arabic)

For mathematical expressions with Arabic:

```python
from manim import *

class ArabicMathScene(Scene):
    def construct(self):
        # Configure LaTeX for Arabic
        template = TexTemplate()
        template.add_to_preamble(r"\usepackage{polyglossia}")
        template.add_to_preamble(r"\setmainlanguage{arabic}")
        template.add_to_preamble(r"\newfontfamily\arabicfont{Noto Naskh Arabic}")
        
        # Arabic math text
        text = Tex(r"المعادلة: $F = ma$", tex_template=template)
        self.play(Write(text))
```

**Requirements:**
- XeLaTeX compiler installed
- Arabic fonts (e.g., Noto Naskh Arabic)

---

## Current Project Setup

**Status:** Using English text in animations + Arabic audio narration

**Why?**
- ✅ Simpler implementation
- ✅ No RTL complexity
- ✅ Works reliably across all platforms
- ✅ Audio provides Arabic content

**To Enable Arabic Text:**
1. Install `manim-arabic`: `pip install manim-arabic`
2. Update `llm/code_generator.py` to generate Arabic text
3. Modify prompts to request Arabic text in animations
4. Test RTL rendering and animations

---

## Recommendation

For **elementary school educational videos**, the current approach (English text + Arabic audio) is actually **beneficial** because:
- Students learn English technical terms
- Simpler visual layout (LTR is easier to animate)
- Audio provides full Arabic explanation
- No technical complexity with RTL rendering

If you want to add Arabic text for specific elements (like titles), use **ManimArabic** for best results.
