# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 목적

스마트폰 하드웨어팀에서 사용하는 PPTX 파일을 고품질 Markdown으로 변환한다. 슬라이드 내 이미지는 `output/images/` 하위 폴더에 저장하고, MD 내 상대경로로 참조하여 렌더링되도록 한다.

---

## 실행 환경

- **Claude**: 데스크탑 앱 (API 키 없음) — Claude가 직접 이미지 Vision 분석 및 MD 생성 수행
- **Python 경로**: `C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe`
- **의존성**: `pip install python-pptx Pillow` (시스템 Python에 설치)
- **OS**: Windows 11 노트북

> 주의: `python` 명령은 hermes-agent venv를 가리키므로 반드시 위 전체 경로 사용

---

## 워크플로우

### v1 (기본)

```
[Step 1] prepare.py 실행
         C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe prepare.py input/파일.pptx output

[Step 2] Claude가 직접 실행 (이 앱 내)
         - output/manifest.json 읽기
         - output/images/*.png 읽기 (Vision 분석)
         - 변환 규칙 적용하여 output/result.md 생성
```

### v2 (복합 이미지 처리 추가)

```
[Step 1] prepare.py 실행 (동일)
         → manifest.json에 width_px, height_px 추가됨

[Step 2] Claude Vision 분석 (이 앱 내)
         - 각 이미지를 rules.json 기준으로 유형 분류
         - complex_photo_text 이미지 발견 시:
             a) 텍스트 영역 추출 → result.md 본문에 포함
             b) 사진 영역 좌표 추정 → output/crop_spec.json 생성
         - output/result.md 생성

[Step 3] crop.py 실행 (복합 이미지가 있을 때만)
         C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe crop.py output/crop_spec.json output
         → images/*_crop.png 생성

[Step 4] (필요 시) result.md에서 크롭 이미지 경로 확인 후 완료
```

---

## 변환 규칙 (v1 승인)

### 1. 언어
- 모든 내용을 **한국어**로 변환
- 고유명사, 수식, 인명, 논문명은 원문 유지

### 2. 슬라이드 구조
- 슬라이드 제목 → `##` 헤딩
- 본문 텍스트 → 단락 또는 불릿 리스트
- 요소 배치 순서: shape의 `top` → `left` 좌표 기준 위→아래, 좌→우

### 3. 이미지 처리 (핵심 규칙)

**이미지가 주로 표(table)이거나 텍스트인 경우 → 구조화된 텍스트로 변환**
- 표 → 마크다운 표
- 수식 → LaTeX (`$$...$$`) 또는 유니코드 수식 텍스트
- 텍스트 목록 → 번호/불릿 리스트

**그 외 이미지 (사진, 다이어그램, 실제 그림) → 이미지 파일 유지 + 설명 3줄 이내**
```markdown
![간결한 alt text](images/파일명.png)

> 이미지가 나타내는 핵심 내용을 3줄 이내로 설명.
```

**판단 기준 (v2 확장):**
| 이미지 유형 | 분류 키 | 처리 방법 |
|------------|---------|-----------|
| 데이터 표, 통계 수치 | `table_image` | 마크다운 표로 변환 |
| 수식, 수학적 표현 | `formula_image` | LaTeX 수식으로 변환 |
| 텍스트 목록, 단계 설명 | `complex_text_heavy` | 본문 텍스트로 변환 |
| 사진, 실제 이미지 | `simple_photo` | 이미지 유지 + 설명 ≤3줄 |
| 아키텍처 다이어그램 | `simple_diagram` | 이미지 유지 + 설명 ≤3줄 |
| **사진 + 텍스트 혼합** | **`complex_photo_text`** | **사진 크롭 + 텍스트 분리 → crop_spec.json** |

> 분류 키는 `rules.json`의 `image_classification` 항목과 일치해야 한다.

#### v2: 복합 이미지(complex_photo_text) 처리 절차

1. Vision으로 이미지 전체 분석 → 사진 영역과 텍스트 영역 식별
2. 텍스트 영역 내용을 마크다운 표 또는 리스트로 result.md에 포함
3. 사진 영역 좌표를 0.0~1.0 비율로 추정 → `crop_spec.json` 출력
4. result.md에서 이미지 경로는 크롭 예정 파일명 사용 (`images/XX_YY_crop.png`)

**crop_spec.json 형식:**
```json
[
  {
    "source": "images/02_01.png",
    "output": "images/02_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "텍스트 영역에서 추출한 내용 (참고용)"
  }
]
```

### 4. 레이아웃 보존
- 좌우 병렬 배치(슬라이드 2단 구성) → HTML `<table>` 사용
- 텍스트 left < 360pt → 왼쪽 컬럼, left ≥ 360pt → 오른쪽 컬럼

