/**
 * API 클라이언트
 */

import axios from "axios";
import type { StackInfo, InjectResponse, InjectionOptions } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

export const detectStack = async (targetPath: string): Promise<StackInfo> => {
	const response = await api.post<StackInfo>("/api/v1/detect", {
		target_path: targetPath,
	});
	return response.data;
};

export const injectBoilerplate = async (
	targetPath: string,
	assets: string[],
	options: InjectionOptions,
): Promise<InjectResponse> => {
	const response = await api.post<InjectResponse>("/api/v1/inject", {
		target_path: targetPath,
		assets,
		options,
	});
	return response.data;
};

