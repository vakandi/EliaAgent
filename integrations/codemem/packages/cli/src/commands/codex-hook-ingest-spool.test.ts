import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
	lockTtlSeconds as claudeLockTtlSeconds,
	spoolDir as claudeSpoolDir,
	LockBusyError,
} from "./claude-hook-ingest-spool.js";
import {
	CodexHookLockBusyError,
	codexHookLockTtlSeconds,
	codexHookSpoolDir,
} from "./codex-hook-ingest-spool.js";

describe("codex-hook-ingest-spool factory config", () => {
	const savedEnv: Record<string, string | undefined> = {};
	const keys = [
		"CODEMEM_CLAUDE_HOOK_LOCK_TTL_S",
		"CODEMEM_CLAUDE_HOOK_SPOOL_DIR",
		"CODEMEM_CODEX_HOOK_LOCK_TTL_S",
		"CODEMEM_CODEX_HOOK_SPOOL_DIR",
	];

	function setEnv(key: string, value: string | undefined): void {
		if (value === undefined) delete process.env[key];
		else process.env[key] = value;
	}

	beforeEach(() => {
		for (const key of keys) savedEnv[key] = process.env[key];
	});

	afterEach(() => {
		for (const [key, value] of Object.entries(savedEnv)) setEnv(key, value);
	});

	it("defaults Codex TTL to 120s and honors CODEMEM_CODEX_HOOK_LOCK_TTL_S", () => {
		setEnv("CODEMEM_CLAUDE_HOOK_LOCK_TTL_S", undefined);
		setEnv("CODEMEM_CODEX_HOOK_LOCK_TTL_S", undefined);
		expect(codexHookLockTtlSeconds()).toBe(120);
		expect(claudeLockTtlSeconds()).toBe(300);

		setEnv("CODEMEM_CODEX_HOOK_LOCK_TTL_S", "45");
		expect(codexHookLockTtlSeconds()).toBe(45);
		expect(claudeLockTtlSeconds()).toBe(300);
	});

	it("keeps Claude and Codex on separate spool directories", () => {
		setEnv("CODEMEM_CLAUDE_HOOK_SPOOL_DIR", undefined);
		setEnv("CODEMEM_CODEX_HOOK_SPOOL_DIR", undefined);
		expect(claudeSpoolDir()).toMatch(/claude-hook-spool$/);
		expect(codexHookSpoolDir()).toMatch(/codex-hook-spool$/);
		expect(claudeSpoolDir()).not.toBe(codexHookSpoolDir());

		setEnv("CODEMEM_CLAUDE_HOOK_SPOOL_DIR", "/tmp/claude-spool");
		setEnv("CODEMEM_CODEX_HOOK_SPOOL_DIR", "/tmp/codex-spool");
		expect(claudeSpoolDir()).toBe("/tmp/claude-spool");
		expect(codexHookSpoolDir()).toBe("/tmp/codex-spool");
	});

	it("uses a distinct lock-busy error identity from Claude", () => {
		const codexErr = new CodexHookLockBusyError();
		const claudeErr = new LockBusyError();
		expect(codexErr.name).toBe("CodexHookLockBusyError");
		expect(codexErr.message).toBe("codex-hook-ingest lock busy");
		expect(claudeErr.name).toBe("LockBusyError");
		expect(codexErr.name).not.toBe(claudeErr.name);
	});
});
