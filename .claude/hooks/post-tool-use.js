#!/usr/bin/env node
/**
 * post-tool-use.js - PostToolUse 훅 스크립트
 *
 * 목적: AI가 도구를 사용하여 코드를 생성/수정한 직후 자동으로 포매팅과 린트를 실행합니다.
 * AI는 기본적으로 90%의 포매팅만 완료하는 경향이 있으므로, 이 훅이 나머지 10%를 처리하여
 * CI 단계에서 포매팅 오류가 발생하지 않도록 합니다.
 *
 * 동작 방식:
 * 1. 도구 사용 직후 트리거됨
 * 2. scripts/core/detect_stack.sh를 호출하여 현재 스택 감지
 * 3. 감지된 스택에 맞는 포매터/린터 자동 실행
 *    - Node.js: Prettier, ESLint
 *    - Python: Black, Ruff
 *    - Go: gofmt, golint
 *    - Rust: rustfmt, clippy
 *
 * 향후 확장: detect_stack.sh가 구현되면 (Phase 4) 완전히 자동화됩니다.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 색상 출력을 위한 유틸리티
const colors = {
	reset: '\x1b[0m',
	green: '\x1b[32m',
	yellow: '\x1b[33m',
	red: '\x1b[31m',
	blue: '\x1b[34m',
};

function log(message, color = 'reset') {
	console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * 스택 감지 스크립트 실행
 * Phase 4에서 구현될 detect_stack.sh를 호출합니다.
 */
function detectStack() {
	const projectRoot = process.cwd();
	const detectScript = path.join(projectRoot, 'scripts', 'core', 'detect_stack.sh');

	if (!fs.existsSync(detectScript)) {
		log('⚠️  Warning: detect_stack.sh not found. Running basic detection...', 'yellow');
		log('   This will be fully implemented in Phase 4.', 'yellow');
		return detectStackBasic();
	}

	try {
		// 스크립트를 source하여 환경 변수 로드
		const output = execSync(`bash -c 'source ${detectScript} && echo "STACK=$DETECTED_STACK" && echo "PM=$DETECTED_PACKAGE_MANAGER"'`, {
			encoding: 'utf-8',
			cwd: projectRoot,
		});

		const stackMatch = output.match(/STACK=(.+)/);
		const pmMatch = output.match(/PM=(.+)/);

		return {
			stack: stackMatch ? stackMatch[1] : null,
			packageManager: pmMatch ? pmMatch[1] : null,
		};
	} catch (error) {
		log(`⚠️  Stack detection failed: ${error.message}`, 'yellow');
		return detectStackBasic();
	}
}

/**
 * 기본 스택 감지 (Phase 4 전까지 사용)
 * 프로젝트 루트의 파일을 확인하여 스택을 추론합니다.
 */
function detectStackBasic() {
	const projectRoot = process.cwd();
	const files = fs.readdirSync(projectRoot);

	if (files.includes('package.json')) {
		return { stack: 'node', packageManager: 'npm' };
	}
	if (files.includes('pyproject.toml') || files.includes('requirements.txt')) {
		return { stack: 'python', packageManager: 'pip' };
	}
	if (files.includes('go.mod')) {
		return { stack: 'go', packageManager: 'go' };
	}
	if (files.includes('Cargo.toml')) {
		return { stack: 'rust', packageManager: 'cargo' };
	}

	return { stack: null, packageManager: null };
}

/**
 * 스택에 맞는 포매터/린터 실행
 */
function runFormatter(stack, packageManager) {
	log('🔧 [HOOK] Running post-tool formatting...', 'blue');

	try {
		switch (stack) {
			case 'node':
				runNodeFormatter(packageManager);
				break;
			case 'python':
				runPythonFormatter();
				break;
			case 'go':
				runGoFormatter();
				break;
			case 'rust':
				runRustFormatter();
				break;
			default:
				log('⚠️  Unknown stack. Skipping formatting.', 'yellow');
				return;
		}
		log('✅ [HOOK] Formatting completed', 'green');
	} catch (error) {
		log(`❌ [HOOK] Formatting failed: ${error.message}`, 'red');
		// 실패해도 계속 진행 (경고만)
	}
}

function runNodeFormatter(packageManager) {
	const projectRoot = process.cwd();
	const packageJson = path.join(projectRoot, 'package.json');

	if (!fs.existsSync(packageJson)) {
		return;
	}

	// package.json의 scripts 확인
	const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf-8'));

	if (pkg.scripts && pkg.scripts.format) {
		log('   Running: npm run format', 'blue');
		execSync('npm run format', { stdio: 'inherit', cwd: projectRoot });
	} else if (packageManager === 'npm' && fs.existsSync(path.join(projectRoot, 'node_modules', '.bin', 'prettier'))) {
		log('   Running: npx prettier --write .', 'blue');
		execSync('npx prettier --write .', { stdio: 'inherit', cwd: projectRoot });
	}

	if (pkg.scripts && pkg.scripts.lint) {
		log('   Running: npm run lint', 'blue');
		execSync('npm run lint', { stdio: 'inherit', cwd: projectRoot });
	}
}

function runPythonFormatter() {
	const projectRoot = process.cwd();

	// Black 사용 시도
	if (execSync('which black', { encoding: 'utf-8', stdio: 'pipe' }).trim()) {
		log('   Running: black .', 'blue');
		execSync('black .', { stdio: 'inherit', cwd: projectRoot });
	}

	// Ruff 사용 시도
	if (execSync('which ruff', { encoding: 'utf-8', stdio: 'pipe' }).trim()) {
		log('   Running: ruff check --fix .', 'blue');
		execSync('ruff check --fix .', { stdio: 'inherit', cwd: projectRoot });
	}
}

function runGoFormatter() {
	log('   Running: gofmt -w .', 'blue');
	execSync('gofmt -w .', { stdio: 'inherit' });
}

function runRustFormatter() {
	log('   Running: cargo fmt', 'blue');
	execSync('cargo fmt', { stdio: 'inherit' });
}

// 메인 실행
function main() {
	const { stack, packageManager } = detectStack();

	if (!stack) {
		log('⚠️  Could not detect project stack. Skipping formatting.', 'yellow');
		return;
	}

	log(`📋 Detected stack: ${stack} (${packageManager || 'unknown'})`, 'blue');
	runFormatter(stack, packageManager);
}

// 스크립트가 직접 실행된 경우에만 실행
if (require.main === module) {
	main();
}

module.exports = { detectStack, runFormatter };

