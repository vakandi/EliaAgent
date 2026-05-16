/**
 * Plugin-observer routes — lets the OpenCode plugin act as the LLM caller.
 *
 * GET  /api/plugin-observer/pending  — returns next batch + built prompts
 * POST /api/plugin-observer/result   — receives LLM output, runs ingest
 *
 * Flow:
 *   1. Plugin polls GET /pending every ~30s
 *   2. Viewer returns system+user prompts for the next unprocessed batch
 *   3. Plugin calls client.session.prompt() with those prompts via OpenCode SDK
 *   4. Plugin POSTs the raw LLM XML output to /result
 *   5. Viewer parses XML, runs ingest pipeline, stores memories
 */

import {
	buildObserverPrompt,
	buildSessionContext,
	buildTranscript,
	ingest,
	normalizeEventsForSessionContext,
	parseObserverResponse,
	truncateObserverTranscript,
	type IngestOptions,
	type MemoryStore,
	type RawEventSweeper,
} from "@codemem/core";
import { Hono } from "hono";

type StoreFactory = () => MemoryStore;

/** In-memory claim lock: batchId → claimedAt ms. Prevents double-processing. */
const claimedBatches = new Map<number, number>();
const CLAIM_TTL_MS = 5 * 60 * 1000;

function pruneStaleClaims() {
	const now = Date.now();
	for (const [id, at] of claimedBatches) {
		if (now - at > CLAIM_TTL_MS) claimedBatches.delete(id);
	}
}

