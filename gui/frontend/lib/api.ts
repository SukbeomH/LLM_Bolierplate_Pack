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

// Config API
export interface ClaudeSections {
	lessons_learned: string;
	team_standards: string;
}

export interface ToolStatus {
	mise: { installed: boolean; version: string | null };
	uv: { installed: boolean; version: string | null };
	mcp: { installed: boolean; config_exists: boolean };
}

export const getClaudeSections = async (): Promise<ClaudeSections> => {
	const response = await api.get<ClaudeSections>("/api/v1/config/claude/sections");
	return response.data;
};

export const updateClaudeSection = async (
	section: string,
	content: string,
	action: "append" | "replace" = "append",
): Promise<{ status: string; message: string }> => {
	const response = await api.post("/api/v1/config/claude/sections", {
		section,
		content,
		action,
	});
	return response.data;
};

export const checkEnv = async (targetPath: string): Promise<{
	return_code: number;
	output: string;
	error?: string;
}> => {
	const response = await api.get("/api/v1/config/env/check", {
		params: { target_path: targetPath },
	});
	return response.data;
};

export const updateEnv = async (
	targetPath: string,
	envVars: Record<string, string>,
): Promise<{ status: string; message: string }> => {
	const response = await api.post("/api/v1/config/env/update", {
		target_path: targetPath,
		env_vars: envVars,
	});
	return response.data;
};

export const checkTools = async (): Promise<ToolStatus> => {
	const response = await api.get<ToolStatus>("/api/v1/config/tools/check");
	return response.data;
};

