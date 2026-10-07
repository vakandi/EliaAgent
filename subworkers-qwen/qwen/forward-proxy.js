import http from 'http';
import net from 'net';
import fs from 'fs';
import crypto from 'crypto';

// Mirror of EliaAI/subworkers/server/app/forward-proxy.js (same LRU egress +
// 4-minute rotation, same pool format). Runs container-local in elia-qwen-srv
// so the Qwen daemon gets the SAME residential-rotation system as live Elia.
// Extra DIRECT bypass: host.docker.internal (host zen gateway :18898) can
// never be dialed through a public residential proxy, so it goes direct.
const PORT = 3128;
const POOL_PATH = '/data/proxies.txt';
// LRU egress: all traffic uses `current`; every ROTATE_MS the egress
// switches to the oldest-used (least-recently-used) pool proxy — even
// mid-session. No quarantine, no per-request round-robin.
const ROTATE_MS = 4 * 60 * 1000;
const DIRECT_MATCH = ['127.0.0.1', 'localhost', '::1', 'host.docker.internal'];
// Internal header forcing pool egress for chained requests (attest :3129 ->
// forward :3128). Stripped before hitting upstream; never sent by clients.
const FORCE_POOL_HEADER = 'x-qwen-egress-rotate';
let pool = [];
const lastUsed = new Map(); // "host:port" -> epoch ms (missing = never used)
let current = null;

function loadPool(){
  try{
    const txt=fs.readFileSync(POOL_PATH,'utf8');
    pool=txt.split('\n').map(l=>l.split('|')[0].trim()).filter(Boolean).map(line=>{
      const [ip,port,user,pass]=line.split(':');
      if(!ip||!port||!user||!pass) return null;
      return {host:ip,port:parseInt(port),user,pass};
    }).filter(Boolean);
    console.log(`[forward] pool ${pool.length} first ${pool[0]?.host}`);
  }catch(e){ console.log('[forward] pool fail',e.message); }
}
loadPool();

function pkey(p){ return `${p.host}:${p.port}`; }

function pickLRU(excludeKey){
  let best = null, bestTs = Infinity;
  for (const p of pool) {
    const k = pkey(p);
    if (excludeKey && k === excludeKey && pool.length > 1) continue;
    const ts = lastUsed.has(k) ? lastUsed.get(k) : 0;
    if (ts < bestTs) { bestTs = ts; best = p; }
  }
  return best;
}

function useEgress(){
  if(!pool.length) return null;
  if(!current || !pool.includes(current)){
    current = pickLRU(null);
    if(current) lastUsed.set(pkey(current), Date.now());
  }
  return current;
}

function rotateTick(){
  loadPool();
  const valid = new Set(pool.map(pkey));
  for (const k of [...lastUsed.keys()]) if(!valid.has(k)) lastUsed.delete(k);
  if(!pool.length){ console.log('[forward] ROTATE skipped: empty pool'); return; }
  const oldK = current ? pkey(current) : 'none';
  current = pickLRU(oldK) || current;
  if(current) lastUsed.set(pkey(current), Date.now());
  console.log(`[forward] ROTATE ${oldK} -> ${current ? pkey(current) : 'none'} pool=${pool.length} ts=${new Date().toISOString()}`);
}

// Initial egress = oldest-used (all stamps empty -> pool[0]); rotate on timer.
current = pickLRU(null);
if(current) lastUsed.set(pkey(current), Date.now());
console.log(`[forward] initial egress ${current ? pkey(current) : 'none'} rotate_every_ms=${ROTATE_MS}`);
setInterval(rotateTick, ROTATE_MS).unref?.();

function isDirect(url){
  return DIRECT_MATCH.some(h => url.includes(h));
}

