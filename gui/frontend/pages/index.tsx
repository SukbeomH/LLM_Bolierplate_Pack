/**
 * 메인 페이지
 */

import { useState } from "react";
import InjectorStep from "@/components/InjectorStep";
import AgentHub from "@/components/AgentHub";
import LogMonitor from "@/components/LogMonitor";

type TabType = "injector" | "agents" | "logs";

export default function Home() {
	const [activeTab, setActiveTab] = useState<TabType>("injector");

	return (
		<main className="min-h-screen bg-gray-50">
			<div className="bg-white border-b shadow-sm">
				<div className="max-w-7xl mx-auto px-4">
					<div className="flex items-center justify-between py-4">
						<h1 className="text-2xl font-bold text-gray-800">
							AI-Native Control Plane
						</h1>
						<nav className="flex gap-4">
							<a
								href="/tutorial"
								className="px-4 py-2 text-gray-600 hover:text-gray-800"
							>
								튜토리얼
							</a>
						</nav>
					</div>
					
					<div className="flex border-t">
						<button
							type="button"
							onClick={() => setActiveTab("injector")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "injector"
									? "border-b-2 border-blue-500 text-blue-600"
									: "text-gray-600 hover:text-gray-800"
							}`}
						>
							Boilerplate Injector
						</button>
						<button
							type="button"
							onClick={() => setActiveTab("agents")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "agents"
									? "border-b-2 border-blue-500 text-blue-600"
									: "text-gray-600 hover:text-gray-800"
							}`}
						>
							에이전트 관리
						</button>
						<button
							type="button"
							onClick={() => setActiveTab("logs")}
							className={`px-6 py-3 font-semibold ${
								activeTab === "logs"
									? "border-b-2 border-blue-500 text-blue-600"
									: "text-gray-600 hover:text-gray-800"
							}`}
						>
							로그 모니터
						</button>
					</div>
				</div>
			</div>
			
			<div className="max-w-7xl mx-auto px-4 py-8">
				{activeTab === "injector" && <InjectorStep />}
				{activeTab === "agents" && <AgentHub />}
				{activeTab === "logs" && <LogMonitor />}
			</div>
		</main>
	);
}

