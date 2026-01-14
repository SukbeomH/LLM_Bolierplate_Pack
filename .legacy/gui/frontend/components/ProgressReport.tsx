/**
 * ProgressReport 컴포넌트
 * 진행 리포트 UI - Cybernetic Minimalism Theme
 */

import { useState } from "react";
import { motion } from "framer-motion";
import { Copy, Check, ExternalLink } from "lucide-react";
import { useToast } from "./ToastProvider";

interface ProgressReportProps {
	progress: number; // 0-100
	logs: string[];
	error?: string | null;
	targetPath?: string; // 주입 대상 프로젝트 경로
}

export default function ProgressReport({ progress, logs, error, targetPath }: ProgressReportProps) {
	const [copied, setCopied] = useState(false);
	const { showToast } = useToast();

	const isSuccess = progress === 100 && !error && targetPath;

	const handleCopyCommand = async () => {
		if (!targetPath) return;
		const command = `cd ${targetPath} && mise run gui`;
		try {
			await navigator.clipboard.writeText(command);
			setCopied(true);
			showToast("명령어가 클립보드에 복사되었습니다", "success");
			setTimeout(() => setCopied(false), 2000);
		} catch (err) {
			showToast("복사에 실패했습니다", "error");
		}
	};

	return (
		<div className="mb-8">
			<h2 className="mb-4 text-2xl font-bold text-zinc-100">진행 리포트</h2>

			{/* 프로그레스 바 */}
			<div className="mb-4">
				<div className="h-6 w-full overflow-hidden rounded-full bg-zinc-800">
					<div
						className={`h-full transition-all duration-300 ${
							progress === 100 ? "bg-green-500" : "bg-indigo-500"
						}`}
						style={{ width: `${progress}%` }}
					/>
				</div>
				<div className="mt-2 text-right text-sm font-medium text-zinc-300">
					{progress}%
				</div>
			</div>

			{/* 로그 */}
			<div className="mb-4 max-h-[300px] overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/50 p-4 font-mono text-sm text-zinc-200">
				{logs.length === 0 ? (
					<div className="text-zinc-500">로그가 없습니다.</div>
				) : (
					logs.map((log, index) => (
						<div key={index} className="mb-1 text-zinc-200">
							{log}
						</div>
					))
				)}
			</div>

			{/* 에러 메시지 */}
			{error && (
				<div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
					<span className="font-semibold">❌</span> {error}
				</div>
			)}

			{/* 인젝션 성공 시 이동 및 실행 가이드 */}
			{isSuccess && (
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.3 }}
					className="mt-6 rounded-lg border border-green-500/30 bg-green-500/10 p-6"
				>
					<div className="mb-4 flex items-center gap-2">
						<span className="text-2xl">🚀</span>
						<h3 className="text-lg font-semibold text-green-400">인젝션 성공!</h3>
					</div>
					<p className="mb-4 text-zinc-300">
						이제 주입된 프로젝트 내부에서 GUI를 실행하세요. 원본 보일러플레이트 GUI를 종료하고, 아래 명령어를 실행하여 주입된 프로젝트 전용 Control Plane을 시작하세요.
					</p>

					<div className="mb-4 rounded-lg border border-zinc-800 bg-zinc-950 p-4">
						<div className="mb-2 flex items-center justify-between">
							<span className="text-sm font-medium text-zinc-400">실행 명령어</span>
							<button
								onClick={handleCopyCommand}
								className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
									copied
										? "bg-green-500/20 text-green-400 border border-green-500/30"
										: "bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/20 active:scale-95"
								}`}
							>
								{copied ? (
									<>
										<Check className="h-4 w-4" />
										<span>복사됨</span>
									</>
								) : (
									<>
										<Copy className="h-4 w-4" />
										<span>복사</span>
									</>
								)}
							</button>
						</div>
						<code className="block font-mono text-sm text-zinc-100">
							cd {targetPath} && mise run gui
						</code>
					</div>

					<div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
						<div className="mb-2 flex items-center gap-2">
							<ExternalLink className="h-4 w-4 text-indigo-400" />
							<span className="text-sm font-semibold text-zinc-300">다음 단계</span>
						</div>
						<ul className="ml-6 list-disc space-y-1 text-sm text-zinc-400">
							<li>주입된 프로젝트의 로컬 로그가 실시간으로 매핑됩니다</li>
							<li>프로젝트 전용 Agent Hub에서 커스터마이징된 스킬을 사용할 수 있습니다</li>
							<li>CLAUDE.md 수정 사항이 해당 프로젝트에 즉시 반영됩니다</li>
						</ul>
					</div>
				</motion.div>
			)}
		</div>
	);
}

