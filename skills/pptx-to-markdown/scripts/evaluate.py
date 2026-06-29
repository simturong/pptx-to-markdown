"""
Automated Quality Evaluation Script — v2
- Compares manifest.json with result.md to validate conversion completeness and detect omissions per slide.
- Generates an evaluation report (evaluation_report.md).

Usage:
  python src/evaluate.py output/manifest.json output/result.md output
"""

import json
import re
import sys
from pathlib import Path


def evaluate_quality(manifest_path: str, result_path: str, output_dir: str):
    manifest_path = Path(manifest_path)
    result_path = Path(result_path)
    output_dir = Path(output_dir)

    if not manifest_path.exists():
        print(f"[Error] manifest.json file not found: {manifest_path}")
        sys.exit(1)

    if not result_path.exists():
        print(f"[Error] result.md file not found: {result_path}")
        sys.exit(1)

    # 1. Read files
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Error] Failed to read manifest.json: {e}")
        sys.exit(1)

    try:
        result_text = result_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[Error] Failed to read result.md: {e}")
        sys.exit(1)

    # Split slides by '\n---' divider
    slides_md = [s.strip() for s in result_text.split("\n---") if s.strip()]
    
    report = []
    report.append("# Auto Evaluation Report")
    report.append(f"- **Target File**: `{result_path.name}`")
    report.append(f"- **Reference File**: `{manifest_path.name}`\n")
    
    report.append("## 1. Summary")
    
    total_slides_manifest = len(manifest)
    total_slides_md = len(slides_md)
    
    report.append(f"- manifest.json slides: **{total_slides_manifest}**")
    report.append(f"- result.md slides: **{total_slides_md}**")
    
    slide_count_match = total_slides_manifest == total_slides_md
    report.append(f"- Slide count match: {'✅ Match' if slide_count_match else '❌ Mismatch (validation required)'}")
    
    errors = []
    warnings = []
    slide_reports = []
    
    # 2. Detailed validation per slide (1-indexed)
    for i, slide_data in enumerate(manifest, start=1):
        slide_idx = slide_data["slide"]
        elements = slide_data["elements"]
        
        slide_errors = []
        slide_warnings = []
        
        # Map 1-indexed to slides_md index (0-indexed)
        md_content = ""
        if i - 1 < len(slides_md):
            md_content = slides_md[i - 1]
        
        # Check slide title
        title_elements = [el for el in elements if el["type"] == "title"]
        for te in title_elements:
            clean_title = re.sub(r'[\*\#\_]', '', te["text"]).strip()
            # Extract keywords to check if they are in md_content
            words = [w for w in re.split(r'\s+', clean_title) if len(w) >= 2]
            matched_words = [w for w in words if w.lower() in md_content.lower()]
            
            if words and len(matched_words) / len(words) < 0.3:
                has_header = md_content.startswith("#") or "\n#" in md_content
                if not has_header:
                    slide_errors.append("Slide title header (# or ##) not identified in the body")
                else:
                    # Downgrade to warning since it is likely translated into Korean
                    slide_warnings.append(f"Title assumed translated: Original '{clean_title[:30]}...' -> Korean header matching")

        # Check images
        image_elements = [el for el in elements if el["type"] == "image"]
        md_images = re.findall(r'!\[.*?\]\((images/.*?)\)', md_content)
        
        # Check if LaTeX math or Markdown table exists in slide
        has_latex = "$$" in md_content or len(re.findall(r'(?<!\$)\$(?!\$)', md_content)) >= 2
        has_table = "|" in md_content and "-" in md_content
        
        for img_el in image_elements:
            orig_path = img_el["path"]
            orig_name = Path(orig_path).stem  # e.g., '05_01'
            
            # Check if this image is referenced in md_content (also permits cropped image name matching)
            found = False
            for md_img in md_images:
                if orig_name in md_img:
                    found = True
                    local_img_path = output_dir / md_img
                    if not local_img_path.exists():
                        slide_errors.append(f"Referenced image file not found: `{md_img}`")
                    break
            
            if not found:
                # Check if image was replaced by math/table
                if has_latex:
                    slide_warnings.append(f"Image `{orig_path}` is assumed to be replaced by a LaTeX equation")
                elif has_table:
                    slide_warnings.append(f"Image `{orig_path}` is assumed to be replaced by a Markdown table")
                else:
                    slide_errors.append(f"Missing image: original `{orig_path}` is not included in the Markdown")

        # Check text (Keyword preservation analysis)
        text_elements = [el for el in elements if el["type"] == "text"]
        all_orig_text = " ".join([te["text"] for te in text_elements])
        
        orig_words = list(set(re.findall(r'[a-zA-Z가-힣]{3,}', all_orig_text)))
        if orig_words:
            matched = 0
            for w in orig_words:
                if w.lower() in md_content.lower():
                    matched += 1
            
            match_ratio = matched / len(orig_words)
            if match_ratio < 0.2 and len(all_orig_text.strip()) > 30:
                slide_warnings.append(f"Text keyword preservation rate is very low ({match_ratio:.1%}). Content omission check required.")

        # Validate Markdown syntax: LaTeX double dollars
        raw_double_dollars = len(re.findall(r'\$\$', md_content))
        if raw_double_dollars % 2 != 0:
            slide_errors.append("LaTeX display math symbol `$$` is unmatched (odd count)")
            
        # Validate Markdown syntax: LaTeX single dollars
        raw_single_dollars = len(re.findall(r'(?<!\$)\$(?!\$)', md_content))
        if raw_single_dollars % 2 != 0:
            slide_warnings.append("LaTeX inline math symbol `$` count is odd (may be currency notation)")

        # Validate Markdown syntax: Table columns
        lines = md_content.split("\n")
        for idx_line, line in enumerate(lines):
            if "|" in line and idx_line + 1 < len(lines):
                next_line = lines[idx_line + 1]
                if "|" in next_line and "-" in next_line and not re.search(r'[a-zA-Z가-힣]', next_line):
                    cols_header = len(line.split("|"))
                    cols_divider = len(next_line.split("|"))
                    if cols_header != cols_divider:
                        slide_errors.append(f"Markdown table structure mismatch (row {idx_line+1}): Header columns ({cols_header}) != Divider columns ({cols_divider})")

        # Record slide report
        slide_reports.append({
            "slide": slide_idx,
            "errors": slide_errors,
            "warnings": slide_warnings,
            "status": "❌ Error" if slide_errors else ("⚠️ Warning" if slide_warnings else "✅ Pass")
        })
        
        errors.extend([f"Slide {slide_idx}: {err}" for err in slide_errors])
        warnings.extend([f"Slide {slide_idx}: {war}" for war in slide_warnings])

    # 3. Calculate score
    # Errors: -10 points each
    # Serious warnings (low keyword preservation): -3 points each
    # Formatting/replacement warnings: 0 points (no penalty)
    deductible_warnings = 0
    for war in warnings:
        if "preservation rate is very low" in war:
            deductible_warnings += 1
            
    score = 100 - (len(errors) * 10) - (deductible_warnings * 3)
    score = max(0, score)
    
    report.append(f"- **Final conversion quality score**: **{score}/100**")
    report.append(f"  - (Deductible warnings: {deductible_warnings} / Informational warnings: {len(warnings) - deductible_warnings})\n")
    
    # 4. Record details
    report.append("## 2. Discovered Issues")
    if errors:
        report.append("### 🔴 Critical Errors (Errors)")
        for err in errors:
            report.append(f"- {err}")
    else:
        report.append("- No critical errors ✅")
        
    report.append("")
    if warnings:
        report.append("### 🟡 Warnings (Warnings)")
        for war in warnings:
            report.append(f"- {war}")
    else:
        report.append("- No warnings ✅")
        
    report.append("\n## 3. Slide Status")
    report.append("| Slide | Status | Errors | Warnings |")
    report.append("| :--- | :--- | :--- | :--- |")
    for sr in slide_reports:
        report.append(f"| Slide {sr['slide']} | {sr['status']} | {len(sr['errors'])} | {len(sr['warnings'])} |")

    # Save report file
    report_text = "\n".join(report)
    report_file = output_dir / "evaluation_report.md"
    report_file.write_text(report_text, encoding="utf-8")
    
    # Print to console
    print(f"==================================================")
    print(f"  Quality Evaluation Completed! Score: {score}/100")
    print(f"  - Critical Errors: {len(errors)}")
    print(f"  - Warnings: {len(warnings)}")
    print(f"  Detailed report saved to:")
    print(f"    {report_file.absolute()}")
    print(f"==================================================")
    
    if errors:
        return False
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python evaluate.py <manifest.json> <result.md> [output_dir]")
        sys.exit(1)
        
    man_file = sys.argv[1]
    res_file = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    
    evaluate_quality(man_file, res_file, out_dir)
