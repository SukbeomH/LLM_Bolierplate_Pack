# Claude Code: AI-Native Boilerplate 확장 프로젝트

## 📋 프로젝트 개요

**목표**: 기존 LangChain 기반 AI-Native Boilerplate에 "LangChain 오케스트레이터 ↔ CLI 네이티브 LLM 협업 시스템"을 추가하여, 이미 구독 중인 코딩 전용 LLM(Claude Code/Codex/Gemini CLI 등)의 할당량을 최대한 활용하면서도 안전하고 투명한 작업 흐름을 구축.

**핵심 아이디어**:
- 가벼운 오케스트레이션 LLM (LangChain + GPT-4o-mini/Claude Haiku)
- 무거운 코딩 작업 LLM (CLI 기반: Claude Code/Codex/Gemini CLI)
- MCP + Git을 이용한 공유 컨텍스트 관리
- 구조화된 로깅 + 실시간 대시보드

---

## 🏗️ 아키텍처 요약

```
┌─────────────────────────────────────┐
│  LangChain Orchestrator             │
│  (경량 모델: 분석/가이드/검증)      │
│  - Architect: 코드 읽기 (R/O)      │
│  - Supervisor: 작업 분해             │
│  - Guardian: 검증                   │
│  - Librarian: 지식 동기화           │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ┌────────────────────────────┐
    │  MCP Shared Context        │
    │  - Context Manager Tool    │
    │  - File Lock Manager       │
    │  - Git Workflow State      │
    └────────────────────────────┘
        ▲             ▲
        │             │
   (R/O)│        (R/W)│
        │             │
    ┌───┴──────────────┴──┐
    │  CLI Coding LLM     │
    │  (구독 중인 도구)    │
    │  - Claude Code      │
    │  - Codex CLI        │
    │  - Gemini CLI       │
    │  - OpenCode         │
    │  (실제 코딩 작업)   │
    └────────────────────┘
        │
        ▼
    ┌────────────────────────────┐
    │  Logging & Dashboard       │
    │  - Structured Logger       │
    │    (JSONL + SQLite)        │
    │  - FastAPI Dashboard       │
    │  - Real-time WebSocket     │
    └────────────────────────────┘
```

---

## 🎯 4단계 구현 로드맵

### **Phase 1: 기반 구조** ⭐ (현재 단계)

#### 1-1. MCP Context Manager 도구 추가
**파일**: `langchain_tools/mcp/context_manager.py`

**목표**: MCP 서버에 새로운 도구 추가 → 양쪽 에이전트가 동일한 컨텍스트 접근 가능

**구현 내용**:
```python
class ContextScope(BaseModel):
    """작업 범위를 정의하는 스냅샷"""
    task_id: str              # "task-123"
    branch_name: str          # "feature/task-123"
    files: list[str]          # ["src/auth.py", "tests/auth_test.py"]
    focus_area: str           # "auth_module", "api_endpoint"
    timestamp: str
    accessor: Literal["langchain", "cli"]  # 누가 접근 중인지

class SharedContextMCP:
    """MCP 도구"""
    
    def read_context(task_id: str) -> ContextScope:
        """모든 에이전트가 읽기 가능"""
        # .git/langchain-context.json에서 읽기
    
    def update_context(task_id: str, updates: dict):
        """컨텍스트 업데이트"""
    
    def lock_files(task_id: str, files: list[str], holder: str):
        """파일 수정 중이니 다른 쪽은 건드리지 말 것"""
    
    def unlock_files(task_id: str):
        """수정 완료, 파일 잠금 해제"""
```

**핵심 로직**:
- `.git/langchain-context.json` 파일에 현재 작업 범위 기록
- 누가(langchain/cli) 어떤 파일(files)을 수정 중인지 추적
- 파일 충돌 방지

**검증 기준**:
- MCP 서버가 `read_context` 호출 시 정상적으로 JSON 반환
- `lock_files` 후 다른 접근자 접근 불가
- 로그에 모든 접근 기록됨

---

#### 1-2. Structured Logger 구현
**파일**: `langchain_tools/logging/structured_logger.py`

**목표**: 모든 에이전트 활동을 체계적으로 기록 (JSONL + SQLite)