export function pluginObserverRoutes(getStore: StoreFactory, _sweeper?: RawEventSweeper | null) {
	const app = new Hono();

	app.get("/api/plugin-observer/report", (c) => {
		const store = getStore();
		const db = store.db;

		const batchStatusCounts = db
			.prepare("SELECT status, COUNT(*) AS count FROM raw_event_flush_batches GROUP BY status ORDER BY count DESC")
			.all();

		const recentBatches = db
			.prepare(
				`SELECT id, source, stream_id, start_event_seq, end_event_seq, status, attempt_count, error_message, updated_at
         FROM raw_event_flush_batches
         ORDER BY updated_at DESC
         LIMIT 50`,
			)
			.all();

		const errorCounts = db
			.prepare(
				`SELECT
           SUM(CASE WHEN status IN ('error','failed') THEN 1 ELSE 0 END) AS errored,
           SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END) AS claimed,
           SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
         FROM raw_event_flush_batches`,
			)
			.get() as { errored?: number; claimed?: number; pending?: number } | undefined;

		const memoryByActor = db
			.prepare(
				`SELECT
           COALESCE(NULLIF(TRIM(actor_id),''), 'unknown') AS actor_id,
           COALESCE(NULLIF(TRIM(actor_display_name),''), NULL) AS actor_display_name,
           COUNT(*) AS count,
           MAX(created_at) AS last_created_at
         FROM memory_items
         WHERE active = 1
         GROUP BY COALESCE(NULLIF(TRIM(actor_id),''), 'unknown'), COALESCE(NULLIF(TRIM(actor_display_name),''), NULL)
         ORDER BY count DESC
         LIMIT 50`,
			)
			.all();

		return c.json({
			ok: true,
			batches: {
				status_counts: batchStatusCounts,
				recent: recentBatches,
				counts: {
					errored: Number(errorCounts?.errored || 0),
					claimed: Number(errorCounts?.claimed || 0),
					pending: Number(errorCounts?.pending || 0),
				},
			},
			memories: {
				by_actor: memoryByActor,
			},
		});
	});

	app.post("/api/plugin-observer/retry-errors", (c) => {
		const store = getStore();
		const db = store.db;
		// Move errored/failed batches back to pending so the plugin observer can retry.
		const info = db
			.prepare(
				`UPDATE raw_event_flush_batches
         SET status='pending', updated_at=datetime('now')
         WHERE status IN ('error','failed')`,
			)
			.run();
		return c.json({ ok: true, retried: Number(info?.changes || 0) });
	});

	/**
	 * GET /api/plugin-observer/pending
	 *
	 * Returns the next pending batch with system + user prompts already built.
	 * Returns 204 when nothing is pending.
	 */
	app.get("/api/plugin-observer/pending", (c) => {
		pruneStaleClaims();
		const store = getStore();

		// First try sessions with existing pending batches
		let sessions = store.rawEventSessionsWithPendingQueue(1);
		// If none, try idle sessions with unflushed events (no batch needed)
		if (sessions.length === 0) {
			const idleBefore = Date.now() - 60_000; // idle for at least 1 min
			sessions = store.rawEventSessionsPendingIdleFlush(idleBefore, 1);
		}
		if (sessions.length === 0) return c.body(null, 204);

		const { source, streamId } = sessions[0]!;

		const lastFlushed = store.rawEventFlushState(streamId, source);
		const events = store.rawEventsSinceBySeq(streamId, source, lastFlushed, 100);
		if (events.length === 0) return c.body(null, 204);

		const seqs = events.map((e) => Number(e.event_seq)).filter(Number.isFinite);
		if (seqs.length === 0) return c.body(null, 204);
		const startSeq = Math.min(...seqs);
		const endSeq = Math.max(...seqs);

		// Get or create batch record for tracking.
		const { batchId, status } = store.getOrCreateRawEventFlushBatch(
			streamId, source, startSeq ?? 0, endSeq ?? 0, "raw_events_v1",
		);
		console.log(`[plugin-observer] pending: streamId=${streamId} batchId=${batchId} status=${status} events=${events.length} claimed=${claimedBatches.has(batchId)}`);
		// Also write to a debug file
		try { require("fs").appendFileSync(require("os").homedir() + "/.codemem/observer-debug.log", `${new Date().toISOString()} pending: streamId=${streamId} batchId=${batchId} status=${status} events=${events.length} claimed=${claimedBatches.has(batchId)}\n`); } catch {}		if (status === "completed") {
			store.updateRawEventFlushState(streamId, endSeq, source);
			return c.body(null, 204);
		}
		if (claimedBatches.has(batchId)) return c.body(null, 204);
		// Reset stuck/started/claimed batches so we can claim them
		if (status === "started" || status === "error" || status === "failed" || status === "claimed") {
			store.updateRawEventFlushBatchStatus(batchId, "pending");
		}
		if (!store.claimRawEventFlushBatch(batchId)) {
			console.log(`[plugin-observer] claimRawEventFlushBatch failed for batchId=${batchId}`);
			try { require("fs").appendFileSync(require("os").homedir() + "/.codemem/observer-debug.log", `${new Date().toISOString()} claim FAILED batchId=${batchId}\n`); } catch {}
			return c.body(null, 204);
		}
		try { require("fs").appendFileSync(require("os").homedir() + "/.codemem/observer-debug.log", `${new Date().toISOString()} claim OK batchId=${batchId}\n`); } catch {}
		claimedBatches.set(batchId, Date.now());

		// Build prompts
		const meta = store.rawEventSessionMeta(streamId, source);
		const normalized = normalizeEventsForSessionContext(events);
		const sessionContext = buildSessionContext(normalized);
		const project = (meta.project as string) ?? null;
		const transcript = buildTranscript(normalized);

		const { system, user } = buildObserverPrompt({
			project,
			userPrompt: sessionContext.firstPrompt ?? "",
			promptNumber: sessionContext.promptCount ?? null,
			transcript: truncateObserverTranscript(transcript, 4000),
			toolEvents: [],
			lastAssistantMessage: null,
			includeSummary: true,
			diffSummary: "",
			recentFiles: "",
		});

		return c.json({
			batch_id: batchId,
			session_id: streamId,
			source,
			start_seq: startSeq,
			end_seq: endSeq,
			system,
			user,
		});
	});

	/**
	 * POST /api/plugin-observer/result
	 *
	 * Body: { batch_id, session_id, source, start_seq, end_seq, llm_output }
	 */
	app.post("/api/plugin-observer/result", async (c) => {
		let body: Record<string, unknown>;
		try {
			body = await c.req.json();
		} catch {
			return c.json({ error: "invalid json" }, 400);
		}

		const batchId = Number(body.batch_id);
		const sessionId = String(body.session_id ?? "");
		const source = String(body.source ?? "opencode");
		const startSeq = Number(body.start_seq ?? 0);
		const endSeq = Number(body.end_seq ?? 0);
		const llmOutput = String(body.llm_output ?? "");

		if (!batchId || !sessionId || !llmOutput) {
			return c.json({ error: "batch_id, session_id, llm_output required" }, 400);
		}

		const store = getStore();

		try {
			const parsed = parseObserverResponse(llmOutput);
			const lastFlushed = store.rawEventFlushState(sessionId, source);
			const events = store.rawEventsSinceBySeq(sessionId, source, lastFlushed, 100);
			const meta = store.rawEventSessionMeta(sessionId, source);
			const normalized = normalizeEventsForSessionContext(events);
			const sessionContext = buildSessionContext(normalized);
			// Scope memories per agent when possible.
			// The OpenCode plugin can scope raw-event sessions by "project/agent".
			// Surface that agent into memory provenance so the Feed agent selector works.
			try {
				const project = String((meta.project as string) ?? "").trim();
				const candidate = project.includes("/") ? project.split("/").pop() : "";
				const agent = (candidate ?? "").trim();
				if (agent) {
					(sessionContext as unknown as Record<string, unknown>).actor_id = agent;
					(sessionContext as unknown as Record<string, unknown>).actor_display_name = agent;
				}
			} catch {}
			sessionContext.opencodeSessionId = sessionId;
			sessionContext.source = source;
			sessionContext.streamId = sessionId;
			sessionContext.flusher = "raw_events";
			sessionContext.flushBatch = { batch_id: batchId, start_event_seq: startSeq, end_event_seq: endSeq };

			// Mock observer that returns the pre-computed LLM result
			const mockObserver = {
				observe: async () => ({ raw: llmOutput, parsed, provider: "opencode", model: "big-pickle" }),
				observeStructuredJson: async () => null,
				getStatus: () => ({
					provider: "opencode", model: "big-pickle", runtime: "opencode_plugin",
					auth: { source: "none", type: "none", hasToken: false, method: "none", token_present: false },
				}),
				toConfig: () => ({}),
				tierRoutingEnabled: false,
				simpleProvider: null, simpleModel: null,
				richProvider: null, richModel: null,
			} as unknown as IngestOptions["observer"];

			await ingest(
				{
					cwd: (meta.cwd as string) ?? process.cwd(),
					project: (meta.project as string) ?? undefined,
					startedAt: (meta.started_at as string) ?? new Date().toISOString(),
					events,
					sessionContext,
				},
				store,
				{ observer: mockObserver },
			);

			store.updateRawEventFlushBatchStatus(batchId, "completed");
			store.updateRawEventFlushState(sessionId, endSeq, source);
			claimedBatches.delete(batchId);

			return c.json({ ok: true, batch_id: batchId });
		} catch (err) {
			const errMsg = String((err as Error).message ?? "");
			// Gracefully handle "no storable output" — batch has no meaningful events.
			// Instead of failing (which causes observer retry loops), mark it completed
			// and advance the flush state so events don't accumulate.
			if (errMsg.includes("observer produced no storable output")) {
				store.updateRawEventFlushBatchStatus(batchId, "completed");
				store.updateRawEventFlushState(sessionId, endSeq, source);
				claimedBatches.delete(batchId);
				return c.json({ ok: true, batch_id: batchId, note: "no storable output" });
			}
			claimedBatches.delete(batchId);
			store.recordRawEventFlushBatchFailure(batchId, {
				message: errMsg.slice(0, 280),
				errorType: (err as Error).name ?? "Error",
				observerProvider: "opencode",
				observerModel: "big-pickle",
				observerRuntime: "opencode_plugin",
				observerAuthSource: null,
				observerAuthType: null,
				observerErrorCode: null,
				observerErrorMessage: null,
			});
			return c.json({ error: errMsg }, 500);
		}
	});

	return app;
}
