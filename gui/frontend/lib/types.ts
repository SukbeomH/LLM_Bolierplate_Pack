/**
 * TypeScript 타입 정의
 */

export interface StackInfo {
	stack: string | null;
	package_manager: string | null;
	venv_path: string | null;
	python_version: string | null;
	detected_files: string[];
	error?: string | null;
}

export interface InjectionOptions {
	backup_existing: boolean;
	merge_claude_config: boolean;
	skip_existing: boolean;
}

export interface PostDiagnosis {
	env_check?: {
		has_env_sample?: boolean;
		has_missing_keys?: boolean;
		output?: string;
		return_code?: number;
		error?: string;
	} | null;
	git_status?: {
		is_git_repo: boolean;
		current_branch?: string | null;
		changed_files?: string[];
		has_changes?: boolean;
		message?: string;
		error?: string;
	} | null;
}

export interface InjectResponse {
	status: string;
	injected_files: string[];
	backed_up_files: string[];
	skipped_files: string[];
	merged_files: string[];
	post_diagnosis?: PostDiagnosis | null;
	error?: string | null;
}

export type AssetType = ".claude/" | "scripts/" | "CLAUDE.md" | "mise.toml" | "docs/ai-onboarding.md";

export const ASSETS: Array<{
	id: AssetType;
	label: string;
	description: string;
	required: boolean;
}> = [
	{
		id: ".claude/",
		label: ".claude/ (Claude 설정)",
		description: "Claude Code 설정 및 자동화 훅 (필수)",
		required: true,
	},
	{
		id: "scripts/",
		label: "scripts/ (자동화 스크립트)",
		description: "스택 감지 및 검증 스크립트 (필수)",
		required: true,
	},
	{
		id: "CLAUDE.md",
		label: "CLAUDE.md (AI 지식베이스)",
		description: "팀 지식 축적 및 AI 페르소나 정의 (필수)",
		required: true,
	},
	{
		id: "mise.toml",
		label: "mise.toml (툴체인 관리)",
		description: "통합 툴체인 관리 설정 (선택)",
		required: false,
	},
	{
		id: "docs/ai-onboarding.md",
		label: "docs/ai-onboarding.md (온보딩 가이드)",
		description: "AI 팀 온보딩 가이드 (선택)",
		required: false,
	},
];