### 5. 금지 사항
- 이미지 내용을 파악했더라도 임의로 처리 방식을 결정하지 않는다
- 이미지 분석 결과를 alt text에만 묻지 않는다 — 반드시 본문에 반영한다
- 처리 방식 변경 시 사용자에게 먼저 확인한다

---

## 출력 구조

```
output/
├── result.md          ← 최종 한국어 마크다운
├── crop_spec.json     ← (v2) 복합 이미지 크롭 스펙 (Claude가 생성)
└── images/
    ├── 01_01.png      ← 슬라이드1 첫번째 이미지
    ├── 02_01.png
    ├── 02_01_crop.png ← (v2) crop.py로 생성된 크롭 이미지
    └── ...
```

---

## 개발 환경

```bash
# 의존성 확인 (prepare.py 실행 시 자동 체크, 없으면 설치 안내)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe prepare.py --check

# PPTX 파싱 실행 (manifest.json + images/ 생성)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe prepare.py input/파일.pptx output

# (v2) 복합 이미지 크롭 실행 — Claude가 crop_spec.json 생성 후 실행
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe crop.py output/crop_spec.json output
```

---

## 주요 처리 흐름

### prepare.py 핵심 로직
- `python-pptx` 라이브러리 사용 (pip install, 소스 복사 아님)
- shape 정렬: `sort_key = (round(top / 457200), left)` — 0.5인치 단위 행 버킷
- 이미지 추출: `shape.image.blob` → `images/슬라이드번호_순번.ext`
- **(v2)** Pillow로 픽셀 크기(`width_px`, `height_px`) 추출 → manifest에 포함
- **(v2)** PPTX 내 표시 크기(`display_width_pt`, `display_height_pt`)도 포함
- 출력: `output/manifest.json` (전체 합본 1개만) + `output/images/`
- `output/manifests/` 폴더는 생성하지 않음 (불필요, 제거됨)

### crop.py 핵심 로직 (v2 신규)
- `output/crop_spec.json`을 읽어 각 항목 처리
- `region_pct` (0.0~1.0 비율) → 실제 픽셀 좌표로 변환 후 Pillow `.crop()` 호출
- 결과: `images/XX_YY_crop.png` (원본 이미지 이름 + `_crop` 접미사)
- 경계 클램프 처리 (이미지 밖 좌표 자동 보정)

### Claude 변환 시 주의사항
- `manifest.json` + `images/` 를 함께 읽어야 정확한 위치 파악 가능
- 수식 이미지는 슬라이드 작성자가 텍스트 shape 대신 이미지로 삽입한 경우가 많음 → Vision으로 읽어 LaTeX 변환
- 슬라이드 텍스트/이미지가 모두 없는 경우 → 내용이 이미지 내부에 내장된 것으로 판단, 명시적으로 표기
- **(v2)** `complex_photo_text` 유형 발견 시 반드시 `crop_spec.json` 항목 생성 후 본문에 크롭 이미지 경로 사용
- **(v2)** 판단 불명확한 경우 사용자에게 확인 요청 (rules.json 우선 참고)

### 학습 데이터 참조 (v2)
- `rules.json` — 이미지 분류 기준, 레이아웃 패턴, 용어 사전
- `examples/` — 슬라이드 유형별 Few-shot 변환 예시 (manifest.json + output.md 쌍)
- 새 패턴 발견 시 `examples/` 폴더에 추가하고 `rules.json` 업데이트

---

## 품질 개선 이력 (튜닝 로그)

### v1 (2026-06-29)
- 이미지 처리 규칙 확립: 표/텍스트 이미지 → 구조화 텍스트, 사진/다이어그램 → 이미지 유지 + 3줄 설명
- 수식 이미지 → LaTeX 변환 적용
- 데이터셋 표 → 마크다운 표 변환 적용
- 한국어 번역 + 원문 기술 용어 병기 규칙 확립
- Python 경로 이슈 해결: 시스템 Python 전체 경로 사용

### v2 (2026-06-30) — Phase 1 완료
- **prepare.py**: 이미지 픽셀 크기 (width_px, height_px) 및 표시 크기 (display_*_pt) manifest 추가
- **crop.py** 신규: Claude Vision이 추정한 좌표로 Pillow 이미지 크롭
- **rules.json** 신규: 이미지 분류 기준, 레이아웃 패턴, 용어 사전, crop_spec 형식 정의
- **examples/** 신규: 제목 슬라이드, 2단 레이아웃, 복합 이미지 Few-shot 예시
- CLAUDE.md: v2 워크플로우, 복합 이미지 처리 절차, crop_spec.json 형식 문서화

> 향후 변환 튜닝 후 이 섹션에 버전별로 추가한다.
