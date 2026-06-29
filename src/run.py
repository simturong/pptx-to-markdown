"""
통합 실행기 (run.py) — v3
사용자가 신속 모드(Lite) 및 정밀 모드(Pro)를 지정하여 PPTX 변환 파이프라인을 원스톱으로 처리합니다.

사용법:
  python src/run.py <파일.pptx> [출력폴더] --mode [lite|pro]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd_list):
    """서브프로세스 명령 실행 및 예외 처리."""
    try:
        # sys.executable을 사용해 현재 작동 중인 파이썬 인터프리터 경로를 명시적으로 전달
        # C:\Users\sando\AppData\Local\Programs\Python\Python313\python.exe 대응
        result = subprocess.run(
            [sys.executable] + cmd_list,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] 명령 실행 실패: {' '.join(cmd_list)}")
        print(f"  반환 코드: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[오류] 시스템 오류 발생: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="PPTX to Markdown 변환기 통합 파이프라인")
    parser.add_argument("pptx_file", help="변환 대상 PPTX 파일 경로")
    parser.add_argument("output_dir", nargs="?", default="output", help="출력 디렉토리 (기본값: output)")
    parser.add_argument(
        "--mode",
        choices=["lite", "pro"],
        default="pro",
        help="실행 모드: lite (스피드 모드, V1) / pro (정밀 모드, V2 - 기본값)"
    )

    args = parser.parse_args()

    pptx_path = Path(args.pptx_file)
    output_dir = Path(args.output_dir)

    if not pptx_path.exists():
        print(f"[오류] PPTX 파일이 존재하지 않습니다: {pptx_path}")
        sys.exit(1)

    print("==================================================")
    print(f"  PPTX to MD 변환 파이프라인 시작")
    print(f"  - 파일: {pptx_path.name}")
    print(f"  - 경로: {pptx_path}")
    print(f"  - 모드: {'🚀 스피드 모드 (Speed Mode)' if args.mode == 'lite' else '🎯 정밀 모드 (Precision Mode)'}")
    print(f"  - 출력: {output_dir.absolute()}")
    print("==================================================\n")

    # 1단계: prepare.py 실행 (공통)
    print("[Step 1] PPTX 분해 및 리소스 파싱 (prepare.py)")
    prepare_script = Path(__file__).parent / "prepare.py"
    if not run_command([str(prepare_script), str(pptx_path), str(output_dir)]):
        print("[실패] 파이프라인이 1단계에서 중단되었습니다.")
        sys.exit(1)

    if args.mode == "lite":
        print("\n==================================================")
        print("🚀 스피드 모드(Speed Mode) 파싱 단계 완료!")
        print("  - output/manifest.json 및 output/images/ 추출 완료.")
        print("  - 이제 이 리소스를 Claude에 입력하여 최종 한국어 MD를 생성하세요.")
        print("==================================================")
        return

    # Pro 모드 전용 단계
    crop_spec_file = output_dir / "crop_spec.json"
    result_md_file = output_dir / "result.md"

    # 2단계: 복합 이미지 크롭 (crop.py)
    print("\n[Step 2] 복합 이미지 크롭 처리 (crop.py)")
    if crop_spec_file.exists():
        crop_script = Path(__file__).parent / "crop.py"
        if run_command([str(crop_script), str(crop_spec_file), str(output_dir)]):
            print("  - 복합 이미지 크롭 완료.")
        else:
            print("  - [경고] 크롭 스크립트 실행 중 문제가 발생했습니다.")
    else:
        print("  - [참고] crop_spec.json 명세서가 발견되지 않아 크롭 단계를 건너뜁니다.")
        print("    (Claude 변환 시 복합 이미지 크롭 사양이 기재되면 crop_spec.json을 생성하고 정밀 모드를 다시 돌리십시오.)")

    # 3단계: 품질 자동 검증 (evaluate.py)
    print("\n[Step 3] 변환 결과물 자동 품질 평가 (evaluate.py)")
    if result_md_file.exists():
        evaluate_script = Path(__file__).parent / "evaluate.py"
        manifest_file = output_dir / "manifest.json"
        run_command([str(evaluate_script), str(manifest_file), str(result_md_file), str(output_dir)])
    else:
        print("  - [참고] 최종 result.md 결과 파일이 아직 없어 품질 평가 단계를 건너뜁니다.")
        print("    (Claude를 통해 result.md를 생성한 후 정밀 모드를 실행하면 자동 품질 보증 리포트가 작동합니다.)")

    print("\n==================================================")
    print("🎯 정밀 모드(Precision Mode) 파이프라인 처리 완료!")
    print("==================================================")


if __name__ == "__main__":
    main()
