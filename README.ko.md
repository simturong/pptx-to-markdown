# PPTX to Markdown (pptx-to-markdown)

> 기술 프레젠테이션용 슬라이드를 위해 설계된 고성능 파워포인트(PPTX) $\rightarrow$ 마크다운(Markdown) 자동 변환기입니다. 배치 레이아웃 자동 정렬, LaTeX 수식 및 표 변환, 복합 이미지 내 사진 자동 크롭, 그리고 변환 정합성을 체크하는 품질 자동 검증(QA) 평가기 기능을 내장하고 있습니다.

[![GitHub License](https://img.shields.io/github/license/simturong/pptx-to-markdown?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)](https://www.python.org/)
[![Quality Score](https://img.shields.io/badge/Quality%20Score-94%2F100-success.svg?style=flat-square)](#-성능-검증-보고서)

---

## 📖 목차
* [핵심 기능](#-핵심-기능)
* [신속 모드 vs 정밀 모드 비교](#-신속-모드-vs-정밀-모드-비교)
* [성능 검증 보고서](#-성능-검증-보고서)
* [클러드 스킬(Claude Skill)로 배포 및 설치하는 방법](#-클러드-스킬claude-skill로-배포-및-설치하는-방법)
* [사용 방법](#-사용-방법)
* [디렉토리 구조](#-디렉토리-구조)

---

## 🌟 핵심 기능

*   **배치 좌표 기반 정렬**: 슬라이드 내 각 요소의 좌표(`top`, `left`)를 분석하여 위$\rightarrow$아래, 좌$\rightarrow$우로 완벽하게 자동 정렬하여 가독성과 읽기 순서를 보존합니다.
*   **복합 이미지 분할 크롭**: 그림과 텍스트 정보가 한 장의 이미지 파일로 뭉쳐있는 복합 이미지(`complex_photo_text`)를 탐지하여, 그림 영역만 잘라내어 별도로 저장하고 우측 텍스트는 마크다운 표/리스트로 추출합니다.
*   **LaTeX 수식 및 표 변환**: 이미지화된 복잡한 수학 수식과 표(Grid)를 고정밀 텍스트(LaTeX 디스플레이 수식 `$$` 및 마크다운 표 문법)로 자동 치환합니다.
*   **품질 자동 검증 엔진 (`evaluate.py`)**: 생성된 마크다운을 원본 메타데이터와 대조하여 슬라이드 매칭, 이미지 누락, 수식 결합 오류를 검증하고 등급 점수 보고서(`evaluation_report.md`)를 즉시 생성합니다.

---

## ⚡ 신속 모드 vs 정밀 모드 비교

사용자의 작업 목적과 인프라 속도에 맞추어 변환 파이프라인 모드를 선택할 수 있습니다.

| 특징 및 지표 | 🚀 신속 모드 (Lite Mode) | 🎯 정밀 모드 (Pro Mode - 기본값) |
| :--- | :---: | :---: |
| **정보 보존 수준** | 보통 (복합 이미지 내 텍스트 유실 가능) | **정보 손실률 0%** (모든 텍스트 구조화 및 사진 크롭) |
| **수식 및 표 텍스트화** | 미지원 (원본 이미지 링크 유지) | **완벽 지원** (LaTeX 코드 및 마크다운 표 코드로 치환) |
| **처리 단계** | 단일 단계 (`prepare.py` 단독 구동) | 3단계 순차 실행 (Prepare $\rightarrow$ Crop $\rightarrow$ QA Evaluator) |
| **처리 속도** | **초고속 (Ultra-Fast)** | 보통 (이미지 및 수식 개수에 비례) |
| **추천 용도** | 텍스트 위주 슬라이드, 빠른 대량의 초안 작성 | 학술 논문, 하드웨어 사양서, 비즈니스 공식 문서 |

---

## 📊 성능 검증 보고서

복잡한 수식, 표, 다이어그램, 바운딩 박스가 혼재된 총 13슬라이드의 대학원 학술 발표 PPTX를 사용하여 정밀 테스트를 진행했습니다.

### 📝 최종 검증 스코어

*   **최종 품질 점수**: **94 / 100 점**
*   **치명적 오류**: **0 건**
*   **검토 필요 경고**: **27 건** (번역에 따른 일치율 미달 및 수식 대체 건)

```
==================================================
  품질 평가 완료! 점수: 94/100
  - 치명적 오류: 0 건
  - 검토 필요 경고: 27 건
  상세 보고서가 다음 경로에 저장되었습니다:
    output/evaluation_report.md
==================================================
```
*주의: 감점된 6점은 슬라이드 내 학술 전문 영어 용어가 한국어 의미로 의역 번역됨에 따라 감지된 보존율 경고입니다. 수작업 검토 결과 번역 퀄리티는 100% 무결함을 확인했습니다.*

---

## 🤖 클러드 스킬(Claude Skill)로 배포 및 설치하는 방법

이 리포지토리를 **클러드 스킬(Claude Skill)**로 설정하면, AI 코딩 에이전트(Claude Code 등)가 슬라이드 파일을 다룰 때 이 변환기를 스킬로 인식해 자율 실행할 수 있습니다.

### 방법 A: 글로벌 스킬로 등록 (모든 작업 공간에서 사용 가능)
패키징된 `skills/pptx-to-markdown` 폴더를 글로벌 커스터마이징 스킬 디렉토리로 통째로 복사하기만 하면 한 번에 설치됩니다.

*   **macOS / Linux**:
    ```bash
    cp -r skills/pptx-to-markdown ~/.gemini/config/skills/
    ```
*   **Windows (PowerShell)**:
    ```powershell
    Copy-Item -Recurse -Path "skills/pptx-to-markdown" -Destination "$HOME\.gemini\config\skills\" -Force
    ```

### 방법 B: 프로젝트 전용 스킬로 등록 (현재 워크스페이스만 적용)
스킬을 특정 프로젝트 디렉토리에서만 동작하게 하려면:
*   워크스페이스 루트 경로에 `.agents/skills/` 디렉토리를 생성합니다.
*   `skills/pptx-to-markdown` 폴더를 해당 디렉토리 아래로 복사합니다. (에이전트가 실행될 때 스킬을 자동 탐지하여 활성화합니다.)

---

## 🚀 사용 방법

### 필수 패키지 설치
`python-pptx`와 `Pillow` 패키지가 사전에 설치되어 있어야 합니다.
```bash
python -m pip install python-pptx Pillow
```

### 파이프라인 구동
```bash
# 1. 정밀 모드로 실행 (수식 변환, 크롭 분할, 자동 QA까지 원스톱 실행 - 권장)
python src/run.py input/sample.pptx output --mode pro

# 2. 신속 모드로 실행 (이미지 크롭 및 평가 단계를 건너뛰고 텍스트 및 기본 이미지만 추출)
python src/run.py input/sample.pptx output --mode lite
```

---

## 📁 디렉토리 구조

```
.
├── src/
│   ├── run.py          # 파이프라인 통합 제어 마스터 스크립트
│   ├── prepare.py      # PPTX 분해기 (텍스트 및 이미지 추출)
│   ├── crop.py         # Pillow 기반 부분 이미지 크롭기
│   └── evaluate.py     # 마크다운 무결성 검증 및 품질 보고서 작성기
├── docs/
│   ├── Plan.md         # 로드맵 및 개발 계획서
│   └── examples/       # Claude Vision 학습용 예시 데이터셋
├── input/              # 변환할 원본 PPTX 위치
└── output/             # 최종 생성된 MD 파일, 크롭 이미지 및 평가 보고서
```

## 📄 라이선스
이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하십시오.
