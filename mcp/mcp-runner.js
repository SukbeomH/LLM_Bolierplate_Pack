#!/usr/bin/env node
const { spawn } = require('child_process');

// 실행 시 전달받은 인자들 (node 경로와 이 스크립트 경로 제외)
// 예: ["uvx", "--from", "...", "start-mcp-server", ...]
const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('[Error] 실행할 명령어가 전달되지 않았습니다.');
  process.exit(1);
}

// 첫 번째 인자는 명령어(예: uvx, npx, node), 나머지는 옵션
const command = args[0];
const commandArgs = args.slice(1);

// 실제 프로세스 실행
const proc = spawn(command, commandArgs, {
  env: process.env, // 부모(MCP 클라이언트)가 전달한 환경변수(env)를 그대로 물려받음
  stdio: ['inherit', 'pipe', 'inherit'], // stdout만 가로채기
  shell: false // args 배열을 정확히 전달하기 위해 shell 모드 끔 (보안상/파싱상 더 안전)
});

proc.stdout.on('data', (data) => {
  const output = data.toString();

  output.split('\n').forEach((line) => {
    if (!line.trim()) return;

    // 1. JSON-RPC 메시지 (중괄호로 시작) -> 정상 출력 (stdout)
    if (line.trim().startsWith('{')) {
      process.stdout.write(line + '\n');
    }
    // 2. 일반 로그/텍스트 -> 에러 채널(stderr)로 우회 (연결 끊김 방지)
    else {
      console.error(`[Filtered]: ${line}`);
    }
  });
});

proc.on('error', (err) => {
  console.error(`[Spawn Error] ${err.message}`);
});

proc.on('close', (code) => {
  process.exit(code);
});
