# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

`whiplash-loop`는 **OpenAI Codex CLI 스킬 플러그인**으로, 코드 변경 작업에 대해 고강도 worker-reviewer 재시도 루프를 구현한다. 한국어 키워드 `위플래쉬` 또는 `플레처소환`으로 트리거되며, 독립 실행 애플리케이션이 아닌 Codex 에이전트 생태계의 플러그인이다.

- GitHub: `tteggu87/whiplash-loop`
- 빌드/테스트/린트 명령 없음 — 순수 선언형 설정 파일(TOML, YAML, JSON, Markdown)로만 구성

## 아키텍처

### 2계층 구조

**1. 스킬 정의** (`.codex/skills/whiplash-loop/`)
- `SKILL.md` — 메인 스킬 프롬프트. 트리거 조건, 루프 상태 추적, 리뷰어 계약(verdict/findings/orders/proof/risk/loop-control), 톤 규칙, 5라운드 상한 정의. Codex가 스킬 활성화 시 읽는 진입점.
- `agents/openai.yaml` — 스킬 인터페이스 메타데이터 (display name, implicit invocation 플래그).
- `references/whiplash-reviewer-profile.md` — Named agent를 지원하지 않는 환경용 폴백 리뷰어 페르소나.
- `references/whiplash-reviewer-verdict.schema.json` — 머신 가독 verdict 객체의 JSON Schema.
- `evals/evals.json` — 3개 평가 케이스: 코드 작업 트리거, 리뷰 트리거, 설명 요청 시 스킵.

**2. Named Agent** (`.codex/agents/`)
- `whiplash-reviewer.toml` — 리뷰어 에이전트 정의. 모델(`gpt-5.4`), 샌드박스(`read-only`), 음성 프로필, 루프 정책, 구조화된 verdict 계약 포함.
- `whiplash-reviewer-verdict.schema.json` — 에이전트 수준에서 직접 참조용 verdict 스키마 사본.

### 루프 동작 방식
1. `위플래쉬` 또는 `플레처소환` + 코드 작업으로 트리거
2. Worker가 구현/수정 패스 수행
3. Reviewer가 **Round 1 강제 리젝션** (보정용)
4. Round 2~5: 증거 기반 pass/fail 판정
5. 종료 조건: pass, 인간 에스컬레이션, 비수렴, 또는 Round 5 도달

### 핵심 설계 결정
- 리뷰어 계약은 6개 섹션 필수: Verdict, Findings, Orders to worker, Proof required, Residual risk, Loop control
- 머신 verdict JSON은 내부용 — 챗 출력에 raw JSON 노출 금지
- `whiplash-reviewer-profile.md`는 named agent 미지원 런타임용 폴백
- Verdict 스키마는 `skills/`와 `agents/` 양쪽에 의도적 중복 배치 (독립 해석 보장)

## 파일 수정 시 주의사항

- `SKILL.md` 수정 시 → `whiplash-reviewer.toml`의 `developer_instructions`와 일관성 유지
- Verdict 스키마 수정 시 → 양쪽 사본(`references/` + `.codex/agents/`) 동시 수정
- `evals/evals.json` 수정 시 → 트리거/비트리거 경계 케이스 포함 유지
- 톤 규칙: 영화 대사 인용/패러프레이즈 금지, 슬러/위협/신원 기반 모욕 금지
