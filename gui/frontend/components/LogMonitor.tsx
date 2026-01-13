/**
 * LogMonitor 컴포넌트
 * 실시간 로컬 로그 모니터링 및 진단 결과 시각화
 */

import { useState, useEffect } from "react";
import { analyzeLogs, readLogs, type LogAnalysisResult } from "@/lib/api";

interface LogMonitorProps {
	targetPath?: string;
	logFile?: string;
}

export default function LogMonitor({ targetPath, logFile }: LogMonitorProps) {
	const [logs, setLogs] = useState<string[]>([]);
	const [analysis, setAnalysis] = useState<LogAnalysisResult | null>(null);
	const [loading, setLoading] = useState(false);
	const [autoRefresh, setAutoRefresh] = useState(false);

	useEffect(() => {
		const fetchLogs = async () => {
			try {
				const result = await readLogs(targetPath, logFile, 50);
				if (result.status === "success") {
					setLogs(result.lines);
				}
			} catch (error) {
				console.error("Failed to fetch logs:", error);
			}
		};

		fetchLogs();
		
		if (autoRefresh) {
			const interval = setInterval(fetchLogs, 5000); // 5초마다 갱신
			return () => clearInterval(interval);
		}
	}, [targetPath, logFile, autoRefresh]);

	const handleAnalyze = async () => {
		setLoading(true);
		try {
			const result = await analyzeLogs(targetPath, logFile);
			setAnalysis(result);
		} catch (error) {
			console.error("Failed to analyze logs:", error);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-bold text-gray-800">로컬 로그 모니터</h2>
				<div className="flex gap-4">
					<label className="flex items-center gap-2">
						<input
							type="checkbox"
							checked={autoRefresh}
							onChange={(e) => setAutoRefresh(e.target.checked)}
							className="rounded"
						/>
						<span className="text-sm text-gray-600">자동 갱신</span>
					</label>
					<button
						type="button"
						onClick={handleAnalyze}
						disabled={loading}
						className={`px-6 py-2 rounded-lg font-semibold ${
							loading
								? "bg-gray-400 text-gray-600 cursor-not-allowed"
								: "bg-blue-600 text-white hover:bg-blue-700"
						}`}
					>
						{loading ? "분석 중..." : "로그 분석"}
					</button>
				</div>
			</div>

			{/* 로그 뷰어 */}
			<div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
				{logs.length === 0 ? (
					<div className="text-gray-500">로그 파일이 없거나 비어있습니다.</div>
				) : (
					logs.map((line, index) => {
						// 로그 레벨에 따른 색상
						let colorClass = "text-green-400";
						if (line.includes("[ERROR]") || line.includes("[CRITICAL]")) {
							colorClass = "text-red-400";
						} else if (line.includes("[WARNING]")) {
							colorClass = "text-yellow-400";
						} else if (line.includes("[INFO]")) {
							colorClass = "text-blue-400";
						}
						
						return (
							<div key={index} className={colorClass}>
								{line}
							</div>
						);
					})
				)}
			</div>

			{/* 분석 결과 */}
			{analysis && (
				<div className="bg-white border-2 rounded-lg p-6">
					<h3 className="text-xl font-semibold text-gray-800 mb-4">로그 분석 결과</h3>
					
					<div className="grid grid-cols-3 gap-4 mb-6">
						<div className={`p-4 rounded-lg ${
							analysis.summary.error_count > 0 ? "bg-red-50 border-2 border-red-500" : "bg-green-50 border-2 border-green-500"
						}`}>
							<div className="text-2xl font-bold text-gray-800">
								{analysis.summary.error_count}
							</div>
							<div className="text-sm text-gray-600">Errors</div>
						</div>
						
						<div className={`p-4 rounded-lg ${
							analysis.summary.critical_count > 0 ? "bg-red-50 border-2 border-red-500" : "bg-green-50 border-2 border-green-500"
						}`}>
							<div className="text-2xl font-bold text-gray-800">
								{analysis.summary.critical_count}
							</div>
							<div className="text-sm text-gray-600">Criticals</div>
						</div>
						
						<div className={`p-4 rounded-lg ${
							analysis.summary.warning_count > 0 ? "bg-yellow-50 border-2 border-yellow-500" : "bg-green-50 border-2 border-green-500"
						}`}>
							<div className="text-2xl font-bold text-gray-800">
								{analysis.summary.warning_count}
							</div>
							<div className="text-sm text-gray-600">Warnings</div>
						</div>
					</div>

					{analysis.summary.has_severe_errors && (
						<div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
							<p className="text-red-800 font-semibold">
								⚠️ 심각한 에러가 발견되었습니다. 승인이 차단됩니다.
							</p>
						</div>
					)}

					{/* 에러 목록 */}
					{(analysis.errors.length > 0 || analysis.criticals.length > 0) && (
						<div className="space-y-4">
							<h4 className="font-semibold text-gray-800">에러 상세</h4>
							
							{analysis.criticals.map((critical, index) => (
								<div key={`critical-${index}`} className="bg-red-50 border-l-4 border-red-500 p-3">
									<div className="font-semibold text-red-800">[CRITICAL]</div>
									<div className="text-sm text-gray-700">
										{critical.module && critical.funcName && critical.lineno && (
											<span className="font-mono">
												{critical.module}:{critical.funcName}:{critical.lineno}
											</span>
										)}
									</div>
									<div className="text-sm text-gray-600 mt-1">{critical.message}</div>
									<div className="text-xs text-gray-500 mt-1">{critical.timestamp}</div>
								</div>
							))}
							
							{analysis.errors.map((error, index) => (
								<div key={`error-${index}`} className="bg-orange-50 border-l-4 border-orange-500 p-3">
									<div className="font-semibold text-orange-800">[ERROR]</div>
									<div className="text-sm text-gray-700">
										{error.module && error.funcName && error.lineno && (
											<span className="font-mono">
												{error.module}:{error.funcName}:{error.lineno}
											</span>
										)}
									</div>
									<div className="text-sm text-gray-600 mt-1">{error.message}</div>
									<div className="text-xs text-gray-500 mt-1">{error.timestamp}</div>
								</div>
							))}
						</div>
					)}

					{/* 코드 분석 가이드 */}
					{analysis.code_analysis_guides && analysis.code_analysis_guides.length > 0 && (
						<div className="mt-6">
							<h4 className="font-semibold text-gray-800 mb-3">코드 분석 가이드</h4>
							<div className="space-y-3">
								{analysis.code_analysis_guides.map((guide, index) => (
									<div key={index} className="bg-blue-50 border-l-4 border-blue-500 p-3">
										<div className="text-sm font-semibold text-blue-800 mb-2">
											{guide.log_entry.module}:{guide.log_entry.funcName}:{guide.log_entry.lineno}
										</div>
										<div className="space-y-1">
											{guide.analysis_guides.map((g, gIndex) => (
												<div key={gIndex} className="text-xs text-gray-700">
													<strong>{g.tool}</strong>: {g.description}
												</div>
											))}
										</div>
									</div>
								))}
							</div>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

