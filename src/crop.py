"""
Image Cropping Script — v2
Crops images based on coordinates analyzed by Claude Vision.

Usage:
  python crop.py output/crop_spec.json [output_dir]

crop_spec.json Format (Generated during Claude conversion):
[
  {
    "source": "images/02_01.png",
    "output": "images/02_01_crop.png",
    "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
    "extracted_text": "Extracted content from text area (for reference)"
  }
]

region_pct: ratio of 0.0 to 1.0 relative to total image size
  x1, y1: crop start coordinates (top-left)
  x2, y2: crop end coordinates (bottom-right)
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
        print("[Error] Pillow is not installed.")
        print("Run: C:\\Users\\sando\\AppData\\Local\\Programs\\Python\\Python313\\python.exe -m pip install Pillow")
        sys.exit(1)

    if not spec_path.exists():
        print(f"[Error] File not found: {spec_path}")
        sys.exit(1)

    try:
        specs = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Error] Failed to read crop_spec.json: {e}")
        sys.exit(1)

    if isinstance(specs, dict):
        specs = [specs]

    ok = 0
    for spec in specs:
        source = output_dir / spec["source"]
        out_file = output_dir / spec["output"]
        region = spec["region_pct"]

        if not source.exists():
            print(f"  [Warning] File not found: {source}")
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
                    print(f"  [Warning] Invalid crop region (width/height=0): {spec['source']}")
                    continue

                cropped = img.crop((x1, y1, x2, y2))
                out_file.parent.mkdir(parents=True, exist_ok=True)
                cropped.save(out_file)
                print(f"  [OK] {spec['source']} → {spec['output']}  ({x2-x1}×{y2-y1}px)")
                ok += 1

        except Exception as e:
            print(f"  [Error] {spec['source']}: {e}")

    print(f"\nCropping completed: {ok}/{len(specs)} cases")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crop.py <crop_spec.json> [output_dir]")
        print()
        print("crop_spec.json example:")
        example = [
            {
                "source": "images/02_01.png",
                "output": "images/02_01_crop.png",
                "region_pct": {"x1": 0.0, "y1": 0.0, "x2": 0.35, "y2": 1.0},
                "extracted_text": "Text area content (for reference)"
            }
        ]
        print(json.dumps(example, ensure_ascii=False, indent=2))
        sys.exit(0)

    spec_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    crop_images(spec_file, out_dir)
