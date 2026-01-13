/**
 * ConfigEditor 컴포넌트
 * CLAUDE.md 편집, 환경 변수 관리, uv 마이그레이션 UI
 */

import { useState, useEffect } from "react";
import {
	getClaudeSections,
	updateClaudeSection,
	checkEnv,
	updateEnv,
	checkTools,
	type ClaudeSections,
	type ToolStatus,
} from "@/lib/api";

export default function ConfigEditor() {
	const [activeTab, setActiveTab] = useState<"claude" | "env" | "migration">("claude");
	const [claudeSections, setClaudeSections] = useState<ClaudeSections | null>(null);
	const [editingSection, setEditingSection] = useState<"lessons_learned" | "team_standards" | null>(null);
	const [editContent, setEditContent] = useState("");
	const [saving, setSaving] = useState(false);
	const [targetPath, setTargetPath] = useState("");
	const [envVars, setEnvVars] = useState<Record<string, string>>({});
	const [envCheckResult, setEnvCheckResult] = useState<string>("");
	const [toolStatus, setToolStatus] = useState<ToolStatus | null>(null);
	const [migrationLogs, setMigrationLogs] = useState<string[]>([]);
	const [migrating, setMigrating] = useState(false);

	useEffect(() => {
		loadClaudeSections();
		loadToolStatus();
	}, []);

	const loadClaudeSections = async () => {
		try {
			const sections = await getClaudeSections();
			setClaudeSections(sections);
		} catch (error) {
			console.error("Failed to load CLAUDE sections:", error);
		}
	};

	const loadToolStatus = async () => {
		try {
			const status = await checkTools();
			setToolStatus(status);
		} catch (error) {
			console.error("Failed to check tools:", error);
		}
	};

	const handleEditSection = (section: "lessons_learned" | "team_standards") => {
		setEditingSection(section);
		setEditContent(claudeSections?.[section] || "");
	};

	const handleSaveSection = async () => {
		if (!editingSection) return;

		setSaving(true);
		try {
			await updateClaudeSection(editingSection, editContent, "replace");
			await loadClaudeSections();
			setEditingSection(null);
			setEditContent("");
		} catch (error) {
			console.error("Failed to save section:", error);
			alert("저장 실패: " + (error as Error).message);
		} finally {
			setSaving(false);
		}
	};

	const handleCheckEnv = async () => {
		if (!targetPath) {
			alert("대상 프로젝트 경로를 입력하세요.");
			return;
		}

		try {
			const result = await checkEnv(targetPath);
			setEnvCheckResult(result.output || result.error || "환경 변수 확인 완료");
		} catch (error) {
			console.error("Failed to check env:", error);
			setEnvCheckResult("환경 변수 확인 실패: " + (error as Error).message);
		}
	};

	const handleUpdateEnv = async () => {
		if (!targetPath) {
			alert("대상 프로젝트 경로를 입력하세요.");
			return;
		}

		try {
			await updateEnv(targetPath, envVars);
			alert("환경 변수가 업데이트되었습니다.");
			setEnvVars({});
		} catch (error) {
			console.error("Failed to update env:", error);
			alert("업데이트 실패: " + (error as Error).message);
		}
	};

	const handleMigrateToUv = async () => {
		if (!targetPath) {
			alert("대상 프로젝트 경로를 입력하세요.");
			return;
		}

		setMigrating(true);
		setMigrationLogs([]);

		try {
			const response = await fetch(
				`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/config/migrate/uv`,
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ target_path: targetPath }),
				}
			);

			if (!response.body) {
				throw new Error("No response body");
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value);
				const lines = chunk.split("\n");

				for (const line of lines) {
					if (line.startsWith("data: ")) {
						try {
							const data = JSON.parse(line.slice(6));
							if (data.type === "log") {
								setMigrationLogs((prev) => [...prev, data.message]);
							} else if (data.type === "success") {
								setMigrationLogs((prev) => [...prev, "✅ 마이그레이션 완료"]);
								setMigrating(false);
							} else if (data.type === "error") {
								setMigrationLogs((prev) => [...prev, `❌ 에러: ${data.message}`]);
								setMigrating(false);
							}
						} catch (e) {
							// JSON 파싱 실패 무시
						}
					}
				}
			}
		} catch (error) {
			console.error("Migration failed:", error);
			setMigrationLogs((prev) => [...prev, `❌ 마이그레이션 실패: ${error}`]);
			setMigrating(false);
		}
	};

	return (
		<div className="space-y-6 dark:text-gray-100">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
					설정 및 지식 편집기
				</h2>
			</div>

			{/* 탭 네비게이션 */}
			<div className="flex border-b dark:border-gray-700">
				<button
					type="button"
					onClick={() => setActiveTab("claude")}
					className={`px-6 py-3 font-semibold ${
						activeTab === "claude"
							? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
							: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
					}`}
				>
					CLAUDE.md 편집
				</button>
				<button
					type="button"
					onClick={() => setActiveTab("env")}
					className={`px-6 py-3 font-semibold ${
						activeTab === "env"
							? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
							: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
					}`}
				>
					환경 변수
				</button>
				<button
					type="button"
					onClick={() => setActiveTab("migration")}
					className={`px-6 py-3 font-semibold ${
						activeTab === "migration"
							? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
							: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
					}`}
				>
					uv 마이그레이션
				</button>
			</div>

			{/* CLAUDE.md 편집 탭 */}
			{activeTab === "claude" && (
				<div className="space-y-4">
					<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
						<h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
							Lessons Learned
						</h3>
						{editingSection === "lessons_learned" ? (
							<div className="space-y-4">
								<textarea
									value={editContent}
									onChange={(e) => setEditContent(e.target.value)}
									className="w-full h-64 p-4 border rounded-lg font-mono text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
									placeholder="Lessons Learned 내용을 입력하세요..."
								/>
								<div className="flex gap-4">
									<button
										type="button"
										onClick={handleSaveSection}
										disabled={saving}
										className="px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
									>
										{saving ? "저장 중..." : "저장"}
									</button>
									<button
										type="button"
										onClick={() => {
											setEditingSection(null);
											setEditContent("");
										}}
										className="px-6 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
									>
										취소
									</button>
								</div>
							</div>
						) : (
							<div>
								<pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm whitespace-pre-wrap overflow-auto max-h-64">
									{claudeSections?.lessons_learned || "내용 없음"}
								</pre>
								<button
									type="button"
									onClick={() => handleEditSection("lessons_learned")}
									className="mt-4 px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
								>
									편집
								</button>
							</div>
						)}
					</div>

					<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
						<h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
							Team Standards
						</h3>
						{editingSection === "team_standards" ? (
							<div className="space-y-4">
								<textarea
									value={editContent}
									onChange={(e) => setEditContent(e.target.value)}
									className="w-full h-64 p-4 border rounded-lg font-mono text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
									placeholder="Team Standards 내용을 입력하세요..."
								/>
								<div className="flex gap-4">
									<button
										type="button"
										onClick={handleSaveSection}
										disabled={saving}
										className="px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
									>
										{saving ? "저장 중..." : "저장"}
									</button>
									<button
										type="button"
										onClick={() => {
											setEditingSection(null);
											setEditContent("");
										}}
										className="px-6 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
									>
										취소
									</button>
								</div>
							</div>
						) : (
							<div>
								<pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm whitespace-pre-wrap overflow-auto max-h-64">
									{claudeSections?.team_standards || "내용 없음"}
								</pre>
								<button
									type="button"
									onClick={() => handleEditSection("team_standards")}
									className="mt-4 px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
								>
									편집
								</button>
							</div>
						)}
					</div>
				</div>
			)}

			{/* 환경 변수 탭 */}
			{activeTab === "env" && (
				<div className="space-y-4">
					<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
						<h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
							환경 변수 관리
						</h3>
						<div className="space-y-4">
							<input
								type="text"
								placeholder="대상 프로젝트 경로"
								value={targetPath}
								onChange={(e) => setTargetPath(e.target.value)}
								className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
							/>
							<div className="flex gap-4">
								<button
									type="button"
									onClick={handleCheckEnv}
									className="px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
								>
									환경 변수 확인
								</button>
								<button
									type="button"
									onClick={handleUpdateEnv}
									className="px-6 py-2 bg-green-600 dark:bg-green-500 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600"
								>
									환경 변수 업데이트
								</button>
							</div>
							{envCheckResult && (
								<pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm whitespace-pre-wrap overflow-auto max-h-64">
									{envCheckResult}
								</pre>
							)}
						</div>
					</div>
				</div>
			)}

			{/* uv 마이그레이션 탭 */}
			{activeTab === "migration" && (
				<div className="space-y-4">
					<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
						<h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
							Poetry → uv 마이그레이션
						</h3>
						<div className="space-y-4">
							<input
								type="text"
								placeholder="대상 프로젝트 경로"
								value={targetPath}
								onChange={(e) => setTargetPath(e.target.value)}
								className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
							/>
							<button
								type="button"
								onClick={handleMigrateToUv}
								disabled={migrating}
								className={`px-6 py-2 rounded-lg font-semibold ${
									migrating
										? "bg-gray-400 dark:bg-gray-600 text-gray-600 dark:text-gray-400 cursor-not-allowed"
										: "bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600"
								}`}
							>
								{migrating ? "마이그레이션 중..." : "마이그레이션 시작"}
							</button>
							{migrationLogs.length > 0 && (
								<div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-auto">
									{migrationLogs.map((log, index) => (
										<div key={index}>{log}</div>
									))}
								</div>
							)}
						</div>
					</div>

					{/* 도구 상태 */}
					{toolStatus && (
						<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
							<h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
								도구 설치 상태
							</h3>
							<div className="grid grid-cols-3 gap-4">
								<div className={`p-4 rounded-lg ${
									toolStatus.mise.installed
										? "bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-400"
										: "bg-red-50 dark:bg-red-900/20 border-2 border-red-500 dark:border-red-400"
								}`}>
									<div className="font-semibold text-gray-800 dark:text-gray-100">mise</div>
									<div className="text-sm text-gray-600 dark:text-gray-400">
										{toolStatus.mise.installed ? `✓ ${toolStatus.mise.version}` : "✗ 미설치"}
									</div>
								</div>
								<div className={`p-4 rounded-lg ${
									toolStatus.uv.installed
										? "bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-400"
										: "bg-red-50 dark:bg-red-900/20 border-2 border-red-500 dark:border-red-400"
								}`}>
									<div className="font-semibold text-gray-800 dark:text-gray-100">uv</div>
									<div className="text-sm text-gray-600 dark:text-gray-400">
										{toolStatus.uv.installed ? `✓ ${toolStatus.uv.version}` : "✗ 미설치"}
									</div>
								</div>
								<div className={`p-4 rounded-lg ${
									toolStatus.mcp.installed
										? "bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-400"
										: "bg-red-50 dark:bg-red-900/20 border-2 border-red-500 dark:border-red-400"
								}`}>
									<div className="font-semibold text-gray-800 dark:text-gray-100">MCP</div>
									<div className="text-sm text-gray-600 dark:text-gray-400">
										{toolStatus.mcp.installed ? "✓ 설정됨" : "✗ 미설정"}
									</div>
								</div>
							</div>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

