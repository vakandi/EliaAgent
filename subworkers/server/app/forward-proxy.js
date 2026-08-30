import http from 'http';
import net from 'net';
import fs from 'fs';

const PORT = 3128;
const POOL_PATH = '/data/proxies.txt';
let pool = [];
let rr = 0;

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

function nextProxy(){
  if(!pool.length) return null;
  const p=pool[rr % pool.length];
  rr++;
  return p;
}

const server=http.createServer((req,res)=>{
  const p=nextProxy();
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
  opts.headers['Proxy-Authorization']='Basic '+Buffer.from(`${p.user}:${p.pass}`).toString('base64');
  const pr=http.request(opts, prs=>{
    res.writeHead(prs.statusCode, prs.headers);
    prs.pipe(res);
  });
  pr.on('error',e=>{ console.log('[forward] err',e.message); res.writeHead(502); res.end(e.message); });
  req.pipe(pr);
});

server.on('connect', (req, clientSocket, head)=>{
  const p=nextProxy();
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
server.listen(PORT,'127.0.0.1',()=>console.log(`[forward] listening 127.0.0.1:${PORT}`));
