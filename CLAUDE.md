# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Convert PPTX files used by the smartphone hardware team into high-quality Korean Markdown documents.

---

## Project Structure

```
src/            ← Python scripts
  prepare.py    ← PPTX parsing → manifest.json + images/
  crop.py       ← Crop photo areas from composite images (v2)
  evaluate.py   ← Automated QA and validation tool (v2)
  run.py        ← Integrated entrypoint pipeline (v3)

docs/           ← Documentation & examples
  Plan.md       ← Development plan and version status
  examples/     ← Few-shot conversion examples by slide type

input/          ← PPTX files to convert
output/         ← Conversion output (result.md + images/)
CLAUDE.md       ← This guide file
```

---

## Execution Environment

- **Claude**: Desktop App (No API key) — Claude directly performs Vision analysis and Markdown generation.
- **Python**: `C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe`
- **Dependencies**: `pip install python-pptx Pillow`
- **OS**: Windows 11

> The default `python` command may point to the hermes-agent venv, so make sure to use the full path above.

---

## Workflow

### v1 (Text + Simple Images)

```
[Step 1] Run prepare.py
         C:\...\python.exe src/prepare.py input/file.pptx output

[Step 2] Run Claude
         - Read output/manifest.json
         - Perform Vision analysis on output/images/*.png
         - Generate output/result.md
```

### v2 (Including Composite Images)

```
[Step 1] Run prepare.py (Same as above)
         → manifest now includes width_px and height_px

[Step 2] Perform Claude Vision Analysis
         - Classify image types (see criteria below)
         - If complex_photo_text is found:
             a) Extract text area → Include in result.md body
             b) Estimate photo coordinates → Create output/crop_spec.json
         - Generate output/result.md

[Step 3] Run crop.py (Only if composite images exist)
         C:\...\python.exe src/crop.py output/crop_spec.json output
         → Generates images/*_crop.png
```

---

## Conversion Rules

### Language
- Translate all content into **Korean**.
- Keep proper nouns, mathematical formulas, names, and paper names in their original languages.

**Terminology Standards:**

| Original | Standard Korean Notation (Translation + English in Parentheses) |
|----------|-----------------------------------------------------------------|
| VLM | Vision-Language Model (VLM) |
| Hallucination | 환각(Hallucination) |
| Fine-tuning | 파인튜닝(Fine-tuning) |
| Benchmark | 벤치마크(Benchmark) |
| Groundtruth | 정답(Groundtruth) |
| NeurIPS / CVPR / ICCV / ECCV / AAAI | Keep original English name |

---

### Slide Structure

- Slide Title → `##` Heading
- Body Text → Paragraphs or Bullet Lists
- Element Ordering: Sort shapes based on `top` → `left` coordinates (top-to-bottom, left-to-right).

**Layout Patterns:**

| Pattern | Criteria | Action |
|------|-----------|------|
| Title Slide | Contains only title + presenter info | `##` Title + presenter info |
| 2-Column Layout | Divided into left < 360pt / left ≥ 360pt | HTML `<table>` with 2 columns |
| Text Only | No images | Headings + bullet lists |
| Image Grid | 3 or more images | Process each image individually |
| Empty Shapes | No text/images found | Embedded inside images → Vision required |

---

### Image Processing

**Classification Criteria:**

| Type | Key | Criteria | Action |
|------|---------|-----------|------|
| Simple Photo | `simple_photo` | No text, natural image | Keep image + Description ≤ 3 lines |
| Simple Diagram | `simple_diagram` | Mostly shapes/arrows, ≤ 10% text | Keep image + Description ≤ 3 lines |
| Text-Heavy Image | `complex_text_heavy` | ≥ 50% text | Extract text → Structure as Table/List |
| **Photo+Text Composite** | **`complex_photo_text`** | ≥ 30% photo and text in parallel | **Crop photo + Separate text** |
| Mathematical Equation | `formula_image` | Mostly formulas/equations | Convert to LaTeX (`$$...$$` or `$ ... $`) |
| Table Image | `table_image` | Clear table with cell borders | Convert to Markdown Table |

**Simple Image Output Format:**
```markdown
![Concise alt text](images/filename.png)

> Key summary within 3 lines.
```

**complex_photo_text Processing Procedure:**
1. Extract text from the text area and include it in the result.md body as a table or list.
2. Estimate the photo area coordinates as ratios (0.0 to 1.0).
3. Create `output/crop_spec.json` (format below).
4. Reference the cropped filename in result.md (`images/XX_YY_crop.png`).

