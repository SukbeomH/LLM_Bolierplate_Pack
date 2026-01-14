# 🤖 AI-Native 팀 온보딩 가이드

> "우리는 AI를 단순 코딩 도구가 아닌, 협업하는 **에이전트(Agent)** 로 대우합니다."

이 문서는 AI 에이전트(Claude, Cursor, Antigravity)와 효과적으로 협업하기 위한 팀의 표준 가이드입니다.

---

## 🏗️ 1. 워크플로우 표준 (RIPER-5)

모든 작업은 **RIPER-5** 원칙을 따릅니다:

1.  **Research (조사)**: 구현 전 관련 코드나 문서를 에이전트에게 읽게 하세요.
    - _"이 기능을 구현하기 위해 참고할 파일들을 먼저 검토해줘."_
2.  **Implementation Plan (계획)**: `implementation_plan.md`를 작성하고 승인받으세요.
    - _"구현하기 전에 계획을 세워서 보여줘."_
3.  **Production (구현)**: 승인된 계획대로 코드를 작성합니다.
    - _"계획대로 진행해."_
4.  **Evaluate (검증)**: `langchain-tools verify` 명령으로 검증하세요.
    - _"작성한 코드를 검증해줘."_
5.  **Record (기록)**: 실패 경험이나 배운 점을 `CLAUDE.md`에 기록하세요.
    - _"이번 버그의 원인과 해결책을 Lessons Learned에 추가해."_

---

## 🛠️ 2. MCP 도구 활용

우리는 Docker 컨테이너로 실행되는 강력한 MCP 도구들을 사용합니다.

| 도구 | 역할 | 명령어 예시 |
|------|------|------------|
| **Serena** | 📍 심볼/코드 검색 | "User 클래스의 정의를 보여줘" |
| **Codanna** | 🧠 시맨틱 분석 | "인증 로직에서 보안 취약점 찾아줘" |
| **Shrimp** | 🦐 작업/티켓 관리 | "로그인 페이지 구현 작업을 생성해줘" |

> 💡 **Tip**: 에이전트가 코드를 잘 못 찾는다면, "Serena를 사용해서 찾아봐"라고 명시적으로 지시하세요.

---

## 🧠 3. 지식 관리 (Compounding Knowledge)

우리 팀은 **실패를 자산으로 만듭니다**.

- **CLAUDE.md**: 프로젝트 루트에 위치하며, 팀의 규칙과 'Lessons Learned'가 저장됩니다.
- **동기화**: 다른 프로젝트에서 배운 점을 가져오려면 다음 명령을 사용하세요.
  ```bash
  uv run langchain-tools sync-knowledge --from ../other-project --to .
  ```

---

## 🚨 4. 트러블슈팅

**Q: 에이전트가 계속 같은 실수를 반복해요.**
A: `CLAUDE.md`의 `Rules` 섹션에 해당 실수를 하지 말라는 규칙을 추가하고, 에이전트에게 "CLAUDE.md를 다시 읽어봐"라고 하세요.

**Q: MCP 도구가 작동하지 않아요.**
A: Docker 컨테이너가 실행 중인지 확인하세요.
   ```bash
   docker ps
   # mcp-serena, mcp-codanna 등이 보여야 함
   ```

**Q: Antigravity에서 연결이 끊겨요.**
A: `npx` 경로 문제일 수 있습니다. `.mcp.json`에서 절대 경로를 사용했는지 확인하세요.

---

## 🏁 5. 시작하기

새 프로젝트를 시작할 때:

```bash
# 1. 보일러플레이트 주입
uv run langchain-tools inject .

# 2. 의존성 설치
uv sync

# 3. 에디터 재시작 (MCP 로드)
```

**Happy Coding with Agents!** 🚀
