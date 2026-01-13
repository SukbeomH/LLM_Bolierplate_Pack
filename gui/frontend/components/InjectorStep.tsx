/**
 * InjectorStep 컴포넌트
 * 메인 인젝터 컴포넌트
 */

import { useState, useRef, useEffect } from "react";
import StackDetection from "./StackDetection";
import AssetSelection from "./AssetSelection";
import ProgressReport from "./ProgressReport";
import EnvDiagnosis from "./EnvDiagnosis";
import PromptCopyCard from "./PromptCopyCard";
import { injectBoilerplate, injectBoilerplateStream, type InjectStreamUpdate } from "@/lib/api";
import type { StackInfo, InjectResponse, InjectionOptions, PostDiagnosis } from "@/lib/types";

interface InjectorStepProps {
	onStackDetected?: (stackInfo: StackInfo | null) => void;
	onDiagnosisUpdate?: (diagnosis: PostDiagnosis | null) => void;
}

export default function InjectorStep({ onStackDetected, onDiagnosisUpdate }: InjectorStepProps) {
	const [targetPath, setTargetPath] = useState("");
	const [stackInfo, setStackInfo] = useState<StackInfo | null>(null);

	// StackDetection에서 경로를 받아오는 콜백
	const handlePathChange = (path: string) => {
		setTargetPath(path);
	};
	const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
	const [injectionOptions, setInjectionOptions] = useState<InjectionOptions>({
		backup_existing: true,
		merge_claude_config: false,
		skip_existing: false,
	});
	const [progress, setProgress] = useState(0);
	const [logs, setLogs] = useState<string[]>([]);
	const [injectResult, setInjectResult] = useState<InjectResponse | null>(null);
	const [loading, setLoading] = useState(false);
	const abortControllerRef = useRef<AbortController | null>(null);

	const handleDetected = (info: StackInfo) => {
		setStackInfo(info);
		onStackDetected?.(info);
		// targetPath는 사용자가 입력한 경로이므로 변경하지 않음
	};

	const handleApply = async () => {
		if (!targetPath.trim()) {
			alert("대상 경로를 입력하고 스택을 감지해주세요.");
			return;
		}

		if (selectedAssets.length === 0) {
			alert("주입할 자산을 선택해주세요.");
			return;
		}

		setLoading(true);
		setProgress(0);
		setLogs([]);
		setInjectResult(null);

		// 기존 스트림 정리
		if (abortControllerRef.current) {
			abortControllerRef.current.abort();
			abortControllerRef.current = null;
		}

		// 새로운 AbortController 생성
		const abortController = new AbortController();
		abortControllerRef.current = abortController;

		try {
			setLogs((prev) => [...prev, "주입 프로세스 시작..."]);
			setProgress(5);

			setLogs((prev) => [...prev, `대상 경로: ${targetPath}`]);
			setProgress(10);

			setLogs((prev) => [...prev, `선택된 자산: ${selectedAssets.join(", ")}`]);
			setProgress(15);

			// SSE 스트리밍으로 주입 수행
			const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/inject/stream`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					target_path: targetPath,
					assets: selectedAssets,
					options: injectionOptions,
				}),
				signal: abortController.signal,
			});

			if (!response.body) {
				throw new Error("Response body is null");
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = "";
			let finalResult: InjectResponse | null = null;

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split("\n");
				buffer = lines.pop() || "";

				for (const line of lines) {
					if (line.startsWith("data: ")) {
						try {
							const update: InjectStreamUpdate = JSON.parse(line.slice(6));

							// 진행률 업데이트
							if (update.progress !== undefined) {
								setProgress(update.progress);
							}

							// 로그 메시지 추가
							if (update.message) {
								setLogs((prev) => [...prev, update.message]);
							}

							// 완료 처리
							if (update.type === "complete" || update.type === "final") {
								if (update.result) {
									finalResult = update.result as InjectResponse;
									setInjectResult(finalResult);
								}

								// 최종 결과 요약
								if (update.result) {
									const result = update.result as InjectResponse;
									if (result.injected_files.length > 0) {
										setLogs((prev) => [...prev, `✅ 주입된 파일: ${result.injected_files.length}개`]);
									}
									if (result.backed_up_files.length > 0) {
										setLogs((prev) => [...prev, `📦 백업된 파일: ${result.backed_up_files.length}개`]);
									}
									if (result.skipped_files.length > 0) {
										setLogs((prev) => [...prev, `⏭️ 건너뛴 파일: ${result.skipped_files.length}개`]);
									}
									if (result.merged_files.length > 0) {
										setLogs((prev) => [...prev, `🔀 병합된 파일: ${result.merged_files.length}개`]);
									}
								}

								// 사후 진단 및 프롬프트 처리
								if (update.type === "final") {
									if (update.post_diagnosis) {
										onDiagnosisUpdate?.(update.post_diagnosis);
									}
								}
							}

							// 에러 처리
							if (update.type === "error") {
								setLogs((prev) => [...prev, `❌ ${update.message}`]);
								setProgress(0);
							}
						} catch (error) {
							console.error("Failed to parse SSE message:", error);
						}
					}
				}
			}

			setProgress(100);
		} catch (error: any) {
			if (error.name !== "AbortError") {
				setLogs((prev) => [...prev, `❌ 에러: ${error.message}`]);
				setProgress(0);
			}
		} finally {
			setLoading(false);
			abortControllerRef.current = null;
		}
	};

	// 컴포넌트 언마운트 시 스트림 정리
	useEffect(() => {
		return () => {
			if (abortControllerRef.current) {
				abortControllerRef.current.abort();
			}
		};
	}, []);

	return (
		<div className="space-y-6">
			<h1 className="mb-8 text-2xl font-bold text-zinc-100">AI-Native Boilerplate Injector</h1>

			{/* 스택 감지 */}
			<StackDetection onDetected={handleDetected} onPathChange={handlePathChange} />

			{/* 자산 선택 */}
			{stackInfo && <AssetSelection onSelectionChange={setSelectedAssets} />}

			{/* 주입 옵션 */}
			{selectedAssets.length > 0 && (
				<div className="mb-8 rounded-lg border border-zinc-800 bg-zinc-900/30 p-6">
					<h2 className="mb-4 text-xl font-bold text-zinc-100">주입 옵션</h2>
					<div className="flex flex-col gap-3">
						<label className="flex items-center gap-3 text-zinc-300">
							<input
								type="checkbox"
								checked={injectionOptions.backup_existing}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, backup_existing: e.target.checked })
								}
								className="h-4 w-4 rounded border-zinc-700 bg-zinc-800 text-indigo-500 focus:ring-2 focus:ring-indigo-500"
							/>
							<span>기존 파일 백업 (.bak 파일 생성)</span>
						</label>
						<label className="flex items-center gap-3 text-zinc-300">
							<input
								type="checkbox"
								checked={injectionOptions.merge_claude_config}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, merge_claude_config: e.target.checked })
								}
								className="h-4 w-4 rounded border-zinc-700 bg-zinc-800 text-indigo-500 focus:ring-2 focus:ring-indigo-500"
							/>
							<span>.claude/ 설정 병합 (기존 설정과 합성)</span>
						</label>
						<label className="flex items-center gap-3 text-zinc-300">
							<input
								type="checkbox"
								checked={injectionOptions.skip_existing}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, skip_existing: e.target.checked })
								}
								className="h-4 w-4 rounded border-zinc-700 bg-zinc-800 text-indigo-500 focus:ring-2 focus:ring-indigo-500"
							/>
							<span>기존 파일 건너뛰기</span>
						</label>
					</div>
				</div>
			)}

			{/* Apply 버튼 */}
			{selectedAssets.length > 0 && (
				<div className="mb-8">
					<button
						onClick={handleApply}
						disabled={loading}
						className={`rounded-lg px-8 py-3 text-lg font-bold transition-all ${
							loading
								? "cursor-not-allowed bg-zinc-700 text-zinc-400"
								: "bg-indigo-500 text-white hover:bg-indigo-600 hover:shadow-lg hover:shadow-indigo-500/50 active:scale-95"
						}`}
					>
						{loading ? "주입 중..." : "Apply AI-Native Standards"}
					</button>
				</div>
			)}

			{/* 진행 리포트 */}
			{(loading || injectResult) && (
				<ProgressReport
					progress={progress}
					logs={logs}
					error={injectResult?.error || null}
					targetPath={injectResult?.status === "success" ? targetPath : undefined}
				/>
			)}

			{/* 프롬프트 복사 카드 (인젝션 성공 시) */}
			{injectResult?.status === "success" && injectResult?.setup_prompt && (
				<PromptCopyCard prompt={injectResult.setup_prompt} />
			)}

			{/* 사후 진단 */}
			{injectResult?.post_diagnosis && <EnvDiagnosis diagnosis={injectResult.post_diagnosis} />}
		</div>
	);
}

