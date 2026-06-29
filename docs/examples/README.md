# Few-shot 변환 예시

각 폴더에는 슬라이드 유형별 변환 예시가 있습니다.
Claude 변환 시 rules.json과 함께 이 예시들을 참조합니다.

## 폴더 구조

```
examples/
├── 01_title_slide/     ← 제목 슬라이드 변환 예시
│   ├── manifest.json   ← 해당 슬라이드의 manifest 발췌
│   └── output.md       ← 기대 변환 결과
├── 02_two_column/      ← 2단 레이아웃 변환 예시
│   ├── manifest.json
│   └── output.md
└── 03_complex_image/   ← 복합 이미지(사진+텍스트) 변환 예시
    ├── manifest.json
    ├── image_desc.md   ← 이미지 Vision 분석 결과 참고
    ├── output.md       ← 기대 변환 결과
    └── crop_spec.json  ← 크롭 스펙 예시
```

## 예시 추가 기준

- 새 PPTX 유형에서 처음 만나는 패턴은 여기에 추가
- 변환 후 사용자가 수정한 결과가 있으면 해당 슬라이드를 예시로 저장
- 파일명: 슬라이드 번호_유형 (예: `04_formula_image/`)
