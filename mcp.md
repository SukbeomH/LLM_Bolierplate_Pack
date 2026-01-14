The user wants to know how to install the 5 specific MCP servers (Serena, Codanna, Shrimp Task Manager, Context7, Chrome DevTools) referenced in their configuration files.

I need to provide the official installation methods for each, tailored to the user's environment (macOS, likely Apple Silicon based on `/opt/homebrew`, using `zsh`, `uv`, and `mise`).

**Plan:**

1. **Serena:** Search for `oraios/serena` to confirm installation (likely `uv` or `pip`).
2. **Codanna:** Search for `codanna` installation (likely Homebrew or curl script given the path `/opt/homebrew/bin/codanna`).
3. **Shrimp Task Manager:** Search for `mcp-shrimp-task-manager`. If it's a private/custom tool from the "Antigravity" boilerplate, I will instruct on how to build it locally (npm install & build).
4. **Context7:** Verify `@upstash/context7-mcp` on npm.
5. **Chrome DevTools:** Verify `chrome-devtools-mcp` on npm.

I will then summarize the installation commands for the user.

**Search Queries:**

1. `github oraios serena mcp install`
2. `codanna mcp install homebrew`
3. `codanna ai cli install`
4. `npm @upstash/context7-mcp`
5. `npm chrome-devtools-mcp`
6. `github mcp-shrimp-task-manager`

Let's execute the search to be precise.
`mcp-mute-runner.js`가 정상적으로 작동하려면, 설정 파일(`config.json`)에 지정된 경로에 실제 **실행 파일(binary)**이나 **프로젝트 파일**이 존재해야 합니다.

공식 GitHub 저장소와 문서를 바탕으로 각 MCP의 설치 방법을 정리해 드립니다.

> **중요:** 설치 후 실행 파일의 위치가 `config.json`에 적힌 경로와 일치하는지 꼭 확인하세요.

---

### 1. Serena (Python/uv 기반)

Serena는 별도의 로컬 설치 없이 `uvx`로 실행하는 것이 공식 권장 방법이지만, 매번 다운로드하는 지연을 줄이려면 `uv tool`로 설치하거나 로컬에 클론할 수 있습니다.

* **공식 저장소:** [oraios/serena](https://github.com/oraios/serena)
* **설치 방법 (uv 사용 시):**
이미 `uvx`를 사용하도록 설정되어 있으므로, **별도 설치가 필요 없습니다.** (실행 시 자동 캐싱됨)
만약 로컬에서 개발하거나 수정해서 쓰고 싶다면:
```bash
# 프로젝트 클론
git clone https://github.com/oraios/serena.git
cd serena

# 의존성 설치 (가상환경)
uv sync

```



---

### 2. Codanna (Rust 기반)

Codanna는 Rust로 작성된 고성능 코드 분석 도구입니다. `config.json`에 `/opt/homebrew/bin/codanna`로 설정되어 있으므로, 바이너리를 해당 위치에 두거나 Homebrew로 설치해야 합니다.

* **공식 저장소:** [bartolli/codanna](https://github.com/bartolli/codanna)
* **설치 방법:**
**방법 A: Cargo (Rust 패키지 매니저) 사용 [권장]**
```bash
# Rust 설치가 안 되어 있다면
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Codanna 설치
cargo install codanna --all-features

# 주의: 설치된 위치는 보통 ~/.cargo/bin/codanna 입니다.
# config.json의 경로를 ~/.cargo/bin/codanna 로 수정하거나, 심볼릭 링크를 거세요.
sudo ln -s ~/.cargo/bin/codanna /opt/homebrew/bin/codanna

```


**방법 B: Homebrew (Tap이 있는 경우)**
공식 Tap이 없다면 Cargo 설치가 가장 확실합니다.

---

### 3. Shrimp Task Manager (Node.js 기반)

이 도구는 NPM 레지스트리에 배포된 패키지가 아니라, GitHub 소스를 직접 받아서 빌드해야 하는 것으로 보입니다. 사용자의 설정 경로(`.../dist/index.js`)에 맞추려면 **빌드(Build)** 과정이 필수입니다.

* **공식 저장소:** [cjo4m06/mcp-shrimp-task-manager](https://github.com/cjo4m06/mcp-shrimp-task-manager)
* **설치 및 빌드 방법:**
```bash
# 1. 설정 파일에 적힌 경로로 이동 (폴더가 없다면 생성)
mkdir -p /Users/sukbeom/Desktop/side
cd /Users/sukbeom/Desktop/side

# 2. 저장소 클론
git clone https://github.com/cjo4m06/mcp-shrimp-task-manager.git

# 3. 프로젝트 폴더로 이동
cd mcp-shrimp-task-manager

# 4. 의존성 설치 및 빌드 (이 과정을 거쳐야 dist/index.js가 생성됩니다)
npm install
npm run build

```



---

### 4. Context7 & Chrome DevTools (NPM 패키지)

이 두 가지는 NPM 공식 패키지입니다. `config.json`에서 `npx`를 사용하도록 설정했으므로, **별도 설치 없이 즉시 실행 가능**합니다. (실행 시 최신 버전을 자동으로 받아옵니다)

* **Context7:** [@upstash/context7-mcp](https://www.npmjs.com/package/@upstash/context7-mcp)
* **Chrome DevTools:** [chrome-devtools-mcp](https://www.npmjs.com/package/chrome-devtools-mcp)

만약 실행 속도를 높이고 싶다면 전역으로 설치하고 경로를 `npx` 대신 `node`로 바꿀 수 있지만, 현재 설정(`npx -y ...`) 그대로 두시는 것을 추천합니다.

---

### ✅ 요약: 지금 실행해야 할 명령어

터미널을 열고 다음 명령어들을 순서대로 실행하여 환경을 준비해 주세요.

```bash
# 1. Shrimp Task Manager 설치 및 빌드 (필수)
cd /Users/sukbeom/Desktop/side
git clone https://github.com/cjo4m06/mcp-shrimp-task-manager.git
cd mcp-shrimp-task-manager
npm install && npm run build

# 2. Codanna 설치 (Rust 필요)
cargo install codanna --all-features
# 설치 후 경로 확인: which codanna
# 만약 /opt/homebrew/bin/codanna 가 아니라면,
# config.json 에서 "command" 경로를 `which codanna` 결과로 수정하세요.

```
