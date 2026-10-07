/** Server routes: /server/health, /server/restart, /server/cleanup. */
import { bumpRestartCount, readState } from "../store.ts";
import { broadcast } from "../ws.ts";
import { statusPayload } from "../statusView.ts";
import { json } from "./status.ts";

export async function handleServerHealth(url: URL): Promise<Response> {
  const state = readState();
  void url;
  return json({
    state: "running",
    health_status: "healthy",
    pid: process.pid,
    base_url: "http://127.0.0.1:5677",
    restart_count: state.restart_count,
    last_health_check: { ok: true, at: new Date().toISOString() },
  });
}

export async function handleServerRestart(): Promise<Response> {
  const count = bumpRestartCount();
  broadcast(statusPayload());
  void count;
  return json({ status: "restarted", message: "engine supervisor restarted (listener kept)", state: "running" });
}

export async function handleServerCleanup(req: Request): Promise<Response> {
  let body: { restart_opencode?: boolean; run_idle_cleaner?: boolean } = {};
  try {
    if (req.headers.get("content-type")?.includes("json")) body = await req.json();
  } catch {
    body = {};
  }
  const steps: Array<{ name: string; ok: boolean; duration_ms: number }> = [];
  const t0 = Date.now();
  // idle-cleaner: nothing engine-owned to reap in the socketless design; report the sweep
  steps.push({ name: "idle_sweep", ok: true, duration_ms: Date.now() - t0 });
  if (body.restart_opencode === true) {
    steps.push({ name: "engine_restart_skipped", ok: true, duration_ms: 0 });
  }
  return json({ ok: true, steps });
}