**구현 내용**:
```python
class StructuredLogger:
    def __init__(self, project_path: str):
        # JSONL: 스트리밍 로그 (실시간 읽기, 디버깅용)
        # SQLite: 구조화된 쿼리 (대시보드, 분석용)
    
    def log_event(self, event: dict):
        """
        event = {
            "task_id": "task-123",
            "phase": "architect" | "cli_execution" | "validation" | "merge",
            "actor": "langchain" | "claude-code" | "cursor-cli" | "gemini-cli",
            "level": "INFO" | "WARNING" | "ERROR",
            "message": "human-readable message",
            "metadata": { ... },  # 추가 컨텍스트
            "duration_ms": 1234
        }
        """
        # JSONL에 기록
        # SQLite에 저장
        # 로그 파일 자동 로테이션
```

**SQLite 스키마**:
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    task_id TEXT,
    phase TEXT,
    actor TEXT,
    level TEXT,
    message TEXT,
    metadata JSON,
    duration_ms REAL
);

CREATE INDEX idx_task_id ON events(task_id);
CREATE INDEX idx_timestamp ON events(timestamp);
CREATE INDEX idx_phase ON events(phase);
```

**검증 기준**:
- 로그 이벤트가 JSONL과 SQLite 양쪽에 저장됨
- 날짜 기준 자동 로테이션 (ex: logs-20260116.jsonl)
- SQLite 쿼리로 특정 task_id의 모든 이벤트 조회 가능
- 대시보드가 이 데이터를 시각화 가능

---

#### 1-3. Git Workflow State Machine
**파일**: `langchain_tools/git/workflow.py`

**목표**: Git을 상태 머신으로 사용 → 현재 작업 단계, 진행 상황, 변경 이력을 추적

**구현 내용**:
```python
class WorkflowPhase(Enum):
    INIT = "init"
    ARCHITECT_ANALYZING = "architect-analyzing"
    ARCHITECT_COMPLETE = "architect-complete"
    CLI_EXECUTING = "cli-executing"
    CLI_COMPLETE = "cli-complete"
    VALIDATION_RUNNING = "validation-running"
    VALIDATION_COMPLETE = "validation-complete"
    MERGE_READY = "merge-ready"
    MERGED = "merged"
    FAILED = "failed"

class GitWorkflowManager:
    def init_workflow(task_id: str, branch: str):
        """새 작업 시작: 브랜치 생성 + 상태 파일 생성"""
    
    def advance_phase(task_id: str, new_phase: WorkflowPhase):
        """단계 진행: 상태 파일 업데이트 + Git 태그"""
    
    def lock_files(task_id: str, files: list[str]):
        """파일 잠금 기록"""
    
    def commit_changes(task_id: str, message: str, author: str):
        """변경사항 커밋 (작성자 기록)"""
