/**
 * Next.js App 컴포넌트
 */

import type { AppProps } from "next/app";
import "@/styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
	return <Component {...pageProps} />;
}

