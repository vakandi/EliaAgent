import { payloadError, readJsonPayload } from "./internal";

export async function loadObserverReport(): Promise<Record<string, unknown>> {
	return fetch("/api/plugin-observer/report").then(async (resp) => {
		const { payload } = await readJsonPayload(resp);
		if (!resp.ok) throw new Error(payloadError(payload) ?? `Observer report failed (${resp.status})`);
		return payload as Record<string, unknown>;
	});
}

export async function retryObserverErrors(): Promise<{ ok: boolean; retried: number }> {
	return fetch("/api/plugin-observer/retry-errors", { method: "POST" }).then(async (resp) => {
		const { payload } = await readJsonPayload(resp);
		if (!resp.ok) throw new Error(payloadError(payload) ?? `Observer retry failed (${resp.status})`);
		return payload as { ok: boolean; retried: number };
	});
}