```

**Git 상태 파일 (.git/langchain-workflow.json)**:
```json
{
  "task_id": "task-123",
  "branch": "feature/task-123",
  "phase": "cli-executing",
  "started_at": "2026-01-16T11:30:00Z",
  "last_heartbeat": "2026-01-16T11:35:15Z",
  "locked_files": ["src/auth.py"],
  "expected_completion": "2026-01-16T12:00:00Z"
}
```

**Git 태그**:
```bash
git tag task-123-architect-complete
git tag task-123-cli-complete
git tag task-123-validation-complete
git tag task-123-merged
```

**검증 기준**:
- 브랜치 생성 시 상태 파일 자동 생성
- 단계 전환 시 Git 태그 생성
- 커밋 메시지에 작성자 정보 포함 (`[langchain]`, `[claude-code]`)
- `git log --all --decorate`로 전체 이력 확인 가능

---

### **Phase 2: 통합** (다음 단계)

#### 2-1. Architect 노드: 읽기 전용 분석

**파일**: `langchain_tools/agent/nodes/architect.py`

```python
def architect_node(state: AgentState):
    """
    역할:
    1. MCP를 통해 코드베이스 읽기 (쓰기 금지)
    2. 요구사항 분석
    3. 구현 가이드 문서 작성
    4. Git 브랜치 생성 (수정은 안 함)
    5. CLI 실행 준비
    """
    
    task_id = state["task_id"]
    git_mgr.advance_phase(task_id, WorkflowPhase.ARCHITECT_ANALYZING)
    
    # 1. MCP 읽기
    context = mcp_client.read_context(task_id)
    code_files = mcp_client.read_files(context["files"])
    
    # 2. 분석 (경량 LLM: Claude Haiku, GPT-4o-mini)
    analysis = lightweight_llm.invoke(
        f"""
        Code Analysis Task
        
        User Request: {state['user_input']}
        
        Current Code:
        {code_files}
        
        Requirements:
        1. Identify what needs to be changed
        2. List affected files
        3. Describe expected outcomes
        4. Note any security/performance concerns
        """
    )
    
    # 3. 가이드 문서 작성
    guide = f"""
    # Implementation Guide: {task_id}
    
    ## Analysis
    {analysis}
    
    ## Files to Modify
    - {context['files']}
    
    ## Implementation Steps
    1. ...
    2. ...
    
    ## Validation Criteria
    - All tests pass
    - No security regressions
    - Performance within limits
    """
    
    # 4. 브랜치 준비
    git_mgr.init_workflow(task_id, f"feature/{task_id}")
    mcp_client.lock_files(task_id, context["files"], "langchain")
    
    # 5. 로깅
    logger.log_event({
        "task_id": task_id,
        "phase": "architect",
        "actor": "langchain",
        "message": "Architecture analysis complete",
        "metadata": {
            "files_analyzed": len(context["files"]),
            "analysis_length": len(analysis)
        }
    })
    
    git_mgr.advance_phase(task_id, WorkflowPhase.ARCHITECT_COMPLETE)
    
    return {
        **state,
        "guide": guide,
        "files_to_modify": context["files"],
        "next_phase": "cli_execution"
    }
