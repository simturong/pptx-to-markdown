"""
Integrated Pipeline Executor (run.py) — v3
Processes the PPTX conversion pipeline in one stop based on Speed (Lite) or Precision (Pro) mode.

Usage:
  python src/run.py <file.pptx> [output_dir] --mode [lite|pro]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd_list):
    """Execute a subprocess command and handle exceptions."""
    try:
        # Explicitly pass current python executable path
        result = subprocess.run(
            [sys.executable] + cmd_list,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[Error] Command execution failed: {' '.join(cmd_list)}")
        print(f"  Return code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[Error] System error occurred: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="PPTX to Markdown Integrated Pipeline")
    parser.add_argument("pptx_file", help="Path to the target PPTX file to convert")
    parser.add_argument("output_dir", nargs="?", default="output", help="Output directory (default: output)")
    parser.add_argument(
        "--mode",
        choices=["lite", "pro"],
        default="pro",
        help="Execution mode: lite (Speed mode, V1) / pro (Precision mode, V2 - default)"
    )

    args = parser.parse_args()

    pptx_path = Path(args.pptx_file)
    output_dir = Path(args.output_dir)

    if not pptx_path.exists():
        print(f"[Error] PPTX file does not exist: {pptx_path}")
        sys.exit(1)

    print("==================================================")
    print(f"  Starting PPTX to MD Conversion Pipeline")
    print(f"  - File: {pptx_path.name}")
    print(f"  - Path: {pptx_path}")
    print(f"  - Mode: {'🚀 Speed Mode (Speed Mode)' if args.mode == 'lite' else '🎯 Precision Mode (Precision Mode)'}")
    print(f"  - Output: {output_dir.absolute()}")
    print("==================================================\n")

    # Step 1: Run prepare.py (Common)
    print("[Step 1] Deconstructing PPTX and parsing resources (prepare.py)")
    prepare_script = Path(__file__).parent / "prepare.py"
    if not run_command([str(prepare_script), str(pptx_path), str(output_dir)]):
        print("[Fail] Pipeline aborted at Step 1.")
        sys.exit(1)

    if args.mode == "lite":
        print("\n==================================================")
        print("🚀 Speed Mode (Speed Mode) parsing completed!")
        print("  - output/manifest.json and output/images/ extracted.")
        print("  - Feed these resources to Claude to generate the final Korean Markdown.")
        print("==================================================")
        return

    # Pro Mode Only Steps
    crop_spec_file = output_dir / "crop_spec.json"
    result_md_file = output_dir / "result.md"

    # Step 2: Crop composite images (crop.py)
    print("\n[Step 2] Processing composite image cropping (crop.py)")
    if crop_spec_file.exists():
        crop_script = Path(__file__).parent / "crop.py"
        if run_command([str(crop_script), str(crop_spec_file), str(output_dir)]):
            print("  - Composite image cropping completed.")
        else:
            print("  - [Warning] Something went wrong while running the crop script.")
    else:
        print("  - [Info] crop_spec.json not found. Skipping crop step.")
        print("    (Once crop specifications for composite images are written during Claude conversion, crop_spec.json will be generated.)")

    # Step 3: Quality validation (evaluate.py)
    print("\n[Step 3] Automated quality evaluation (evaluate.py)")
    if result_md_file.exists():
        evaluate_script = Path(__file__).parent / "evaluate.py"
        manifest_file = output_dir / "manifest.json"
        run_command([str(evaluate_script), str(manifest_file), str(result_md_file), str(output_dir)])
    else:
        print("  - [Info] Final result.md not found. Skipping quality evaluation.")
        print("    (Quality evaluation will run once result.md is generated.)")

    print("\n==================================================")
    print("🎯 Precision Mode (Precision Mode) pipeline completed!")
    print("==================================================")


if __name__ == "__main__":
    main()
