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

```
[Step 1] prepare.py 실행 (Python)
         python prepare.py input/파일.pptx output

[Step 2] Claude가 직접 실행 (이 앱 내)
         - output/manifest.json 읽기
         - output/images/*.png 읽기 (Vision 분석)
         - 변환 규칙 적용하여 output/result.md 생성
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

**판단 기준:**
| 이미지 유형 | 처리 방법 |
|------------|-----------|
| 데이터 표, 통계 수치 | 마크다운 표로 변환 |
| 수식, 수학적 표현 | LaTeX 수식으로 변환 |
| 텍스트 목록, 단계 설명 | 본문 텍스트로 변환 |
| 사진, 실제 이미지 | 이미지 유지 + 설명 ≤3줄 |
| 아키텍처 다이어그램 | 이미지 유지 + 설명 ≤3줄 |
| 연구 배경 그림 | 이미지 유지 + 설명 ≤3줄 |

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
└── images/
    ├── 01_01.png      ← 슬라이드1 첫번째 이미지
    ├── 02_01.png
    └── ...
```

---

## 개발 환경

```bash
# 의존성 확인 (prepare.py 실행 시 자동 체크, 없으면 설치 안내)
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe prepare.py --check

# PPTX 파싱 실행
C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe prepare.py input/파일.pptx output
```

---

## 주요 처리 흐름

### prepare.py 핵심 로직
- `python-pptx` 라이브러리 사용 (pip install, 소스 복사 아님)
- shape 정렬: `sort_key = (round(top / 457200), left)` — 0.5인치 단위 행 버킷
- 이미지 추출: `shape.image.blob` → `images/슬라이드번호_순번.ext`
- 출력: `output/manifest.json` (전체 합본 1개만) + `output/images/`
- `output/manifests/` 폴더는 생성하지 않음 (불필요, 제거됨)

### Claude 변환 시 주의사항
- `manifest.json` + `images/` 를 함께 읽어야 정확한 위치 파악 가능
- 수식 이미지는 슬라이드 작성자가 텍스트 shape 대신 이미지로 삽입한 경우가 많음 → Vision으로 읽어 LaTeX 변환
- 슬라이드 10처럼 텍스트/이미지가 모두 없는 경우 → 내용이 이미지 내부에 내장된 것으로 판단, 명시적으로 표기

---

## 품질 개선 이력 (튜닝 로그)

### v1 (2026-06-29)
- 이미지 처리 규칙 확립: 표/텍스트 이미지 → 구조화 텍스트, 사진/다이어그램 → 이미지 유지 + 3줄 설명
- 수식 이미지 → LaTeX 변환 적용
- 데이터셋 표 → 마크다운 표 변환 적용
- 한국어 번역 + 원문 기술 용어 병기 규칙 확립
- Python 경로 이슈 해결: 시스템 Python 전체 경로 사용

> 향후 변환 튜닝 후 이 섹션에 버전별로 추가한다.
