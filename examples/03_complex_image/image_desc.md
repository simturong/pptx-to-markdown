# 복합 이미지 분석 예시 (05_01.png)

## Vision 분석 결과

**이미지 유형**: complex_photo_text (사진 + 텍스트 병렬)

**레이아웃**:
- 좌측 35% : 고양이 사진 (자연 이미지)
- 우측 65% : 텍스트 영역 (Q&A 형태)

**텍스트 영역 추출 내용**:
```
Prompt: How many cats are in the image?
Groundtruth: (B) 1
MobileVLM-V2: 3 ❌
Ours: (B) 1 ✅
```

**처리 결정**: complex_photo_text → crop.py로 사진 크롭 + 텍스트 분리

## crop_spec.json 출력

```json
[
  {
    "source": "images/05_01.png",
    "output": "images/05_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "Prompt: How many cats are in the image?\nGroundtruth: (B) 1\nMobileVLM-V2: 3 ❌\nOurs: (B) 1 ✅"
  }
]
```
