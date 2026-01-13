/**
 * ThemeToggle 컴포넌트
 * 다크 모드 토글 버튼
 */

import { useEffect, useState } from "react";

export default function ThemeToggle() {
	const [darkMode, setDarkMode] = useState(false);

	useEffect(() => {
		// localStorage에서 다크 모드 설정 불러오기
		const saved = localStorage.getItem("darkMode");
		if (saved !== null) {
			const isDark = saved === "true";
			setDarkMode(isDark);
			if (isDark) {
				document.documentElement.classList.add("dark");
			} else {
				document.documentElement.classList.remove("dark");
			}
		} else {
			// 시스템 설정 확인
			const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
			setDarkMode(prefersDark);
			if (prefersDark) {
				document.documentElement.classList.add("dark");
			}
		}
	}, []);

	const toggleDarkMode = () => {
		const newDarkMode = !darkMode;
		setDarkMode(newDarkMode);
		localStorage.setItem("darkMode", String(newDarkMode));
		
		if (newDarkMode) {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
	};

	return (
		<button
			type="button"
			onClick={toggleDarkMode}
			className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
			aria-label="Toggle dark mode"
		>
			{darkMode ? (
				<svg
					className="w-5 h-5 text-gray-800 dark:text-gray-200"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
					/>
				</svg>
			) : (
				<svg
					className="w-5 h-5 text-gray-800 dark:text-gray-200"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
					/>
				</svg>
			)}
		</button>
	);
}

