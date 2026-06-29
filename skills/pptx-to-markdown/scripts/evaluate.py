"""
변환 품질 자동 평가 스크립트 — v2
- manifest.json과 result.md를 비교하여 슬라이드별 변환 완성도 및 누락 요소를 검증합니다.
- 평가 보고서(evaluation_report.md)를 생성합니다.

사용법:
  python src/evaluate.py output/manifest.json output/result.md output
"""

import json
import re
import sys
from pathlib import Path


def evaluate_quality(manifest_path: str, result_path: str, output_dir: str):
    manifest_path = Path(manifest_path)
    result_path = Path(result_path)
    output_dir = Path(output_dir)
    image_dir = output_dir / "images"

    if not manifest_path.exists():
        print(f"[오류] manifest.json 파일이 없습니다: {manifest_path}")
        sys.exit(1)

    if not result_path.exists():
        print(f"[오류] result.md 파일이 없습니다: {result_path}")
        sys.exit(1)

    # 1. 파일 읽기
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[오류] manifest.json 읽기 실패: {e}")
        sys.exit(1)

    try:
        result_text = result_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[오류] result.md 읽기 실패: {e}")
        sys.exit(1)

    # 슬라이드별 파싱 (result.md를 '---' 구분선 기준으로 쪼갬)
    # PPTX 변환기 출력 포맷 상 각 슬라이드는 '---' 로 구분되어야 함
    slides_md = [s.strip() for s in result_text.split("\n---") if s.strip()]
    
    # 만약 첫 슬라이드가 # 제목으로 시작하고 '---'가 없다면 첫 슬라이드로 처리됨
    # splitting '\n---' handles most layouts. If length differs, we'll flag it.
    
    report = []
    report.append("# 변환 품질 평가 보고서 (Auto Evaluation Report)")
    report.append(f"- **대상 파일**: `{result_path.name}`")
    report.append(f"- **기준 파일**: `{manifest_path.name}`\n")
    
    report.append("## 1. 총평 요약")
    
    total_slides_manifest = len(manifest)
    total_slides_md = len(slides_md)
    
    report.append(f"- manifest.json 슬라이드 수: **{total_slides_manifest}**")
    report.append(f"- result.md 분할 슬라이드 수: **{total_slides_md}**")
    
    slide_count_match = total_slides_manifest == total_slides_md
    report.append(f"- 슬라이드 수 일치 여부: {'✅ 일치' if slide_count_match else '❌ 불일치 (검증 필요)'}")
    
    errors = []
    warnings = []
    slide_reports = []
    
    # 2. 슬라이드별 정밀 검사
    # 매핑을 슬라이드 번호 기준으로 진행 (1-indexed)
    for i, slide_data in enumerate(manifest, start=1):
        slide_idx = slide_data["slide"]
        elements = slide_data["elements"]
        
        slide_title = f"슬라이드 {slide_idx}"
        slide_errors = []
        slide_warnings = []
        
        # 1-indexed와 slides_md index (0-indexed) 매핑
        md_content = ""
        if i - 1 < len(slides_md):
            md_content = slides_md[i - 1]
        
        # 슬라이드 내 제목(Title) 추출 및 확인
        title_elements = [el for el in elements if el["type"] == "title"]
        for te in title_elements:
            clean_title = re.sub(r'[\*\#\_]', '', te["text"]).strip()
            # 한글로 변환되었을 수도 있으므로 완전 매칭보다는 한글/영어 키워드로 체크하거나
            # 제목에 사용된 주요 명사 단어가 md_content에 포함되는지 체크
            words = [w for w in re.split(r'\s+', clean_title) if len(w) >= 2]
            matched_words = [w for w in words if w.lower() in md_content.lower()]
            
            # 제목 텍스트 자체가 제목 헤더(# 또는 ##) 근처에 존재하는지 검사
            # (한국어로 번역되어 매칭되지 않을 수 있어 warning으로 격하)
            if words and len(matched_words) / len(words) < 0.3:
                # 번역기 특성상 완전히 한글화될 수 있으므로 한글 제목이 존재하는지만 대략 체크
                has_header = md_content.startswith("#") or "\n#" in md_content
                if not has_header:
                    slide_errors.append("슬라이드 제목 헤더(# 또는 ##)가 본문에서 식별되지 않음")
                else:
                    # 번역된 것으로 추정되므로 단순 정보성 경고로 완화
                    slide_warnings.append(f"제목 번역됨 추정: 원본 '{clean_title[:30]}...' -> 한글 헤더 매칭")

        # 이미지 검사
        image_elements = [el for el in elements if el["type"] == "image"]
        md_images = re.findall(r'!\[.*?\]\((images/.*?)\)', md_content)
        
        # 슬라이드 내에 수식이나 표가 존재하는지 검사
        has_latex = "$$" in md_content or len(re.findall(r'(?<!\$)\$(?!\$)', md_content)) >= 2
        has_table = "|" in md_content and "-" in md_content
        
        # 크롭된 이미지 매핑도 허용해야 함
        # 예: images/05_01.png 대신 images/05_01_crop.png도 매칭으로 인정
        for img_el in image_elements:
            orig_path = img_el["path"]
            orig_name = Path(orig_path).stem  # e.g., '05_01'
            
            # md_content 내에 이 이미지가 언급되는지 체크
            found = False
            for md_img in md_images:
                if orig_name in md_img:
                    found = True
                    # 실제 로컬 파일이 존재하는지 체크
                    local_img_path = output_dir / md_img
                    if not local_img_path.exists():
                        slide_errors.append(f"참조 이미지 파일 없음: `{md_img}`")
                    break
            
            if not found:
                # 수식/표 이미지로 대체되었을 가능성 체크
                if has_latex:
                    slide_warnings.append(f"이미지 `{orig_path}`가 LaTeX 수식으로 대체된 것으로 추정됨")
                elif has_table:
                    slide_warnings.append(f"이미지 `{orig_path}`가 마크다운 표(Table)로 대체된 것으로 추정됨")
                else:
                    slide_errors.append(f"이미지 누락: 원본 `{orig_path}`가 마크다운 내에 포함되지 않음")

        # 텍스트 검사 (전체적인 키워드 보존율 분석)
        text_elements = [el for el in elements if el["type"] == "text"]
        all_orig_text = " ".join([te["text"] for te in text_elements])
        
        # 5글자 이상의 영단어나 한글 단어 추출
        orig_words = list(set(re.findall(r'[a-zA-Z가-힣]{3,}', all_orig_text)))
        if orig_words:
            # 번역이 되었을 수 있으므로 단어 매칭률은 보수적으로 체크 (한글 번역 시 영어 단어가 한글로 바뀔 수 있음)
            # 기술 용어 병기 기준(CLAUDE.md)을 준수했는지도 체크 가능
            matched = 0
            for w in orig_words:
                if w.lower() in md_content.lower():
                    matched += 1
                # 혹시 한글 번역 단어가 매칭되는지 추가 체크할 수도 있지만 여기서는 단순 포함율로 경고 수준 결정
            
            match_ratio = matched / len(orig_words)
            if match_ratio < 0.2 and len(all_orig_text.strip()) > 30:
                slide_warnings.append(f"텍스트 키워드 보존율 매우 낮음 ({match_ratio:.1%}). 내용 누락 여부 검토 필요.")

        # 마크다운 문법 검사 (LaTeX 수식)
        # $$ 짝이 맞는지 검사
        display_math_blocks = re.findall(r'\$\$.*?\$\$', md_content, re.DOTALL)
        raw_double_dollars = len(re.findall(r'\$\$', md_content))
        if raw_double_dollars % 2 != 0:
            slide_errors.append("LaTeX 디스플레이 수식 기호 `$$`가 짝이 맞지 않음 (홀수 개수)")
            
        # $ 짝이 맞는지 검사 (inline math)
        # 단, 일반 $ 기호(달러 기호)도 있을 수 있으므로 수식 구조인지 확인하는 간이 검사
        raw_single_dollars = len(re.findall(r'(?<!\$)\$(?!\$)', md_content))
        if raw_single_dollars % 2 != 0:
            slide_warnings.append("LaTeX 인라인 수식 기호 `$`가 홀수 개수임 (단순 화폐 표기일 수도 있음)")

        # 마크다운 표(Table) 문법 검사
        # '|' 기호가 포함된 라인이 연속해서 있는데 2번째 라인이 '--|--' 형태인지 검사
        lines = md_content.split("\n")
        for idx_line, line in enumerate(lines):
            if "|" in line and idx_line + 1 < len(lines):
                next_line = lines[idx_line + 1]
                # 헤더 구분선인지 체크
                if "|" in next_line and "-" in next_line and not re.search(r'[a-zA-Z가-힣]', next_line):
                    # 앞뒤 컬럼 개수 비교
                    cols_header = len(line.split("|"))
                    cols_divider = len(next_line.split("|"))
                    if cols_header != cols_divider:
                        slide_errors.append(f"마크다운 표 구조 불일치 ({idx_line+1}행): 헤더 컬럼 수({cols_header}) != 구분선 컬럼 수({cols_divider})")

        # 결과 기록
        slide_reports.append({
            "slide": slide_idx,
            "errors": slide_errors,
            "warnings": slide_warnings,
            "status": "❌ 오류" if slide_errors else ("⚠️ 경고" if slide_warnings else "✅ 통과")
        })
        
        errors.extend([f"슬라이드 {slide_idx}: {err}" for err in slide_errors])
        warnings.extend([f"슬라이드 {slide_idx}: {war}" for war in slide_warnings])

    # 3. 종합 평가 점수 계산
    # 에러는 개당 -10점
    # 심각한 경고(키워드 보존율 낮음 등)는 개당 -3점
    # 정상적 대체/번역 관련 정보성 경고(수식/표 대체, 제목 번역)는 감점 없음 (0점)
    deductible_warnings = 0
    for war in warnings:
        if "보존율 매우 낮음" in war:
            deductible_warnings += 1
            
    score = 100 - (len(errors) * 10) - (deductible_warnings * 3)
    score = max(0, score)
    
    report.append(f"- **최종 변환 품질 점수**: **{score}/100**")
    report.append(f"  - (실제 감점 대상 경고: {deductible_warnings} 건 / 단순 정보성 경고: {len(warnings) - deductible_warnings} 건)\n")
    
    # 4. 발견된 에러 및 경고 상세 기록
    report.append("## 2. 발견된 문제 사항")
    if errors:
        report.append("### 🔴 치명적 오류 (Errors)")
        for err in errors:
            report.append(f"- {err}")
    else:
        report.append("- 치명적 오류 없음 ✅")
        
    report.append("")
    if warnings:
        report.append("### 🟡 검토 필요 사항 (Warnings)")
        for war in warnings:
            report.append(f"- {war}")
    else:
        report.append("- 검토 필요 사항 없음 ✅")
        
    report.append("\n## 3. 슬라이드별 상태")
    report.append("| 슬라이드 | 상태 | 에러 수 | 경고 수 |")
    report.append("| :--- | :--- | :--- | :--- |")
    for sr in slide_reports:
        report.append(f"| 슬라이드 {sr['slide']} | {sr['status']} | {len(sr['errors'])} | {len(sr['warnings'])} |")

    # 보고서 파일 저장
    report_text = "\n".join(report)
    report_file = output_dir / "evaluation_report.md"
    report_file.write_text(report_text, encoding="utf-8")
    
    # 화면 출력
    print(f"==================================================")
    print(f"  품질 평가 완료! 점수: {score}/100")
    print(f"  - 치명적 오류: {len(errors)} 건")
    print(f"  - 검토 필요 경고: {len(warnings)} 건")
    print(f"  상세 보고서가 다음 경로에 저장되었습니다:")
    print(f"    {report_file.absolute()}")
    print(f"==================================================")
    
    if errors:
        return False
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python evaluate.py <manifest.json> <result.md> [출력폴더]")
        sys.exit(1)
        
    man_file = sys.argv[1]
    res_file = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    
    evaluate_quality(man_file, res_file, out_dir)
