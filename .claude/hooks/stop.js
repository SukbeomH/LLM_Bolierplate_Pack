#!/usr/bin/env node
/**
 * stop.js - Stop 훅 스크립트
 *
 * 목적: 위험한 작업(DB 마이그레이션, 인프라 변경 등) 직후 AI가 자동으로 진행하기 전에
 * 반드시 사용자의 검토와 승인을 받도록 작업을 중단합니다.
 *
 * 트리거 조건 (CLAUDE.md에 명시된 대로):
 * - 데이터베이스 마이그레이션 생성/수정
 * - 인프라 변경 (Terraform 파일 수정)
 * - 환경 변수 변경 (.env 파일 수정)
 * - 의존성 변경 (package.json, requirements.txt 등)
 * - 인증/권한 관련 코드 변경
 *
 * 동작 방식:
 * 1. Git diff를 분석하여 위험한 파일 변경 감지
 * 2. 감지되면 사용자에게 경고 메시지 출력
 * 3. 사용자 승인 대기 (자동화 환경에서는 환경 변수로 우회 가능)
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// 색상 출력
const colors = {
	reset: '\x1b[0m',
	green: '\x1b[32m',
	yellow: '\x1b[33m',
	red: '\x1b[31m',
	blue: '\x1b[34m',
	bold: '\x1b[1m',
};

function log(message, color = 'reset') {
	console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Git diff를 분석하여 위험한 파일 변경 감지
 */
function detectRiskyChanges() {
	const riskyPatterns = [
		// 데이터베이스 마이그레이션
		{ pattern: /migrations\/|alembic\/versions\/|db\/migrate\//, type: 'Database Migration' },
		// 인프라 변경
		{ pattern: /\.tf$|terraform\.tfvars/, type: 'Infrastructure Change' },
		// 환경 변수
		{ pattern: /\.env$|\.env\.example/, type: 'Environment Variable' },
		// 의존성 파일
		{ pattern: /package\.json|requirements\.txt|go\.mod|Cargo\.toml|pyproject\.toml/, type: 'Dependency Change' },
		// 인증/권한
		{ pattern: /auth\/|middleware\/|permissions\//, type: 'Authentication/Authorization' },
	];

	try {
		// Git이 초기화되지 않은 경우 스킵
		if (!fs.existsSync('.git')) {
			return [];
		}

		// 변경된 파일 목록 가져오기
		const changedFiles = execSync('git diff --name-only --cached 2>/dev/null || git diff --name-only 2>/dev/null', {
			encoding: 'utf-8',
		}).trim();

		if (!changedFiles) {
			return [];
		}

		const files = changedFiles.split('\n').filter(Boolean);
		const detected = [];

		for (const file of files) {
			for (const { pattern, type } of riskyPatterns) {
				if (pattern.test(file)) {
					detected.push({ file, type });
					break; // 한 파일이 여러 패턴에 매치되어도 한 번만 추가
				}
			}
		}

		return detected;
	} catch (error) {
		// Git 명령어 실패 시 (예: 새 저장소) 빈 배열 반환
		return [];
	}
}

/**
 * 사용자 승인 요청
 */
function requestApproval(riskyChanges) {
	return new Promise((resolve) => {
		const rl = readline.createInterface({
			input: process.stdin,
			output: process.stdout,
		});

		log('\n⚠️  [STOP HOOK] Risky changes detected:', 'yellow');
		log('', 'reset');

		for (const { file, type } of riskyChanges) {
			log(`   ${colors.red}${type}${colors.reset}: ${file}`, 'reset');
		}

		log('', 'reset');
		log('This requires human review before proceeding.', 'yellow');
		log('', 'reset');

		// 환경 변수로 자동 승인 가능 (CI 환경용)
		if (process.env.AUTO_APPROVE === 'true') {
			log('⚠️  AUTO_APPROVE is set. Proceeding automatically.', 'yellow');
			rl.close();
			resolve(true);
			return;
		}

		rl.question(`${colors.bold}Do you approve these changes? (yes/no): ${colors.reset}`, (answer) => {
			rl.close();
			const approved = answer.toLowerCase() === 'yes' || answer.toLowerCase() === 'y';
			if (approved) {
				log('✅ Changes approved. Proceeding...', 'green');
			} else {
				log('❌ Changes rejected by user. Stopping.', 'red');
			}
			resolve(approved);
		});
	});
}

/**
 * 메인 실행 함수
 */
async function main() {
	const riskyChanges = detectRiskyChanges();

	if (riskyChanges.length === 0) {
		// 위험한 변경사항이 없으면 정상 진행
		return;
	}

	log('🛑 [STOP HOOK] Triggered', 'red');
	log('', 'reset');

	const approved = await requestApproval(riskyChanges);

	if (!approved) {
		process.exit(1);
	}
}

// 스크립트가 직접 실행된 경우에만 실행
if (require.main === module) {
	main().catch((error) => {
		log(`❌ Error: ${error.message}`, 'red');
		process.exit(1);
	});
}

module.exports = { detectRiskyChanges, requestApproval };