const server=http.createServer((req,res)=>{
  const url = req.url || "";
  // Ops endpoint for sibling containers (shim calls this on engine 429):
  // force immediate rotation to the oldest-unused egress, bypassing the
  // 4-min timer. Compose-internal only (never published to host).
  if (req.method === 'POST' && url === '/__rotate') {
    loadPool();
    const oldK = current ? pkey(current) : 'none';
    current = pickLRU(oldK) || current;
    if (current) lastUsed.set(pkey(current), Date.now());
    const now = current ? pkey(current) : 'none';
    console.log(`[forward] ROTATE-ON-ERROR ${oldK} -> ${now} pool=${pool.length}`);
    res.writeHead(200, {'content-type': 'application/json'});
    res.end(JSON.stringify({egress: now}));
    return;
  }
  // Chained callers (the :3129 attest listener) set FORCE_POOL so stamped
  // inference calls rotate IPs. But pool egress can never reach loopback /
  // host targets (a residential exit cannot route back to host.docker.internal)
  // — DIRECT targets always go direct, pool is for internet hosts only.
  const forcePool = req.headers[FORCE_POOL_HEADER] === '1' && !isDirect(url);
  delete req.headers[FORCE_POOL_HEADER];
  if (isDirect(url)) {
    try {
      const u = new URL(url);
      const opts = {host: u.hostname, port: u.port || 80, method: req.method, path: u.pathname + u.search, headers: req.headers};
      const pr = http.request(opts, prs=>{res.writeHead(prs.statusCode, prs.headers); prs.pipe(res);});
      pr.on('error',e=>{res.writeHead(502); res.end(e.message);});
      req.pipe(pr);
      return;
    } catch {}
  }
  const p=useEgress();
  if(!p){ res.writeHead(502); res.end('no pool'); return; }
  console.log(`[forward] ${req.method} ${req.url.slice(0,60)} via ${p.host}`);
  const opts={
    host:p.host,
    port:p.port,
    method:req.method,
    path:req.url,
    headers:{...req.headers, 'Proxy-Authorization':'Basic '+Buffer.from(`${p.user}:${p.pass}`).toString('base64')}
  };
  delete opts.headers['proxy-authorization'];
  delete opts.headers[FORCE_POOL_HEADER];
  opts.headers['Proxy-Authorization']='Basic '+Buffer.from(`${p.user}:${p.pass}`).toString('base64');
  const pr=http.request(opts, prs=>{
    res.writeHead(prs.statusCode, prs.headers);
    prs.pipe(res);
  });
  pr.on('error',e=>{ console.log('[forward] err',e.message); res.writeHead(502); res.end(e.message); });
  req.pipe(pr);
});

server.on('connect', (req, clientSocket, head)=>{
  const url = req.url || "";
  delete req.headers[FORCE_POOL_HEADER];
  if (isDirect(url)) {
    const [host, port] = url.split(":");
    const srv = net.connect(parseInt(port) || 443, host, ()=>{
      clientSocket.write('HTTP/1.1 200 Connection Established\r\n\r\n');
      if (head && head.length) srv.write(head);
      srv.pipe(clientSocket); clientSocket.pipe(srv);
    });
    srv.on('error',()=>clientSocket.end());
    clientSocket.on('error',()=>srv.end());
    return;
  }
  const p=useEgress();
  if(!p){ clientSocket.end('HTTP/1.1 502 no pool\r\n\r\n'); return; }
  console.log(`[forward] CONNECT ${req.url} via ${p.host}`);
  const srvSocket=net.connect(p.port, p.host, ()=>{
    const auth=Buffer.from(`${p.user}:${p.pass}`).toString('base64');
    srvSocket.write(`CONNECT ${req.url} HTTP/1.1\r\nHost: ${req.url}\r\nProxy-Authorization: Basic ${auth}\r\nConnection: keep-alive\r\n\r\n`);
    srvSocket.write(head);
    srvSocket.pipe(clientSocket);
    clientSocket.pipe(srvSocket);
  });
  srvSocket.on('error',e=>{ console.log('[forward] CONNECT err',e.message); clientSocket.end(); });
  clientSocket.on('error',()=>srvSocket.end());
  srvSocket.on('close',()=>clientSocket.end());
  clientSocket.on('close',()=>srvSocket.end());
});

