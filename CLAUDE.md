# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 목적

스마트폰 하드웨어팀에서 사용하는 PPTX 파일을 고품질 한국어 Markdown으로 변환한다.

---

## 프로젝트 구조

```
src/            ← Python 스크립트
  prepare.py    ← PPTX 파싱 → manifest.json + images/
  crop.py       ← 복합 이미지 사진 영역 크롭 (v2)

docs/           ← 문서 & 예시
  Plan.md       ← 개발 계획 및 버전 현황
  examples/     ← 슬라이드 유형별 Few-shot 변환 예시

input/          ← 변환할 PPTX 파일
output/         ← 변환 결과 (result.md + images/)
CLAUDE.md       ← 이 파일
```

---

## 실행 환경

- **Claude**: 데스크탑 앱 (API 키 없음) — Claude가 직접 Vision 분석 및 MD 생성 수행
- **Python**: `C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe`
- **의존성**: `pip install python-pptx Pillow`
- **OS**: Windows 11

> `python` 명령은 hermes-agent venv를 가리키므로 반드시 위 전체 경로 사용

---

## 워크플로우

### v1 (텍스트 + 단순 이미지)

```
[Step 1] prepare.py 실행
         C:\...\python.exe src/prepare.py input/파일.pptx output

[Step 2] Claude가 직접 실행
         - output/manifest.json 읽기
         - output/images/*.png Vision 분석
         - output/result.md 생성
```

### v2 (복합 이미지 포함)

```
[Step 1] prepare.py 실행 (동일)
         → manifest에 width_px, height_px 포함됨

[Step 2] Claude Vision 분석
         - 이미지 유형 분류 (아래 기준 참고)
         - complex_photo_text 발견 시:
             a) 텍스트 영역 추출 → result.md 본문에 포함
             b) 사진 좌표 추정 → output/crop_spec.json 생성
         - output/result.md 생성

[Step 3] crop.py 실행 (복합 이미지가 있을 때만)
         C:\...\python.exe src/crop.py output/crop_spec.json output
         → images/*_crop.png 생성
```

---

## 변환 규칙

### 언어
- 모든 내용을 **한국어**로 변환
- 고유명사·수식·인명·논문명은 원문 유지

**용어 표기 기준:**

| 원문 | 표기 |
|------|------|
| VLM | Vision-Language Model (VLM) |
| Hallucination | 환각(Hallucination) |
| Fine-tuning | 파인튜닝(Fine-tuning) |
| Benchmark | 벤치마크(Benchmark) |
| Groundtruth | 정답(Groundtruth) |
| NeurIPS / CVPR / ICCV / ECCV / AAAI | 원문 그대로 유지 |

---

### 슬라이드 구조

- 슬라이드 제목 → `##` 헤딩
- 본문 텍스트 → 단락 또는 불릿 리스트
- 요소 배치 순서: shape의 `top` → `left` 좌표 기준 위→아래, 좌→우

**레이아웃 패턴:**

| 패턴 | 판별 기준 | 처리 |
|------|-----------|------|
| 제목 슬라이드 | 제목 + 발표자 정보만 | `##` + 발표자 정보 |
| 2단 레이아웃 | left < 360pt / left ≥ 360pt 두 구역 | HTML `<table>` 2컬럼 |
| 텍스트만 | 이미지 없음 | 헤딩 + 불릿 리스트 |
| 이미지 그리드 | 이미지 3개 이상 | 각 이미지 개별 처리 |
| 텍스트/이미지 없음 | shape 비어있음 | 이미지 내부에 내장 → Vision 필수 |

---

### 이미지 처리

**분류 기준:**

| 유형 | 분류 키 | 판별 기준 | 처리 |
|------|---------|-----------|------|
| 단순 사진 | `simple_photo` | 텍스트 없음, 자연 이미지 | 이미지 유지 + 설명 ≤3줄 |
| 단순 다이어그램 | `simple_diagram` | 도형/화살표 위주, 텍스트 10% 이하 | 이미지 유지 + 설명 ≤3줄 |
| 텍스트 주도 이미지 | `complex_text_heavy` | 텍스트 50% 이상 | 텍스트 추출 → 표/리스트 구조화 |
| **사진+텍스트 혼합** | **`complex_photo_text`** | 사진·텍스트 각각 30% 이상 병렬 | **크롭 + 텍스트 분리** |
| 수식 이미지 | `formula_image` | 수식·방정식 위주 | LaTeX (`$$...$$`) 변환 |
| 표 이미지 | `table_image` | 셀 경계선 명확한 표 형태 | 마크다운 표 변환 |

**단순 이미지 출력 형식:**
```markdown
![간결한 alt text](images/파일명.png)

> 핵심 내용 3줄 이내.
```

**complex_photo_text 처리 절차:**
1. 텍스트 영역 내용 추출 → result.md 본문에 표/리스트로 포함
2. 사진 영역 좌표를 0.0~1.0 비율로 추정
3. `output/crop_spec.json` 생성 (아래 형식)
4. result.md 이미지 경로는 크롭 파일명 사용 (`images/XX_YY_crop.png`)

**crop_spec.json 형식:**
```json
[
  {
    "source": "images/02_01.png",
    "output": "images/02_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "텍스트 영역 추출 내용 (참고용)"
  }
]
```

---

### 금지 사항
- 이미지 분석 결과를 alt text에만 묻지 않는다 — 반드시 본문에 반영
- `complex_photo_text` 판단 불명확 시 사용자에게 먼저 확인
- 처리 방식 임의 변경 금지

