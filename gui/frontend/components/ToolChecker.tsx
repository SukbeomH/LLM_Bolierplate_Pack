/**
 * ToolChecker 컴포넌트
 * 필수 도구(mise, uv, mcp)의 설치 상태를 확인하고 표시합니다.
 */

import { useState, useEffect } from "react";
import { checkTools } from "@/lib/api";
import type { ToolStatus } from "@/lib/api";

interface ToolCheckerProps {
	onStatusChange?: (allInstalled: boolean) => void;
}

export default function ToolChecker({ onStatusChange }: ToolCheckerProps) {
	const [toolStatus, setToolStatus] = useState<ToolStatus | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchToolStatus = async () => {
			try {
				const status = await checkTools();
				setToolStatus(status);
				
				const allInstalled =
					status.mise.installed &&
					status.uv.installed &&
					status.mcp.installed;
				
				onStatusChange?.(allInstalled);
			} catch (error) {
				console.error("Failed to check tools:", error);
			} finally {
				setLoading(false);
			}
		};

		fetchToolStatus();
		const interval = setInterval(fetchToolStatus, 5000); // 5초마다 갱신

		return () => clearInterval(interval);
	}, [onStatusChange]);

	if (loading) {
		return (
			<div className="flex items-center gap-2 text-gray-600">
				<div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
				<span>도구 상태 확인 중...</span>
			</div>
		);
	}

	if (!toolStatus) {
		return <div className="text-red-600">도구 상태를 확인할 수 없습니다.</div>;
	}

	const tools = [
		{
			name: "mise",
			label: "Mise",
			status: toolStatus.mise,
			installCmd: "curl https://mise.run | sh",
		},
		{
			name: "uv",
			label: "uv",
			status: toolStatus.uv,
			installCmd: "curl -LsSf https://astral.sh/uv/install.sh | sh",
		},
		{
			name: "mcp",
			label: "MCP Config",
			status: toolStatus.mcp,
			installCmd: ".mcp.json 파일이 필요합니다.",
		},
	];

	return (
		<div className="space-y-3">
			<h3 className="text-lg font-semibold text-gray-800">필수 도구 상태</h3>
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				{tools.map((tool) => (
					<div
						key={tool.name}
						className={`p-4 rounded-lg border-2 ${
							tool.status.installed
								? "border-green-500 bg-green-50"
								: "border-red-500 bg-red-50"
						}`}
					>
						<div className="flex items-center justify-between mb-2">
							<span className="font-medium text-gray-800">{tool.label}</span>
							{tool.status.installed ? (
								<span className="text-green-600">✓</span>
							) : (
								<span className="text-red-600">✗</span>
							)}
						</div>
						{tool.status.installed && "version" in tool.status && tool.status.version && (
							<div className="text-sm text-gray-600">
								{tool.status.version}
							</div>
						)}
						{!tool.status.installed && (
							<div className="text-xs text-gray-600 mt-2">
								설치: <code className="bg-gray-100 px-1 rounded">{tool.installCmd}</code>
							</div>
						)}
					</div>
				))}
			</div>
		</div>
	);
}