```

**검증 기준**:
- 코드베이스를 읽기 전용으로 분석
- 가이드 문서가 `.langchain-guides/{task_id}.md`에 저장됨
- 파일 잠금이 기록됨
- 로그에 "Architecture analysis complete" 기록됨

---

#### 2-2. CLI Wrapper: 외부 프로세스 호출

**파일**: `langchain_tools/agent/nodes/cli_executor.py`

```python
class CLIExecutor:
    """
    Claude Code/Codex/Gemini CLI 등을 subprocess로 호출
    """
    
    def __init__(self, cli_type: str = "claude-code"):
        # claude-code, codex, gemini-cli, opencode
        self.cli_type = cli_type
    
    def execute(
        self,
        task_id: str,
        branch: str,
        guide: str,
        project_path: str,
        timeout: int = 600  # 10분
    ) -> dict:
        """
        CLI 에이전트 실행
        """
        
        git_mgr = GitWorkflowManager(project_path)
        logger = StructuredLogger(project_path)
        
        try:
            git_mgr.advance_phase(task_id, WorkflowPhase.CLI_EXECUTING)
            
            # 가이드 파일 생성
            guide_path = f"{project_path}/.langchain-guides/{task_id}.md"
            with open(guide_path, "w") as f:
                f.write(guide)
            
            # CLI 호출
            if self.cli_type == "claude-code":
                cmd = [
                    "claude",
                    "--branch", branch,
                    "--context-file", guide_path,
                    "--task-id", task_id,
                    "--mode", "strict",  # MCP 파일 잠금 존중
                    f"Implement according to: {guide_path}"
                ]
            elif self.cli_type == "codex":
                cmd = [
                    "codex-cli",
                    "--task", task_id,
                    "--guide", guide_path,
                    "--branch", branch,
                    "code"
                ]
            # ... 다른 CLI 타입
            
            logger.log_event({
                "task_id": task_id,
                "phase": "cli_execution",
                "actor": self.cli_type,
                "level": "INFO",
                "message": f"Starting CLI execution",
                "metadata": {"command": " ".join(cmd)}
            })
            
            # 프로세스 실행
            process = subprocess.Popen(
                cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 실시간 로그 수집
            for line in process.stdout:
                logger.log_event({
                    "task_id": task_id,
                    "phase": "cli_execution",
                    "actor": self.cli_type,
                    "level": "INFO",
                    "message": line.strip()
                })
            
            returncode = process.wait(timeout=timeout)
            
            if returncode != 0:
                stderr = process.stderr.read()
                logger.log_event({
                    "task_id": task_id,
                    "phase": "cli_execution",
                    "actor": self.cli_type,
                    "level": "ERROR",
                    "message": "CLI execution failed",
                    "metadata": {"error": stderr}
                })
                git_mgr.advance_phase(task_id, WorkflowPhase.FAILED)
                return {"success": False, "error": stderr}
            
            # 변경사항 수집
            changed_files = self._get_changed_files(project_path, branch)
            
            # CLI가 커밋한 변경사항 기록
            git_mgr.commit_changes(
                task_id,
                message=f"Implement: {task_id}",
                author=self.cli_type
            )
            
            git_mgr.advance_phase(task_id, WorkflowPhase.CLI_COMPLETE)
            mcp_client.unlock_files(task_id)  # 파일 잠금 해제
            
            logger.log_event({
                "task_id": task_id,
                "phase": "cli_execution",
                "actor": self.cli_type,
                "level": "INFO",
                "message": "CLI execution complete",
                "metadata": {
                    "files_modified": len(changed_files),
                    "files": changed_files
                }
            })
            
            return {
                "success": True,
                "files_modified": changed_files,
                "branch": branch
            }
        
        except subprocess.TimeoutExpired:
            logger.log_event({
                "task_id": task_id,
                "phase": "cli_execution",
                "actor": self.cli_type,
                "level": "ERROR",
                "message": f"CLI execution timeout (>{timeout}s)"
            })
            git_mgr.advance_phase(task_id, WorkflowPhase.FAILED)
            return {"success": False, "error": "Timeout"}
    
    def _get_changed_files(self, project_path: str, branch: str) -> list[str]:
        """현재 브랜치에서 main과의 diff 파일 목록"""
        result = subprocess.run(
            ["git", "diff", "--name-only", "main..HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n")

def cli_execution_node(state: AgentState):
    """LangGraph 노드"""
    cli = CLIExecutor(cli_type="claude-code")  # 또는 다른 타입
    result = cli.execute(
        task_id=state["task_id"],
        branch=state["files_to_modify"],
        guide=state["guide"],
        project_path=state["project_path"]
    )
    
    return {
        **state,
        "cli_result": result,
        "next_phase": "validation"
    }
```

**검증 기준**:
- CLI 프로세스가 정상적으로 시작됨
- 가이드 파일이 `.langchain-guides/{task_id}.md`에 전달됨
- CLI 실행 로그가 실시간으로 기록됨
- 완료 후 변경된 파일 목록이 수집됨
- Git 커밋에 작성자 정보 포함

---

#### 2-3. Guardian 노드: 검증

**파일**: `langchain_tools/agent/nodes/guardian.py`

```python
def validation_node(state: AgentState):
    """
    Guardian: CLI 결과 검증
    1. 테스트 실행
    2. 코드 리뷰
    3. 보안 검사
    4. 의도 일치 확인
    """
    
    task_id = state["task_id"]
    git_mgr = GitWorkflowManager(state["project_path"])
    logger = StructuredLogger(state["project_path"])
    
    git_mgr.advance_phase(task_id, WorkflowPhase.VALIDATION_RUNNING)
    
    logger.log_event({
        "task_id": task_id,
        "phase": "validation",
        "actor": "langchain",
        "message": "Starting validation"
    })
    
    # 1. 테스트 실행
    test_result = subprocess.run(
        ["pytest", "-v"],
        cwd=state["project_path"],
        capture_output=True,
        text=True
    )
    
    tests_passed = test_result.returncode == 0
    
    logger.log_event({
        "task_id": task_id,
        "phase": "validation",
        "actor": "langchain",
        "message": f"Tests {'passed' if tests_passed else 'failed'}",
        "metadata": {
            "stdout": test_result.stdout,
            "stderr": test_result.stderr
        }
    })
    
    # 2. 코드 리뷰
    changed_files = state["cli_result"]["files_modified"]
    review_prompt = f"""
    Review the following changes:
    
    Original Requirement: {state['user_input']}
    
    Changed Files: {changed_files}
    
    Check:
    1. Meets requirements
    2. No breaking changes
    3. Code quality acceptable
    4. Documentation updated if needed
    
    Provide detailed review.
    """
    
    review = lightweight_llm.invoke(review_prompt)
    
    logger.log_event({
        "task_id": task_id,
        "phase": "validation",
        "actor": "langchain",
        "message": "Code review complete",
        "metadata": {"review": review}
    })
    
    # 3. 최종 결정
    validation_passed = tests_passed and "approved" in review.lower()
    
    if validation_passed:
        git_mgr.advance_phase(task_id, WorkflowPhase.VALIDATION_COMPLETE)
        logger.log_event({
            "task_id": task_id,
            "phase": "validation",
            "actor": "langchain",
            "level": "INFO",
            "message": "Validation passed - ready to merge"
        })
    else:
        git_mgr.advance_phase(task_id, WorkflowPhase.FAILED)
        logger.log_event({
            "task_id": task_id,
            "phase": "validation",
            "actor": "langchain",
            "level": "ERROR",
            "message": "Validation failed - manual review needed"
        })
    
    return {
        **state,
        "validation_passed": validation_passed,
        "review": review,
        "tests_passed": tests_passed,
        "next_phase": "merge" if validation_passed else "failed"
    }
```

**검증 기준**:
- pytest 실행 후 결과 기록
- 코드 리뷰 프롬프트 정상 실행
- 검증 결과 (PASSED/FAILED) 기록됨

---

#### 2-4. Merge 노드

**파일**: `langchain_tools/agent/nodes/merge.py`

```python
def merge_node(state: AgentState):
    """
    최종 병합: feature 브랜치 → main
    """
    
    if not state.get("validation_passed"):
        return state
    
    task_id = state["task_id"]
    git_mgr = GitWorkflowManager(state["project_path"])
    logger = StructuredLogger(state["project_path"])
    
    try:
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=state["project_path"],
            check=True
        )
        
        subprocess.run(
            ["git", "merge", state["files_to_modify"], 
             "-m", f"Merge {task_id}: {state['user_input'][:50]}"],
            cwd=state["project_path"],
            check=True
        )
        
        git_mgr.advance_phase(task_id, WorkflowPhase.MERGED)
        
        logger.log_event({
            "task_id": task_id,
            "phase": "merge",
            "actor": "langchain",
            "level": "INFO",
            "message": "Successfully merged to main",
            "metadata": {"branch": state["files_to_modify"]}
        })
        
        return {**state, "merged": True}
    
    except subprocess.CalledProcessError as e:
        logger.log_event({
            "task_id": task_id,
            "phase": "merge",
            "actor": "langchain",
            "level": "ERROR",
            "message": f"Merge failed: {str(e)}"
        })
        return {**state, "merged": False}
```

---

### **Phase 3: 모니터링** (대시보드)

#### 3-1. FastAPI 대시보드

**파일**: `langchain_tools/dashboard/api.py`

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import sqlite3
import asyncio

app = FastAPI()

@app.websocket("/ws/logs/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: str):
    """실시간 로그 스트리밍"""
    await websocket.accept()
    
    logger = StructuredLogger(".")
    
    try:
        while True:
            # 최신 로그 조회
            logs = logger.query_events(
                task_id=task_id,
                limit=50,
                order="DESC"
            )
            
            await websocket.send_json({
                "logs": logs,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await asyncio.sleep(1)
    except Exception as e:
        await websocket.close()

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """작업 상태 조회"""
    git_mgr = GitWorkflowManager(".")
    state = git_mgr.read_state(task_id)
    
    logger = StructuredLogger(".")
    events = logger.query_events(task_id=task_id)
    
    return {
        "task_id": task_id,
        "phase": state.phase.value,
        "branch": state.branch,
        "locked_files": state.locked_files,
        "started_at": state.started_at,
        "last_heartbeat": state.last_heartbeat,
        "events_count": len(events)
    }

@app.get("/dashboard/{task_id}")
async def dashboard_html(task_id: str):
    """대시보드 HTML"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangChain Task Monitor: {task_id}</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Courier New', monospace;
                background: #0d1117;
                color: #c9d1d9;
                padding: 20px;
            }
            
            .container { max-width: 1400px; margin: 0 auto; }
            
            h1 {
                margin-bottom: 30px;
                font-size: 24px;
                color: #58a6ff;
            }
            
            .phases {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .phase {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 15px;
            }
            
            .phase-name {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 14px;
            }
            
            .phase-bar {
                background: #30363d;
                border-radius: 3px;
                height: 8px;
                overflow: hidden;
            }
            
            .phase-progress {
                height: 100%;
                background: #238636;
                transition: width 0.3s;
            }
            
            .phase-progress.active {
                background: #58a6ff;
            }
            
            .phase-progress.error {
                background: #f85149;
            }
            
            .phase-status {
                font-size: 12px;
                margin-top: 5px;
                color: #8b949e;
            }
            
            .logs-section {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 15px;
            }
            
            .logs-section h2 {
                font-size: 16px;
                margin-bottom: 15px;
                color: #58a6ff;
            }
            
            .logs {
                background: #010409;
                border: 1px solid #30363d;
                border-radius: 4px;
                height: 400px;
                overflow-y: auto;
                padding: 10px;
                font-size: 12px;
                line-height: 1.5;
            }
            
            .log-entry {
                padding: 5px 0;
                border-bottom: 1px solid #30363d;
                word-break: break-all;
            }
            
            .log-entry:last-child {
                border-bottom: none;
            }
            
            .log-timestamp {
                color: #8b949e;
                margin-right: 10px;
            }
            
            .log-actor {
                color: #79c0ff;
                font-weight: bold;
                margin-right: 10px;
            }
            
            .log-message {
                color: #c9d1d9;
            }
            
            .log-error .log-message {
                color: #f85149;
            }
            
            .log-success .log-message {
                color: #238636;
            }
            
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #010409;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #30363d;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #484f58;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Task Monitor: {task_id}</h1>
            
            <div class="phases">
                <div class="phase">
                    <div class="phase-name">📐 Architect</div>
                    <div class="phase-bar">
                        <div class="phase-progress" id="phase-architect" style="width: 0%"></div>
                    </div>
                    <div class="phase-status" id="phase-architect-status">Pending</div>
                </div>
                
                <div class="phase">
                    <div class="phase-name">⚙️ CLI Execution</div>
                    <div class="phase-bar">
                        <div class="phase-progress" id="phase-cli" style="width: 0%"></div>
                    </div>
                    <div class="phase-status" id="phase-cli-status">Pending</div>
                </div>
                
                <div class="phase">
                    <div class="phase-name">✅ Validation</div>
                    <div class="phase-bar">
                        <div class="phase-progress" id="phase-validation" style="width: 0%"></div>
                    </div>
                    <div class="phase-status" id="phase-validation-status">Pending</div>
                </div>
                
                <div class="phase">
                    <div class="phase-name">🔀 Merge</div>
                    <div class="phase-bar">
                        <div class="phase-progress" id="phase-merge" style="width: 0%"></div>
                    </div>
                    <div class="phase-status" id="phase-merge-status">Pending</div>
                </div>
            </div>
            
            <div class="logs-section">
                <h2>📋 Live Logs</h2>
                <div class="logs" id="logs"></div>
            </div>
        </div>
        
        <script>
            const taskId = "{task_id}";
            const ws = new WebSocket(`ws://localhost:8000/ws/logs/${{taskId}}`);
            
            const phaseMap = {
                "architect-analyzing": { id: "architect", progress: 25, status: "Running" },
                "architect-complete": { id: "architect", progress: 100, status: "Complete" },
                "cli-executing": { id: "cli", progress: 50, status: "Running" },
                "cli-complete": { id: "cli", progress: 100, status: "Complete" },
                "validation-running": { id: "validation", progress: 50, status: "Running" },
                "validation-complete": { id: "validation", progress: 100, status: "Complete" },
                "merged": { id: "merge", progress: 100, status: "Complete" },
                "failed": { id: "current", progress: 100, status: "Failed", error: true }
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                const logsDiv = document.getElementById("logs");
                
                // 로그 업데이트
                logsDiv.innerHTML = data.logs.map(log => {
                    const timestamp = new Date(log.timestamp).toLocaleTimeString();
                    const className = log.level === "ERROR" ? "log-error" : 
                                    log.level === "INFO" && log.message.includes("complete") ? "log-success" : "";
                    return `
                        <div class="log-entry ${className}">
                            <span class="log-timestamp">${timestamp}</span>
                            <span class="log-actor">[${log.actor}]</span>
                            <span class="log-message">${log.message}</span>
                        </div>
                    `;
                }).join("");
                
                // 페이즈 업데이트
                logsDiv.scrollTop = logsDiv.scrollHeight;
            };
        </script>
    </body>
    </html>
    """.format(task_id=task_id))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**실행 방법**:
```bash
python -m langchain_tools.dashboard.api
# http://localhost:8000/dashboard/task-123
```

---

### **Phase 4: 최적화** (향후)

- 다중 CLI 백엔드 지원 (Codex, Claude Code, Gemini CLI 동시 사용)
- 자동 롤백 시나리오
- 인증/권한 관리 (GitHub API, org level)
- 성능 최적화 (캐싱, 병렬 처리)

---

## 📝 구현 시 주의사항

### ✅ 해야 할 것

1. **MCP 도구 격리**: 읽기/쓰기 권한을 엄격히 분리
   - Architect → read only
   - CLI → read-write (파일 잠금 존중)

2. **Git 상태 동기화**: 모든 상태 변화는 Git에 기록
   - 커밋 메시지에 작성자 포함
   - 태그로 마일스톤 기록

3. **로깅 중복성**: JSONL + SQLite 양쪽 기록
   - JSONL: 스트리밍(터미널/디버깅)
   - SQLite: 쿼리/분석(대시보드)

4. **타임아웃 설정**: CLI 실행에는 반드시 타임아웃
   - 기본 600초(10분)
   - 환경변수로 제어 가능

5. **에러 처리**: 각 단계마다 try-except + 로깅
   - 실패 시 상태 업데이트 + 로그 기록
   - 수동 개입 지점 명확히

### ❌ 하지 말아야 할 것

1. **MCP 없이 직접 파일 접근**
   - 반드시 MCP Context Manager 통해 접근
   - 충돌 감지 가능

2. **로그 없는 작업**
   - 모든 에이전트 활동은 logging 필수
   - 추후 디버깅/감사 추적 불가능

3. **상태 파일 .gitignore**
   - `.git/langchain-*.json` 등은 Git 추적 제외
   - 하지만 로그는 추적 가능하게 (`.langchain-logs/` 포함)

4. **CLI 결과를 바로 사용**
   - 항상 Guardian 검증 거친 후 병합
   - 자동화된 테스트 필수

---

## 🎯 정리

이 시스템의 핵심은:

```
LangChain (경량, 오케스트레이션)
    ↓
    ├─ [구독 중인 CLI LLM에 일 넘김]
    │  (Claude Code, Codex, Gemini CLI 등)
    │
    └─ [MCP + Git을 통해 상태 동기화]
       (공유 컨텍스트, 파일 잠금, 워크플로우)
    
    ↓
    
[체계적인 로깅]
    └─ JSONL (스트리밍) + SQLite (쿼리)
    
    ↓
    
[실시간 모니터링]
    └─ FastAPI + WebSocket 대시보드
```

**장점**:
- ✅ 비용 효율: 구독 활용 극대화
- ✅ 안전성: Git 기반 감사 추적
- ✅ 투명성: 실시간 대시보드
- ✅ 확장성: 여러 CLI 백엔드 지원 가능

**다음 단계**: Phase 1 구현 후, 실제 워크플로우 테스트로 검증!

---

## 📞 질문 및 확인사항

구현 중 다음 부분에 대해 의견 부탁드립니다:

1. **CLI 타입**: Claude Code, Codex, Gemini CLI 중 먼저 구현할 것은?
   - 제안: Claude Code (공식 문서 가장 좋음)

2. **파일 잠금 방식**: 위 예시 외에 다른 전략이 있을까?
   - 예: Git branch protection + CODEOWNERS?

3. **대시보드 백엔드**: FastAPI 외에 다른 옵션?
   - 예: 기존 Next.js 대시보드 개선?

4. **배포 환경**: 로컬만? 아니면 원격 서버도?
   - Git push → GitHub Actions 트리거?

미리 좋은 피드백 주신 것 같아서, 우선 Phase 1부터 시작하겠습니다! 🚀
