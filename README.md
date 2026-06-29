# PPTX to Markdown (pptx-to-markdown)

> A high-fidelity PowerPoint (PPTX) to Markdown converter designed for technical presentations. Featuring automated layout alignment, LaTeX formula/table conversion, complex image cropping, and automated QA evaluation.

[![GitHub License](https://img.shields.io/github/license/simturong/pptx-to-markdown?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)](https://www.python.org/)
[![Quality Score](https://img.shields.io/badge/Quality%20Score-94%2F100-success.svg?style=flat-square)](#performance-evaluation)

---

## 📖 Table of Contents
* [Features](#features)
* [Lite vs. Pro Mode Comparison](#lite-vs-pro-mode-comparison)
* [Performance Evaluation](#performance-evaluation)
* [How to Install as a Claude Skill](#how-to-install-as-a-claude-skill)
* [Usage](#usage)
* [Directory Structure](#directory-structure)

---

## 🌟 Features

*   **Coordinate-Based Sorting**: Automatically sorts slide shapes from top-to-bottom and left-to-right (using a 0.5-inch row bucket) to preserve reading order.
*   **Complex Image Splitting**: Detects composite images (containing both figures and textual descriptions) and splits them into clean cropped images and structured tables.
*   **LaTeX Math & Markdown Table Conversion**: High-accuracy conversion of mathematical equations and grids into natively editable Markdown formulas and tables.
*   **Automated QA Evaluator**: A dedicated verification engine (`evaluate.py`) that checks document integrity, counts slide/image parity, parses table/LaTeX structures, and outputs a Quality Report.

---

## ⚡ Lite vs. Pro Mode Comparison

You can select the translation pipeline speed and fidelity according to your needs:

| Feature / Metric | 🚀 Lite Mode (Express) | 🎯 Pro Mode (Depth - Default) |
| :--- | :---: | :---: |
| **Fidelity & Information Loss** | High Loss (Composite image text is ignored) | **Zero Loss** (Crops images & extracts all text) |
| **LaTeX & Table Conversion** | Unsupported (Keeps raw image reference) | **Fully Supported** (Converts to code) |
| **Pipeline Steps** | Single Step (`prepare.py` only) | Multi-Step (Prepare $\rightarrow$ Crop $\rightarrow$ Auto QA Evaluator) |
| **Processing Speed** | **Ultra-Fast** | Moderate (Depends on image counts) |
| **Best Used For** | Text-heavy slides, quick drafts | Academic papers, hardware specs, official manuals |

---

## 📊 Performance Evaluation

Tested with an academic presentation slide deck containing 13 slides rich in mathematics, bounding boxes, and complex images.

### 📝 Final Quality Audit Report

*   **Final Score**: **94 / 100**
*   **Critical Errors**: **0**
*   **Warnings**: **27** (Translation-related or LaTeX substitutions)

```
==================================================
  Quality Evaluation Completed! Score: 94/100
  - Critical Errors: 0
  - Warnings for Review: 27
  Detailed report saved at: output/evaluation_report.md
==================================================
```
*Note: The 6-point deduction was due to high translation variance in slides 3 and 8 where academic English terms were fully localized. Manual review confirmed 100% preservation of semantics.*

---

## 🤖 How to Install as a Claude Skill

You can deploy this repository as a **Claude Skill**, allowing AI coding agents to automatically invoke this converter.

### Option A: Global Installation (Available in all workspaces)
1. Copy the `src/` scripts to your global configuration directory:
   ```bash
   mkdir -p ~/.gemini/config/skills/pptx-to-markdown/scripts
   cp src/* ~/.gemini/config/skills/pptx-to-markdown/scripts/
   ```
2. Create a `SKILL.md` in `~/.gemini/config/skills/pptx-to-markdown/SKILL.md`:
   ```markdown
   ---
   name: pptx-to-markdown
   description: High-fidelity PPTX to Markdown conversion tool with Pro/Lite modes and auto evaluation.
   ---
   # PPTX to Markdown Converter
   Run: python [skill_path]/scripts/run.py {pptx} {output} --mode [pro|lite]
   ```

### Option B: Local Installation (Workspace-only)
Create a `.agents/skills/pptx-to-markdown/` directory inside your workspace root, copy the scripts, and place the `SKILL.md` file there. The AI agent will auto-detect the skill when initialized.

---

## 🚀 Usage

### Prerequisites
Make sure you have python-pptx and Pillow installed:
```bash
python -m pip install python-pptx Pillow
```

### Run the Pipeline
```bash
# Run in Pro Mode (Recommended)
python src/run.py input/sample.pptx output --mode pro

# Run in Lite Mode (Faster, text-only extraction)
python src/run.py input/sample.pptx output --mode lite
```

---

## 📁 Directory Structure

```
.
├── src/
│   ├── run.py          # Unified entrypoint pipeline script
│   ├── prepare.py      # Core parser (extracts text and images)
│   ├── crop.py         # Sub-image cropper (Pillow-based)
│   └── evaluate.py     # Quality evaluator & reporter
├── docs/
│   ├── Plan.md         # Detailed development roadmap
│   └── examples/       # Few-shot examples for Claude Vision
├── input/              # Target PPTX location
└── output/             # Output markdown, crops, and evaluation report
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
