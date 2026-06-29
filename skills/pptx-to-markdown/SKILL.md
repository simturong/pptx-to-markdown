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

### 1단계: 파이프라인 구동 (Run Pipeline)
먼저 사용자의 모드 선택(Lite/Pro)에 따라 파이썬 스크립트를 구동하십시오.
*   **Pro 모드 구동 시**: `run.py`를 통해 파싱(`prepare.py`), 크롭(`crop.py`), 품질 평가(`evaluate.py`)가 연속으로 연동됩니다.

### 2단계: 고품질 마크다운 문서 생성 (Generate Markdown)
파싱된 `manifest.json` 정보 및 `output/images/` 리소스를 직접 읽고 다음 지침들을 적용하여 [result.md](file:///output/result.md)를 완성하십시오.

#### A. 언어 및 기술 용어 번역 규칙
*   모든 슬라이드 본문은 **한국어**로 정제하여 번역하되, 아래의 고유 학술/기술 용어 표기 기준을 철저히 준수하십시오.

| 원문 | 표기 기준 (번역 + 영문 병기) |
| :--- | :--- |
| VLM | Vision-Language Model (VLM) |
| Hallucination | 환각(Hallucination) |
| Fine-tuning | 파인튜닝(Fine-tuning) |
| Benchmark | 벤치마크(Benchmark) |
| Groundtruth | 정답(Groundtruth) |
| NeurIPS / CVPR / ICCV / ECCV / AAAI | 번역 없이 원어 유지 |

#### B. 슬라이드 구조 및 레이아웃 처리 규칙
*   요소 배치 순서는 shape의 `top` $\rightarrow$ `left` 좌표 기준(위$\rightarrow$아래, 좌$\rightarrow$우)으로 자연스러운 읽기 흐름을 복원합니다.
*   **2단 레이아웃**: left 좌표 기준으로 구역이 나뉠 때(예: left < 360pt / left $\ge$ 360pt)는 HTML `<table>`을 사용하여 2컬럼 레이아웃으로 변환합니다.

#### C. 이미지 유형별 분기 처리 규칙
*   **단순 사진 (`simple_photo`) / 다이어그램 (`simple_diagram`)**:
    *   마크다운 이미지 경로 유지 및 이미지 하단에 `> 핵심 설명(3줄 이내)`를 배치합니다.
*   **수식 이미지 (`formula_image`)**:
    *   이미지 참조를 생략하고, 본문에 정확히 매칭된 LaTeX 디스플레이 수식(`$$...$$`) 또는 인라인 수식(`$...$`) 기호로 수식을 텍스트화하십시오.
*   **표 이미지 (`table_image`)**:
    *   이미지 참조를 생략하고, 마크다운 표 문법(`|` 컬럼 분할 및 `--|--` 구분선)을 엄격히 사용하여 정렬된 텍스트 표로 변환하십시오.
*   **복합 이미지 (`complex_photo_text` — 사진과 텍스트의 병렬 결합)**:
    1.  텍스트 영역의 글자를 모두 추출해 마크다운 본문에 표/리스트 구조로 포함하십시오.
    2.  사진 영역의 좌표를 0.0~1.0 비율로 추정하여 `output/crop_spec.json`에 기록하십시오.
    3.  `crop.py`를 통해 생성된 잘라낸 이미지 경로(`images/*_crop.png`)를 마크다운에 참조시키십시오.

#### D. 금지 사항
*   이미지 분석 내용을 alt text 안에만 작성하지 마십시오. 반드시 마크다운 본문에 반영되어야 합니다.
*   `complex_photo_text` 판별이 불분명할 경우, 임의로 변환하지 말고 사용자에게 먼저 확인하십시오.

### 3단계: 품질 보증 검증 (QA & Evaluation)
변환 완료 후 `evaluate.py` 자동 품질 평가 도구를 실행하여, 누락된 슬라이드가 없으며 수식 및 표 구조가 정합성을 유지하는지 확인하고, 최종 품질 점수 90점 이상을 달성하도록 유도하십시오.