server.on('error',e=>console.log('[forward] server err',e));
server.listen(PORT,'0.0.0.0',()=>console.log(`[forward] listening 0.0.0.0:${PORT} (compose-internal only)`));

// --- OpenCode-client attestation shim (zen path, :3129) ---
// omp source: packages/ai/src/providers/inference-headers.ts
// applyInferenceHeaders stamps, for provider opencode-go/opencode-zen:
//   User-Agent: omp/<VERSION> (omp sets-if-absent; OVERWRITTEN here — the
//     daemon's own UA would otherwise arrive as non-omp and gateway 403s)
//   x-opencode-session: <session UUID> (authoritative overwrite, mirroring
//     omp's setHeader overwrite semantics)
// The qwen daemon points OPENAI_BASE_URL at this listener (see qwen/.env);
// it stamps both headers and chains through the rotating forward proxy
// above (127.0.0.1:3128, FORCE_POOL_HEADER) to the host zen gateway, so
// stamped inference egress rotates. No timeout: inference SSE streams pause
// during reasoning.
// Session value = host install-id (~/.omp/install-id): persistent, never
// expires, so no re-mint hook is needed. Wired via OPENCODE_SESSION in
// qwen/.env (same secrecy as QWEN_SERVER_TOKEN), exported as ATTEST_SESSION
// by entrypoint.sh. Empty/missing → ephemeral randomUUID fallback (gateway
// accepts any UUID for inference; omp itself mints random v4 per turn when
// the caller omits it — see opencode-session-header.test.ts).
const ATTEST_PORT = 3129;
const ATTEST_UA = process.env.ATTEST_UA || 'omp/18.2.6';
const ATTEST_UPSTREAM_HOST = process.env.ATTEST_UPSTREAM_HOST || 'host.docker.internal';
const ATTEST_UPSTREAM_PORT = parseInt(process.env.ATTEST_UPSTREAM_PORT || '18898', 10);
let attestSession = (process.env.ATTEST_SESSION || '').trim();
if (!attestSession) {
  attestSession = crypto.randomUUID();
  console.log('[attest] WARNING: ATTEST_SESSION empty — using ephemeral fallback');
} else {
  console.log(`[attest] session ${attestSession.slice(0,8)} ua=${ATTEST_UA}`);
}
const attest = http.createServer((req, res) => {
  const headers = { ...req.headers };
  for (const k of Object.keys(headers)) {
    const lk = k.toLowerCase();
    if (lk === 'proxy-authorization' || lk === 'proxy-connection' || lk === 'connection' || lk === 'host') delete headers[k];
  }
  headers['User-Agent'] = ATTEST_UA;
  headers['x-opencode-session'] = attestSession;
  headers['host'] = `${ATTEST_UPSTREAM_HOST}:${ATTEST_UPSTREAM_PORT}`;
  // Chain through the rotating forward proxy (:3128) with forced pool
  // egress so stamped inference calls rotate IPs like everything else.
  // Absolute-form path = forward-proxy request; FORCE_POOL_HEADER survives
  // isDirect (host.docker.internal) and is stripped before upstream.
  headers[FORCE_POOL_HEADER] = '1';
  const up = http.request(
    { host: '127.0.0.1', port: PORT, method: req.method, path: `http://${ATTEST_UPSTREAM_HOST}:${ATTEST_UPSTREAM_PORT}${req.url}`, headers, timeout: 0 },
    urs => {
      const out = { ...urs.headers };
      delete out['content-length'];
      res.writeHead(urs.statusCode, out);
      urs.pipe(res);
    }
  );
  up.on('error', e => { console.log('[attest] upstream err', e.message); if (!res.headersSent) res.writeHead(502); res.end('attest upstream error'); });
  req.pipe(up);
});
attest.on('error', e => console.log('[attest] server err', e.message));
attest.listen(ATTEST_PORT, '127.0.0.1', () => console.log(`[attest] listening 127.0.0.1:${ATTEST_PORT} -> ${ATTEST_UPSTREAM_HOST}:${ATTEST_UPSTREAM_PORT}`));
