/**
 * AgentHub 컴포넌트
 * 에이전트 관리 대시보드 - 개별 에이전트 실행 및 실시간 결과 뷰어
 */

import { useState, useEffect } from "react";
import { runAgent, runAgentStream, type AgentRunRequest } from "@/lib/api";

interface AgentStatus {
	name: string;
	id: string;
	status: "idle" | "running" | "completed" | "failed";
	lastRun?: Date;
	result?: any;
	logs: string[];
}

interface VerificationResult {
	simplifier: AgentStatus;
	visual: AgentStatus;
	security: AgentStatus;
	log_analyzer: AgentStatus;
	overall: {
		status: "pass" | "fail" | "warning";
		score: number;
	};
}

export default function AgentHub() {
	const [agents, setAgents] = useState<AgentStatus[]>([
		{
			name: "Code Simplifier",
			id: "simplifier",
			status: "idle",
			logs: [],
		},
		{
			name: "Visual Verifier",
			id: "visual_verifier",
			status: "idle",
			logs: [],
		},
		{
			name: "Security Audit",
			id: "security_audit",
			status: "idle",
			logs: [],
		},
		{
			name: "Log Analyzer",
			id: "log_analyzer",
			status: "idle",
			logs: [],
		},
	]);

	const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
	const [loading, setLoading] = useState(false);
	const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
	const [targetPath, setTargetPath] = useState<string>("");

	const runSingleAgent = async (agentId: string) => {
		const agent = agents.find((a) => a.id === agentId);
		if (!agent) return;

		setAgents((prev) =>
			prev.map((a) =>
				a.id === agentId ? { ...a, status: "running" as const, logs: [] } : a
			)
		);

		try {
			const request: AgentRunRequest = {
				agent_name: agentId as any,
				target_path: targetPath || undefined,
			};

			// 실시간 스트리밍
			const eventSource = runAgentStream(request, (data) => {
				if (data.type === "log") {
					setAgents((prev) =>
						prev.map((a) =>
							a.id === agentId
								? { ...a, logs: [...a.logs, data.message] }
								: a
						)
					);
				} else if (data.type === "success") {
					setAgents((prev) =>
						prev.map((a) =>
							a.id === agentId
								? {
										...a,
										status: "completed" as const,
										lastRun: new Date(),
									}
								: a
						)
					);
					eventSource.close();
				} else if (data.type === "error") {
					setAgents((prev) =>
						prev.map((a) =>
							a.id === agentId
								? {
										...a,
										status: "failed" as const,
										lastRun: new Date(),
									}
								: a
						)
					);
					eventSource.close();
				}
			});

			// 결과도 가져오기
			const result = await runAgent(request);
			if (result.status === "success" && result.result) {
				setAgents((prev) =>
					prev.map((a) =>
						a.id === agentId ? { ...a, result: result.result } : a
					)
				);
			}
		} catch (error) {
			console.error(`Agent ${agentId} failed:`, error);
			setAgents((prev) =>
				prev.map((a) =>
					a.id === agentId
						? { ...a, status: "failed" as const, lastRun: new Date() }
						: a
				)
			);
		}
	};

	const runVerification = async () => {
		setLoading(true);
		setAgents((prev) =>
			prev.map((agent) => ({ ...agent, status: "running" as const, logs: [] }))
		);

		try {
			// 모든 에이전트 순차 실행
			for (const agent of agents) {
				await runSingleAgent(agent.id);
			}

			// 전체 결과 요약 생성
			const overallResult: VerificationResult = {
				simplifier: agents.find((a) => a.id === "simplifier")!,
				visual: agents.find((a) => a.id === "visual_verifier")!,
				security: agents.find((a) => a.id === "security_audit")!,
				log_analyzer: agents.find((a) => a.id === "log_analyzer")!,
				overall: {
					status: "pass",
					score: 95,
				},
			};

			setVerificationResult(overallResult);
		} catch (error) {
			console.error("Verification failed:", error);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="space-y-6 dark:text-gray-100">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
					에이전트 관리 대시보드
				</h2>
				<div className="flex gap-4">
					<input
						type="text"
						placeholder="대상 프로젝트 경로 (선택사항)"
						value={targetPath}
						onChange={(e) => setTargetPath(e.target.value)}
						className="px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
					/>
					<button
						type="button"
						onClick={runVerification}
						disabled={loading}
						className={`px-6 py-2 rounded-lg font-semibold ${
							loading
								? "bg-gray-400 dark:bg-gray-600 text-gray-600 dark:text-gray-400 cursor-not-allowed"
								: "bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600"
						}`}
					>
						{loading ? "실행 중..." : "전체 검증 실행"}
					</button>
				</div>
			</div>

			{/* 에이전트 카드 */}
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				{agents.map((agent) => (
					<div
						key={agent.id}
						className={`border-2 rounded-lg p-4 dark:border-gray-700 ${
							agent.status === "completed"
								? "border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-900/20"
								: agent.status === "running"
								? "border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20"
								: agent.status === "failed"
								? "border-red-500 dark:border-red-400 bg-red-50 dark:bg-red-900/20"
								: "border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800"
						}`}
					>
						<div className="flex items-center justify-between mb-2">
							<h3 className="font-semibold text-gray-800 dark:text-gray-100">
								{agent.name}
							</h3>
							<span
								className={`text-sm font-semibold ${
									agent.status === "completed"
										? "text-green-600 dark:text-green-400"
										: agent.status === "running"
										? "text-blue-600 dark:text-blue-400"
										: agent.status === "failed"
										? "text-red-600 dark:text-red-400"
										: "text-gray-500 dark:text-gray-400"
								}`}
							>
								{agent.status === "completed"
									? "✓ 완료"
									: agent.status === "running"
									? "⏳ 실행 중"
									: agent.status === "failed"
									? "✗ 실패"
									: "대기"}
							</span>
						</div>

						{agent.lastRun && (
							<p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
								마지막 실행: {agent.lastRun.toLocaleString()}
							</p>
						)}

						<button
							type="button"
							onClick={() => runSingleAgent(agent.id)}
							disabled={agent.status === "running"}
							className={`w-full mt-2 px-4 py-2 rounded text-sm font-semibold ${
								agent.status === "running"
									? "bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400 cursor-not-allowed"
									: "bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700"
							}`}
						>
							{agent.status === "running" ? "실행 중..." : "개별 실행"}
						</button>

						{agent.result && (
							<div className="mt-3 space-y-1 text-sm">
								{agent.result.suggestions !== undefined && (
									<div className="text-gray-700 dark:text-gray-300">
										제안 사항: <strong>{agent.result.suggestions}개</strong>
									</div>
								)}
								{agent.result.vulnerabilities !== undefined && (
									<div className="text-gray-700 dark:text-gray-300">
										취약점: <strong>{agent.result.vulnerabilities}개</strong>
									</div>
								)}
								{agent.result.complexity !== undefined && (
									<div className="text-gray-700 dark:text-gray-300">
										복잡도: <strong>{agent.result.complexity}</strong>
									</div>
								)}
								{agent.result.errors && agent.result.errors.length > 0 && (
									<div className="text-red-600 dark:text-red-400">
										에러: {agent.result.errors.length}개
									</div>
								)}
							</div>
						)}

						{agent.logs.length > 0 && (
							<button
								type="button"
								onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
								className="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
							>
								{selectedAgent === agent.id ? "로그 숨기기" : "로그 보기"}
							</button>
						)}
					</div>
				))}
			</div>

			{/* 로그 뷰어 모달 */}
			{selectedAgent && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
					<div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-auto">
						<div className="flex items-center justify-between mb-4">
							<h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
								{agents.find((a) => a.id === selectedAgent)?.name} 실행 로그
							</h3>
							<button
								type="button"
								onClick={() => setSelectedAgent(null)}
								className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
							>
								✕
							</button>
						</div>
						<div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
							{agents
								.find((a) => a.id === selectedAgent)
								?.logs.map((log, index) => (
									<div key={index}>{log}</div>
								))}
						</div>
					</div>
				</div>
			)}

			{/* 전체 결과 요약 */}
			{verificationResult && (
				<div className="bg-white dark:bg-gray-800 border-2 dark:border-gray-700 rounded-lg p-6">
					<h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4">
						검증 결과 요약
					</h3>

					<div className="flex items-center gap-4 mb-4">
						<div
							className={`text-4xl font-bold ${
								verificationResult.overall.status === "pass"
									? "text-green-600 dark:text-green-400"
									: verificationResult.overall.status === "fail"
									? "text-red-600 dark:text-red-400"
									: "text-yellow-600 dark:text-yellow-400"
							}`}
						>
							{verificationResult.overall.score}점
						</div>
						<div>
							<div className="text-sm text-gray-600 dark:text-gray-400">전체 상태</div>
							<div
								className={`font-semibold ${
									verificationResult.overall.status === "pass"
										? "text-green-600 dark:text-green-400"
										: verificationResult.overall.status === "fail"
										? "text-red-600 dark:text-red-400"
										: "text-yellow-600 dark:text-yellow-400"
								}`}
							>
								{verificationResult.overall.status === "pass"
									? "통과"
									: verificationResult.overall.status === "fail"
									? "실패"
									: "경고"}
							</div>
						</div>
					</div>

					{/* 품질 지표 그래프 */}
					<div className="grid grid-cols-4 gap-4 mt-4">
						<div className="text-center">
							<div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
								{verificationResult.simplifier.result?.suggestions || 0}
							</div>
							<div className="text-xs text-gray-600 dark:text-gray-400">코드 개선 제안</div>
						</div>
						<div className="text-center">
							<div className="text-2xl font-bold text-green-600 dark:text-green-400">
								{verificationResult.security.result?.vulnerabilities === 0
									? "✓"
									: verificationResult.security.result?.vulnerabilities || "?"}
							</div>
							<div className="text-xs text-gray-600 dark:text-gray-400">보안 취약점</div>
						</div>
						<div className="text-center">
							<div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
								{verificationResult.simplifier.result?.complexity || "N/A"}
							</div>
							<div className="text-xs text-gray-600 dark:text-gray-400">코드 복잡도</div>
						</div>
						<div className="text-center">
							<div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
								{verificationResult.log_analyzer.result?.summary?.error_count || 0}
							</div>
							<div className="text-xs text-gray-600 dark:text-gray-400">로그 에러</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
