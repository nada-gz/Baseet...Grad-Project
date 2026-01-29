# Manim Rendering Error Analysis

## Problem Summary

The pipeline generates educational videos but **some segments fail to render** after all 3 retry attempts. The failures are caused by **LLM-generated Manim code containing logic errors** that even the code-fixing agent cannot resolve.

---

## Root Causes Identified

### 1. **Grid Arrangement Error** (Segment 1)
**Error:**
```
ValueError: Too few rows and columns to fit all submobjects.
```

**Problematic Code:**
```python
ingredients = VGroup(sun, sun_label, water, water_label, co2, co2_label)  # 6 elements
ingredients.arrange_in_grid(rows=1, cols=3, buff=1)  # Only fits 3 elements
```

**Why it happens:**
- The LLM creates a VGroup with 6 items (3 shapes + 3 labels)
- Then tries to arrange them in a 1×3 grid (which only holds 3 items)
- Manim throws a ValueError

**Fix:** Either use `rows=2, cols=3` or create separate VGroups.

---

### 2. **Undefined Color Error** (Segment 3)
**Error:**
```
NameError: name 'BROWN' is not defined
```

**Problematic Code:**
```python
stem = Line(start=root.get_top(), end=root.get_top() + UP*2, color=BROWN)
```

**Why it happens:**
- Manim doesn't have a `BROWN` constant
- Valid Manim colors: RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, PINK, WHITE, GRAY, BLACK
- The LLM hallucinates color names

**Fix:** Use valid Manim colors or custom RGB values like `rgb_to_color([0.6, 0.3, 0.1])`

---

### 3. **Likely Pattern for Segment 2**
Based on the error pattern `Write(Text('Sunlight: The Power Source')):   0%|   | 0/30`, Segment 2 probably had:
- **Syntax errors** in the generated code
- **Missing imports** or incorrect method calls
- **Invalid text formatting** (special characters)
- Or similar **logic errors** that prevent initial rendering

---

## Why the Retry Mechanism Fails

The current fix attempt:
```python
code = await fix_code(self.qwen_client, code, error[:300])  # Only 300 chars of error
```

**Problems:**
1. **Truncated error messages** - Only first 300 characters sent to LLM
2. **Context loss** - The LLM doesn't understand Manim's API limitations
3. **Random fixes** - The fixer might introduce new errors
4. **No validation** - No syntax checking before re-attempting render

---

## Impact

- Videos are generated **without failed segments**
- User sees **partial content** (in your case: intro + segments 1, 3, 4, but missing segment 2)
- **Time wasted** on 3 failed render attempts (30-45 seconds per failed segment)

---

## Recommendations

### **Short-term Fix (Quick)**
1. ✅ **Improve LLM prompts** to avoid common errors
2. ✅ **Add code validation** before rendering
3. ✅ **Increase error context** sent to fixer (from 300 to 1000+ chars)

### **Medium-term Fix (Better)**
1. **Add a code validator** that checks for:
   - Valid Manim color names
   - Grid arrangement math (rows × cols ≥ elements)
   - Required imports
   - Basic syntax errors
   
2. **Improve the code_fixer prompt** with:
   - Specific Manim API knowledge
   - Common error patterns
   - Valid color names list

### **Long-term Fix (Best)**
1. **Fine-tune the LLM** on correct Manim code examples
2. **Use RAG** with Manim documentation
3. **Implement code templates** for common visualizations
4. **Add unit tests** for generated code before rendering

---

## Files for Reference

Debug files saved to:
- `outputs/final/[session_id]/debug/segment_X_attempt_1_code.py` - Generated code
- `outputs/final/[session_id]/debug/segment_X_attempt_1_error.txt` - Full error traceback

This enhancement (added in pipeline_v2.py) now captures full error details for easier debugging! 🎉
