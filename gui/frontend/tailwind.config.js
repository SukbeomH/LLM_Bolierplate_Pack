/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./pages/**/*.{js,ts,jsx,tsx,mdx}",
		"./components/**/*.{js,ts,jsx,tsx,mdx}",
	],
	darkMode: "class", // 클래스 기반 다크 모드
	theme: {
		extend: {},
	},
	plugins: [],
};

