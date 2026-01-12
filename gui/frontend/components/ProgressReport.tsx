/**
 * ProgressReport 컴포넌트
 * 진행 리포트 UI
 */

interface ProgressReportProps {
	progress: number; // 0-100
	logs: string[];
	error?: string | null;
}

export default function ProgressReport({ progress, logs, error }: ProgressReportProps) {
	return (
		<div style={{ marginBottom: "2rem" }}>
			<h2 style={{ marginBottom: "1rem", fontSize: "1.5rem", fontWeight: "bold" }}>진행 리포트</h2>

			{/* 프로그레스 바 */}
			<div style={{ marginBottom: "1rem" }}>
				<div
					style={{
						width: "100%",
						height: "24px",
						backgroundColor: "#e0e0e0",
						borderRadius: "12px",
						overflow: "hidden",
					}}
				>
					<div
						style={{
							width: `${progress}%`,
							height: "100%",
							backgroundColor: progress === 100 ? "#4caf50" : "#0070f3",
							transition: "width 0.3s ease",
						}}
					/>
				</div>
				<div style={{ textAlign: "right", marginTop: "0.25rem", fontSize: "0.9rem", color: "#666" }}>
					{progress}%
				</div>
			</div>

			{/* 로그 */}
			<div
				style={{
					padding: "1rem",
					backgroundColor: "#1e1e1e",
					color: "#d4d4d4",
					borderRadius: "4px",
					fontFamily: "monospace",
					fontSize: "0.9rem",
					maxHeight: "300px",
					overflowY: "auto",
					marginBottom: "1rem",
				}}
			>
				{logs.length === 0 ? (
					<div style={{ color: "#888" }}>로그가 없습니다.</div>
				) : (
					logs.map((log, index) => (
						<div key={index} style={{ marginBottom: "0.25rem" }}>
							{log}
						</div>
					))
				)}
			</div>

			{/* 에러 메시지 */}
			{error && (
				<div
					style={{
						padding: "1rem",
						backgroundColor: "#fee",
						color: "#c33",
						borderRadius: "4px",
						border: "1px solid #fcc",
					}}
				>
					❌ {error}
				</div>
			)}
		</div>
	);
}

