/**
 * 메인 페이지
 */

import { useState } from "react";
import InjectorStep from "@/components/InjectorStep";
import AgentHub from "@/components/AgentHub";
import LogMonitor from "@/components/LogMonitor";
import ConfigEditor from "@/components/ConfigEditor";
import ThemeToggle from "@/components/ThemeToggle";

type TabType = "injector" | "agents" | "logs" | "config";

export default function Home() {
	const [activeTab, setActiveTab] = useState<TabType>("injector");

	return (
		<main className="min-h-screen bg-gray-50 dark:bg-gray-900">
			<div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 shadow-sm">
				<div className="max-w-7xl mx-auto px-4">
					<div className="flex items-center justify-between py-4">
						<h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
							AI-Native Control Plane
						</h1>
						<nav className="flex items-center gap-4">
							<a
								href="/tutorial"
								className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
							>
								튜토리얼
							</a>
							<ThemeToggle />
						</nav>
					</div>
					
					<div className="flex border-t dark:border-gray-700">
						<button
							type="button"
							onClick={() => setActiveTab("injector")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "injector"
									? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
									: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
							}`}
						>
							Boilerplate Injector
						</button>
						<button
							type="button"
							onClick={() => setActiveTab("agents")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "agents"
									? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
									: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
							}`}
						>
							에이전트 관리
						</button>
						<button
							type="button"
							onClick={() => setActiveTab("logs")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "logs"
									? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
									: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
							}`}
						>
							로그 모니터
						</button>
						<button
							type="button"
							onClick={() => setActiveTab("config")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "config"
									? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
									: "text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
							}`}
						>
							설정 편집기
						</button>
					</div>
				</div>
			</div>
			
			<div className="max-w-7xl mx-auto px-4 py-8">
				{activeTab === "injector" && <InjectorStep />}
				{activeTab === "agents" && <AgentHub />}
				{activeTab === "logs" && <LogMonitor />}
				{activeTab === "config" && <ConfigEditor />}
			</div>
		</main>
	);
}

