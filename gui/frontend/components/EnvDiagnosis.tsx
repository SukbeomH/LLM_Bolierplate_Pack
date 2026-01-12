/**
 * EnvDiagnosis 컴포넌트
 * 환경 진단 UI
 */

import type { PostDiagnosis } from "@/lib/types";

interface EnvDiagnosisProps {
	diagnosis: PostDiagnosis | null;
}

export default function EnvDiagnosis({ diagnosis }: EnvDiagnosisProps) {
	if (!diagnosis) {
		return null;
	}

	return (
		<div style={{ marginBottom: "2rem" }}>
			<h2 style={{ marginBottom: "1rem", fontSize: "1.5rem", fontWeight: "bold" }}>사후 진단</h2>

			{/* 환경 변수 체크 */}
			{diagnosis.env_check && (
				<div
					style={{
						padding: "1rem",
						backgroundColor: "#f5f5f5",
						borderRadius: "4px",
						marginBottom: "1rem",
						border: "1px solid #ddd",
					}}
				>
					<h3 style={{ marginBottom: "0.5rem", fontSize: "1.1rem", fontWeight: "bold" }}>환경 변수 체크</h3>
					{diagnosis.env_check.error ? (
						<div style={{ color: "#c33" }}>❌ {diagnosis.env_check.error}</div>
					) : (
						<div>
							<div style={{ marginBottom: "0.5rem" }}>
								{diagnosis.env_check.has_env_sample ? (
									<span style={{ color: "#4caf50" }}>✅ .env_sample 파일 존재</span>
								) : (
									<span style={{ color: "#ff9800" }}>⚠️ .env_sample 파일 없음</span>
								)}
							</div>
							{diagnosis.env_check.has_missing_keys && (
								<div style={{ color: "#ff9800", marginTop: "0.5rem" }}>
									⚠️ 누락된 환경 변수가 있습니다. check_env.sh를 실행하여 확인하세요.
								</div>
							)}
						</div>
					)}
				</div>
			)}

			{/* Git 상태 */}
			{diagnosis.git_status && (
				<div
					style={{
						padding: "1rem",
						backgroundColor: "#f5f5f5",
						borderRadius: "4px",
						border: "1px solid #ddd",
					}}
				>
					<h3 style={{ marginBottom: "0.5rem", fontSize: "1.1rem", fontWeight: "bold" }}>Git 상태</h3>
					{diagnosis.git_status.error ? (
						<div style={{ color: "#c33" }}>❌ {diagnosis.git_status.error}</div>
					) : diagnosis.git_status.is_git_repo ? (
						<div>
							<div style={{ marginBottom: "0.5rem" }}>
								<span style={{ color: "#4caf50" }}>✅ Git 저장소</span>
								{diagnosis.git_status.current_branch && (
									<span style={{ marginLeft: "1rem", color: "#666" }}>
										브랜치: {diagnosis.git_status.current_branch}
									</span>
								)}
							</div>
							{diagnosis.git_status.has_changes && diagnosis.git_status.changed_files && (
								<div style={{ marginTop: "0.5rem" }}>
									<div style={{ color: "#ff9800", marginBottom: "0.25rem" }}>
										⚠️ 변경된 파일: {diagnosis.git_status.changed_files.length}개
									</div>
									<div
										style={{
											fontSize: "0.9rem",
											color: "#666",
											maxHeight: "100px",
											overflowY: "auto",
										}}
									>
										{diagnosis.git_status.changed_files.slice(0, 10).map((file, index) => (
											<div key={index}>{file}</div>
										))}
										{diagnosis.git_status.changed_files.length > 10 && (
											<div>... 외 {diagnosis.git_status.changed_files.length - 10}개</div>
										)}
									</div>
								</div>
							)}
						</div>
					) : (
						<div>
							<div style={{ color: "#ff9800", marginBottom: "0.5rem" }}>
								⚠️ {diagnosis.git_status.message || "Git 저장소가 아닙니다."}
							</div>
							<div style={{ fontSize: "0.9rem", color: "#666" }}>
								권장: <code style={{ backgroundColor: "#eee", padding: "0.2rem 0.4rem", borderRadius: "3px" }}>git init</code>을
								실행하세요.
							</div>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

