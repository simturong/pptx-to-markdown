---
name: pptx-to-markdown
description: 스마트폰 H/W팀 PPTX 문서를 고품질 한국어 Markdown으로 변환 및 정합성 검증을 수행하는 스킬 (Lite/Pro 모드 지원)
---

# PPTX to Markdown Skill

This skill automates the process of converting PowerPoint presentations (PPTX) into high-fidelity Markdown files.

## 🚀 Execution Guide (실행 가이드)

The skill features a unified entrypoint script located at `scripts/run.py` within the skill directory.

### Commands (실행 명령어)
*   **Pro Mode (🎯 정밀 모드 - 기본값)**: Performs layout sorting, composite image splitting, and quality validation.
    ```bash
    python {skill_dir}/scripts/run.py <pptx_file> [output_dir] --mode pro
    ```
*   **Lite Mode (🚀 신속 모드)**: Fast text and image extraction only.
    ```bash
    python {skill_dir}/scripts/run.py <pptx_file> [output_dir] --mode lite
    ```

---

## 🛠️ Instructions for Claude (클로드가 수행할 지침)

When you receive a request to convert a PPTX file using this skill, follow these steps:

1.  **Run Pipeline (1단계: 파이프라인 구동)**:
    Execute the python script in either `lite` or `pro` mode (default: `pro`).
2.  **Generate Markdown (2단계: 마크다운 변환)**:
    Read the parsed `manifest.json` and output images, then generate the final `result.md` following these rules:
    *   **Translation**: Translate all slide text to Korean. For technical terms (e.g., VLM, Fine-tuning), append original English terms in parentheses (e.g., *시각-언어 모델(VLM)*).
    *   **Complex Images**: If `complex_photo_text` (combination of figures and text) is found, extract the text into a Markdown table, crop the image using `crop_spec.json`, and reference the cropped image (`*_crop.png`) in the markdown.
    *   **LaTeX Math**: Convert mathematical equations into LaTeX syntax (`$$` or `$`).
    *   **Tables**: Re-render slide tables using Markdown table syntax, ensuring column count matches the divider exactly.
3.  **Evaluate Parity (3단계: 품질 보증 검증)**:
    Run the `evaluate.py` module (included in `run.py --mode pro` execution) to ensure the `result.md` has no missing slides or syntax errors.
