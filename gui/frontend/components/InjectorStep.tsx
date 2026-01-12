/**
 * InjectorStep 컴포넌트
 * 메인 인젝터 컴포넌트
 */

import { useState } from "react";
import StackDetection from "./StackDetection";
import AssetSelection from "./AssetSelection";
import ProgressReport from "./ProgressReport";
import EnvDiagnosis from "./EnvDiagnosis";
import { injectBoilerplate } from "@/lib/api";
import type { StackInfo, InjectResponse, InjectionOptions } from "@/lib/types";

export default function InjectorStep() {
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

	const handleDetected = (info: StackInfo) => {
		setStackInfo(info);
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

		try {
			setLogs((prev) => [...prev, "주입 프로세스 시작..."]);
			setProgress(10);

			setLogs((prev) => [...prev, `대상 경로: ${targetPath}`]);
			setProgress(20);

			setLogs((prev) => [...prev, `선택된 자산: ${selectedAssets.join(", ")}`]);
			setProgress(30);

			const result = await injectBoilerplate(targetPath, selectedAssets, injectionOptions);

			setLogs((prev) => [...prev, "주입 완료"]);
			setProgress(100);

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

			setInjectResult(result);
		} catch (error: any) {
			setLogs((prev) => [...prev, `❌ 에러: ${error.message}`]);
			setProgress(0);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem" }}>
			<h1 style={{ marginBottom: "2rem", fontSize: "2rem", fontWeight: "bold" }}>
				AI-Native Boilerplate Injector
			</h1>

			{/* 스택 감지 */}
			<StackDetection onDetected={handleDetected} onPathChange={handlePathChange} />

			{/* 자산 선택 */}
			{stackInfo && <AssetSelection onSelectionChange={setSelectedAssets} />}

			{/* 주입 옵션 */}
			{selectedAssets.length > 0 && (
				<div style={{ marginBottom: "2rem" }}>
					<h2 style={{ marginBottom: "1rem", fontSize: "1.5rem", fontWeight: "bold" }}>주입 옵션</h2>
					<div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
						<label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
							<input
								type="checkbox"
								checked={injectionOptions.backup_existing}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, backup_existing: e.target.checked })
								}
							/>
							<span>기존 파일 백업 (.bak 파일 생성)</span>
						</label>
						<label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
							<input
								type="checkbox"
								checked={injectionOptions.merge_claude_config}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, merge_claude_config: e.target.checked })
								}
							/>
							<span>.claude/ 설정 병합 (기존 설정과 합성)</span>
						</label>
						<label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
							<input
								type="checkbox"
								checked={injectionOptions.skip_existing}
								onChange={(e) =>
									setInjectionOptions({ ...injectionOptions, skip_existing: e.target.checked })
								}
							/>
							<span>기존 파일 건너뛰기</span>
						</label>
					</div>
				</div>
			)}

			{/* Apply 버튼 */}
			{selectedAssets.length > 0 && (
				<div style={{ marginBottom: "2rem" }}>
					<button
						onClick={handleApply}
						disabled={loading}
						style={{
							padding: "0.75rem 2rem",
							backgroundColor: loading ? "#ccc" : "#0070f3",
							color: "white",
							border: "none",
							borderRadius: "4px",
							cursor: loading ? "not-allowed" : "pointer",
							fontSize: "1.1rem",
							fontWeight: "bold",
						}}
					>
						{loading ? "주입 중..." : "Apply AI-Native Standards"}
					</button>
				</div>
			)}

			{/* 진행 리포트 */}
			{(loading || injectResult) && (
				<ProgressReport progress={progress} logs={logs} error={injectResult?.error || null} />
			)}

			{/* 사후 진단 */}
			{injectResult?.post_diagnosis && <EnvDiagnosis diagnosis={injectResult.post_diagnosis} />}
		</div>
	);
}