---

### 변환 자가 개선 지침 (품질 평가 에러 방지)
향후 Claude가 직접 변환을 수행할 때 품질 평가기(`evaluate.py`)에서 치명적 오류나 경고를 받지 않도록 다음 원칙을 철저히 준수해야 합니다.

1. **LaTeX 수식 이미지 대체 규칙**:
   - 수식 이미지를 마크다운 수식으로 대체할 때, 평가 스크립트가 이를 '수식 대체'로 감지할 수 있도록 해당 슬라이드 본문에 반드시 올바르게 닫힌 LaTeX 기호(`$$...$$` 또는 `$ ... $`)가 최소 1쌍 이상 온전하게 작성되어야 합니다.
2. **표 이미지 대체 규칙**:
   - 표 형상 이미지(table_image)를 마크다운 텍스트 표로 변환해 넣을 때, 헤더 컬럼 수와 구분선(`--|--`)의 컬럼 수가 정확히 일치하도록 엄격히 검증하여 표 구조 불일치 에러를 방지하십시오.
3. **텍스트 중심 이미지 대체 규칙**:
   - 영어 문장들이 나열된 텍스트 이미지(`complex_text_heavy`)를 치환할 때는 단순 텍스트 나열보다 영한 대조표 등 **마크다운 표(Table)** 포맷을 활용하십시오. 가독성이 극대화될 뿐 아니라 평가기에서 정당한 대체로 자동 인정됩니다.
4. **용어 사전 및 번역 키워드 보존**:
   - 제목 및 본문 번역 시 전문 학술/기술 용어는 [언어 표기 기준](file:///e:/Tak/Cluade/PPTX%20to%20MD/CLAUDE.md#L80)을 반드시 준수하고 영문 고유명사는 괄호 병기(예: *환각(Hallucination)*)하여 평가기의 키워드 누락 감지율을 사전에 최소화하십시오.

---

## 출력 구조

```
output/
├── result.md          ← 최종 한국어 마크다운
├── crop_spec.json     ← (v2) 복합 이미지 크롭 스펙
└── images/
    ├── 01_01.png
    ├── 02_01.png
    └── 02_01_crop.png ← (v2) crop.py 결과
```

---

## 개발 및 실행 환경 (v3 통합)

### 의존성 및 환경 확인
```bash
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/prepare.py --check
```

### 파이프라인 실행 모드
사용자는 목적에 맞게 두 가지 변환 모드를 선택하여 변환기를 실행할 수 있습니다.

1. **🚀 신속 모드 (Lite Mode)**: 파싱 및 단순 리소스 추출 위주의 빠른 속도 지향 모드
2. **🎯 정밀 모드 (Pro Mode)**: 복합 이미지 크롭, 마크다운 표 구조화 및 자동 품질 평가를 거치는 정밀 지향 모드 (기본값)

```bash
# 1. 신속 모드 (Lite) 실행
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/run.py input/파일.pptx output --mode lite

# 2. 정밀 모드 (Pro) 실행 (기본값)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/run.py input/파일.pptx output --mode pro
```

### 서브 모듈 개별 실행 (필요시)
```bash
# PPTX 파싱 및 분해
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/prepare.py input/파일.pptx output

# 복합 이미지 크롭
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/crop.py output/crop_spec.json output

# 변환 품질 자동 평가
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe src/evaluate.py output/manifest.json output/result.md output
```

---

## 스크립트 핵심 로직

### prepare.py
- shape 정렬: `sort_key = (round(top / 457200), left)` — 0.5인치 단위 행 버킷
- 이미지 추출: `shape.image.blob` → `images/슬라이드번호_순번.ext`
- (v2) Pillow로 `width_px`, `height_px` 추출 → manifest 포함
- (v2) PPTX 표시 크기 `display_width_pt`, `display_height_pt` 포함

### crop.py
- `crop_spec.json`의 `region_pct` (0.0~1.0) → 픽셀 좌표 변환 후 Pillow `.crop()`
- 경계 클램프 처리 (이미지 밖 좌표 자동 보정)
- 결과: `images/XX_YY_crop.png`

---

## Few-shot 예시

`docs/examples/` 폴더 참고:
- `01_title_slide/` — 제목 슬라이드
- `02_two_column/` — 2단 레이아웃
- `03_complex_image/` — 복합 이미지 (사진+텍스트)

각 폴더: `manifest.json` (입력) + `output.md` (기대 출력) 쌍으로 구성.

---

## 품질 개선 이력

### v1 (2026-06-29)
- 이미지 처리 규칙 확립, LaTeX 수식 변환, 마크다운 표 변환
- 한국어 번역 + 기술 용어 병기 규칙, Python 경로 이슈 해결

### v2 (2026-06-30)
- prepare.py: 픽셀 크기 manifest 추가
- crop.py 신규: 복합 이미지 사진 영역 크롭
- rules.json → CLAUDE.md 통합 (단일 지침 파일)
- src/ / docs/ 구조로 재편
- evaluate.py 신규: 누락 감지 및 마크다운 정합성 검증용 품질 평가 자동화 시스템 구축
- sample.pptx 대상 복합 이미지(02_01.png) 크롭 테스트 및 최종 마크다운 구조화 융합 완료

### v3 (2026-06-30)
- run.py 신규: CLI 인자(--mode pro/lite)를 지원하는 단일 진입점 파이프라인 마스터 스크립트 개발
- 신속 모드(Lite) 및 정밀 모드(Pro) 실행 가이드라인 제공 및 연동 테스트 통과
