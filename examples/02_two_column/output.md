## 연구 배경 (Research Background)

<!-- 2단 레이아웃: 텍스트 left=66pt(왼쪽), 이미지 left=401pt(오른쪽) -->
<table><tr>
<td valign="top" width="55%">

VLM은 지속적인 개선 노력에도 불구하고, **이미지에 없는 객체를 설명하는 환각(Hallucination) 콘텐츠**를 자주 생성합니다. **Mahajan et al., NeurIPS 2025 (AGE-VLM)**

전역 및 영역 수준 설명을 모두 생성하는 VLM은 **두 캡션 유형 간에 의미적으로 일치하지 않는 캡션**을 생성할 수 있습니다. **Liu et al., CVPR 2024 (GRCap)**

이러한 문제는 다음 실세계 응용에 치명적입니다:
- 공공 CCTV 감시 (이상 탐지)
- 의료 이미지 캡셔닝 (임상 보고서 생성)
- 자율주행
- 원격 감지 및 위성 이미지 해석
- 산업 검사 및 품질 관리
- 로봇공학 및 인간-로봇 상호작용

</td>
<td valign="top" width="45%">

![연구 배경 — AGE-VLM 환각 예시](images/02_01.png)

> AGE-VLM(NeurIPS 2025)에서 발췌한 VLM 환각 문제 예시.  
> 이미지에 없는 객체를 생성하거나 잘못된 수를 보고하는 사례를 보여준다.

*Source: Mahajan et al., NeurIPS 2025 (AGE-VLM)*

</td>
</tr></table>
