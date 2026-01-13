/**
 * AgentHub 컴포넌트
 * 에이전트 관리 대시보드 - Simplifier, Visual Verifier, Security Audit 상태 및 결과 표시
 */

import { useState, useEffect } from "react";

interface AgentStatus {
	name: string;
	status: "idle" | "running" | "completed" | "failed";
	lastRun?: Date;
	result?: {
		suggestions?: number;
		vulnerabilities?: number;
		complexity?: number;
		errors?: string[];
	};
}

interface VerificationResult {
	simplifier: AgentStatus;
	visual: AgentStatus;
	security: AgentStatus;
	overall: {
		status: "pass" | "fail" | "warning";
		score: number;
	};
}

export default function AgentHub() {
	const [agents, setAgents] = useState<AgentStatus[]>([
		{
			name: "Code Simplifier",
			status: "idle",
		},
		{
			name: "Visual Verifier",
			status: "idle",
		},
		{
			name: "Security Audit",
			status: "idle",
		},
	]);

	const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
	const [loading, setLoading] = useState(false);

	const runVerification = async () => {
		setLoading(true);
		setAgents((prev) =>
			prev.map((agent) => ({ ...agent, status: "running" as const }))
		);

		try {
			// 실제로는 verify-feedback-loop.js를 실행하고 결과를 받아와야 함
			// 여기서는 시뮬레이션
			await new Promise((resolve) => setTimeout(resolve, 2000));

			// 시뮬레이션 결과
			const mockResult: VerificationResult = {
				simplifier: {
					name: "Code Simplifier",
					status: "completed",
					lastRun: new Date(),
					result: {
						suggestions: 3,
						complexity: 12,
					},
				},
				visual: {
					name: "Visual Verifier",
					status: "completed",
					lastRun: new Date(),
					result: {
						errors: [],
					},
				},
				security: {
					name: "Security Audit",
					status: "completed",
					lastRun: new Date(),
					result: {
						vulnerabilities: 0,
					},
				},
				overall: {
					status: "pass",
					score: 95,
				},
			};

			setVerificationResult(mockResult);
			setAgents([
				mockResult.simplifier,
				mockResult.visual,
				mockResult.security,
			]);
		} catch (error) {
			console.error("Verification failed:", error);
			setAgents((prev) =>
				prev.map((agent) => ({ ...agent, status: "failed" as const }))
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-bold text-gray-800">에이전트 관리 대시보드</h2>
				<button
					type="button"
					onClick={runVerification}
					disabled={loading}
					className={`px-6 py-2 rounded-lg font-semibold ${
						loading
							? "bg-gray-400 text-gray-600 cursor-not-allowed"
							: "bg-blue-600 text-white hover:bg-blue-700"
					}`}
				>
					{loading ? "실행 중..." : "검증 실행"}
				</button>
			</div>

			{/* 에이전트 카드 */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				{agents.map((agent) => (
					<div
						key={agent.name}
						className={`border-2 rounded-lg p-4 ${
							agent.status === "completed"
								? "border-green-500 bg-green-50"
								: agent.status === "running"
								? "border-blue-500 bg-blue-50"
								: agent.status === "failed"
								? "border-red-500 bg-red-50"
								: "border-gray-300 bg-gray-50"
						}`}
					>
						<div className="flex items-center justify-between mb-2">
							<h3 className="font-semibold text-gray-800">{agent.name}</h3>
							<span
								className={`text-sm font-semibold ${
									agent.status === "completed"
										? "text-green-600"
										: agent.status === "running"
										? "text-blue-600"
										: agent.status === "failed"
										? "text-red-600"
										: "text-gray-500"
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
							<p className="text-xs text-gray-600 mb-2">
								마지막 실행: {agent.lastRun.toLocaleString()}
							</p>
						)}

						{agent.result && (
							<div className="mt-3 space-y-1 text-sm">
								{agent.result.suggestions !== undefined && (
									<div className="text-gray-700">
										제안 사항: <strong>{agent.result.suggestions}개</strong>
									</div>
								)}
								{agent.result.vulnerabilities !== undefined && (
									<div className="text-gray-700">
										취약점: <strong>{agent.result.vulnerabilities}개</strong>
									</div>
								)}
								{agent.result.complexity !== undefined && (
									<div className="text-gray-700">
										복잡도: <strong>{agent.result.complexity}</strong>
									</div>
								)}
								{agent.result.errors && agent.result.errors.length > 0 && (
									<div className="text-red-600">
										에러: {agent.result.errors.length}개
									</div>
								)}
							</div>
						)}
					</div>
				))}
			</div>

			{/* 전체 결과 요약 */}
			{verificationResult && (
				<div className="bg-white border-2 rounded-lg p-6">
					<h3 className="text-xl font-semibold text-gray-800 mb-4">검증 결과 요약</h3>
					
					<div className="flex items-center gap-4 mb-4">
						<div
							className={`text-4xl font-bold ${
								verificationResult.overall.status === "pass"
									? "text-green-600"
									: verificationResult.overall.status === "fail"
									? "text-red-600"
									: "text-yellow-600"
							}`}
						>
							{verificationResult.overall.score}점
						</div>
						<div>
							<div className="text-sm text-gray-600">전체 상태</div>
							<div
								className={`font-semibold ${
									verificationResult.overall.status === "pass"
										? "text-green-600"
										: verificationResult.overall.status === "fail"
										? "text-red-600"
										: "text-yellow-600"
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

					{/* 품질 지표 그래프 (간단한 시각화) */}
					<div className="grid grid-cols-3 gap-4 mt-4">
						<div className="text-center">
							<div className="text-2xl font-bold text-blue-600">
								{verificationResult.simplifier.result?.suggestions || 0}
							</div>
							<div className="text-xs text-gray-600">코드 개선 제안</div>
						</div>
						<div className="text-center">
							<div className="text-2xl font-bold text-green-600">
								{verificationResult.security.result?.vulnerabilities === 0 ? "✓" : verificationResult.security.result?.vulnerabilities || "?"}
							</div>
							<div className="text-xs text-gray-600">보안 취약점</div>
						</div>
						<div className="text-center">
							<div className="text-2xl font-bold text-purple-600">
								{verificationResult.simplifier.result?.complexity || "N/A"}
							</div>
							<div className="text-xs text-gray-600">코드 복잡도</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