**crop_spec.json Format:**
```json
[
  {
    "source": "images/02_01.png",
    "output": "images/02_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "Extracted text content from text area (for reference)"
  }
]
```

---

## Prohibited Actions
- Do not write image analysis results only in alt text — always reflect them in the body text.
- If classification for `complex_photo_text` is ambiguous, ask the user first.
- Do not change the workflow rules arbitrarily.

---

## Self-Improvement Guidelines (Preventing Evaluation Errors)
To prevent critical errors or warnings from the quality evaluator (`evaluate.py`), strictly adhere to the following principles:

1. **LaTeX Equation Alternative Rule**:
   - When replacing equation images with Markdown equations, ensure there is at least one pair of properly closed LaTeX symbols (`$$...$$` or `$ ... $`) in the slide text so the evaluator can detect the equation replacement.
2. **Table Image Alternative Rule**:
   - When converting table images to Markdown tables, ensure the number of columns in the header and divider lines (`--|--`) match exactly to avoid structure mismatch errors.
3. **Text-Heavy Image Alternative Rule**:
   - When replacing text-heavy images (`complex_text_heavy`), use Markdown tables (e.g., English-Korean contrast tables) rather than simple text listings to maximize readability and satisfy the evaluator.
4. **Glossary and Keyword Preservation**:
   - Strictly follow the [terminology standards](file:///e:/Tak/Gemini/pptx-to-markdown/CLAUDE.md#l80) and include English terms in parentheses (e.g., *환각(Hallucination)*) to minimize keyword omission detection by the evaluator.

---

## Output Structure

```
output/
├── result.md          ← Final Korean Markdown document
├── crop_spec.json     ← (v2) Coordinates for composite image cropping
└── images/
    ├── 01_01.png
    ├── 02_01.png
    └── 02_01_crop.png ← (v2) Result of crop.py
```

---

## Development & Execution Environment (v3 Integrated)

### Dependency & Environment Verification
```bash
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/prepare.py --check
```

### Pipeline Execution Modes
Run the pipeline with the appropriate execution mode:

1. **🚀 Speed Mode (Lite)**: Faster execution focusing on parsing and resource extraction.
2. **🎯 Precision Mode (Pro)**: Detailed execution including composite cropping, Markdown structuring, and automated QA evaluation (Default).

```bash
# 1. Speed Mode (Lite)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/run.py input/file.pptx output --mode lite

# 2. Precision Mode (Pro) (Default)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/run.py input/file.pptx output --mode pro
```

### Run Standalone Modules Individually (If needed)
```bash
# Parse and deconstruct PPTX
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/prepare.py input/file.pptx output

# Crop composite images
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/crop.py output/crop_spec.json output

# Automated quality evaluation
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/evaluate.py output/manifest.json output/result.md output
```

---

## Script Core Logic

### prepare.py
- Shape sorting: `sort_key = (round(top / 457200), left)` — Row buckets of 0.5 inches.
- Image extraction: `shape.image.blob` → `images/slideNumber_sequence.ext`
- Includes pixel size (`width_px`, `height_px`) and display size (`display_width_pt`, `display_height_pt`) in the manifest.

### crop.py
- Translates `region_pct` (0.0~1.0) into pixel coordinates and crops using Pillow `.crop()`.
- Clamps boundaries to prevent coordinates out of range.
- Output: `images/XX_YY_crop.png`

---

## Few-shot Examples

Refer to the `docs/examples/` folder:
- `01_title_slide/` — Title slide example
- `02_two_column/` — 2-column layout example
- `03_complex_image/` — Composite image (photo+text) example

Each folder contains a `manifest.json` (input) + `output.md` (expected output) pair.

---

## Quality Improvement History

### v1 (2026-06-29)
- Established image processing rules, LaTeX formula conversion, and Markdown table conversion.
- Implemented Korean translation rules with English term inclusion, resolved Python path issues.

### v2 (2026-06-30)
- prepare.py: Added pixel sizes to manifest.
- crop.py: Added composite image photo cropping.
- Integrated rules.json into CLAUDE.md as a single source of truth.
- Restructured repository layout into src/ and docs/.
- evaluate.py: Implemented automated QA to detect omissions and validate Markdown syntax.
- Tested composite image cropping (02_01.png) and Markdown integration on sample.pptx.

### v3 (2026-06-30)
- run.py: Developed integrated entrypoint script with CLI arguments (`--mode pro/lite`).
- Passed integration tests for Speed and Precision pipelines.
