"""
이미지 크롭 스크립트 — v2
Claude Vision이 분석한 사진 영역 좌표로 이미지를 크롭합니다.

사용법:
  python crop.py output/crop_spec.json [출력폴더]

crop_spec.json 형식 (Claude가 변환 분석 시 생성):
[
  {
    "source": "images/02_01.png",
    "output": "images/02_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "텍스트 영역에서 추출된 내용 (참고용)"
  }
]

region_pct: 이미지 전체 크기 대비 0.0~1.0 비율
  x1, y1: 크롭 시작 좌표 (좌상단)
  x2, y2: 크롭 끝 좌표 (우하단)
"""

import json
import sys
from pathlib import Path


def crop_images(spec_path: str, output_dir: str = "output"):
    spec_path = Path(spec_path)
    output_dir = Path(output_dir)

    try:
        from PIL import Image
    except ImportError:
        print("[오류] Pillow가 설치되어 있지 않습니다.")
        print("실행: C:\\Users\\sando\\AppData\\Local\\Programs\\Python\\Python313\\python.exe -m pip install Pillow")
        sys.exit(1)

    if not spec_path.exists():
        print(f"[오류] 파일 없음: {spec_path}")
        sys.exit(1)

    try:
        specs = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[오류] crop_spec.json 읽기 실패: {e}")
        sys.exit(1)

    if isinstance(specs, dict):
        specs = [specs]

    ok = 0
    for spec in specs:
        source = output_dir / spec["source"]
        out_file = output_dir / spec["output"]
        region = spec["region_pct"]

        if not source.exists():
            print(f"  [경고] 파일 없음: {source}")
            continue

        try:
            with Image.open(source) as img:
                w, h = img.size
                x1 = int(region["x1"] * w)
                y1 = int(region["y1"] * h)
                x2 = int(region["x2"] * w)
                y2 = int(region["y2"] * h)

                x1, x2 = max(0, x1), min(w, x2)
                y1, y2 = max(0, y1), min(h, y2)

                if x2 <= x1 or y2 <= y1:
                    print(f"  [경고] 크롭 영역 불유효 (너비/높이=0): {spec['source']}")
                    continue

                cropped = img.crop((x1, y1, x2, y2))
                out_file.parent.mkdir(parents=True, exist_ok=True)
                cropped.save(out_file)
                print(f"  [OK] {spec['source']} → {spec['output']}  ({x2-x1}×{y2-y1}px)")
                ok += 1

        except Exception as e:
            print(f"  [오류] {spec['source']}: {e}")

    print(f"\n크롭 완료: {ok}/{len(specs)} 건")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python crop.py <crop_spec.json> [출력폴더]")
        print()
        print("crop_spec.json 예시:")
        example = [
            {
                "source": "images/02_01.png",
                "output": "images/02_01_crop.png",
                "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
                "extracted_text": "텍스트 영역 내용 (참고용)"
            }
        ]
        print(json.dumps(example, ensure_ascii=False, indent=2))
        sys.exit(0)

    spec_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    crop_images(spec_file, out_dir)
