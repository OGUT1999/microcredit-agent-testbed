/** Disabled-workflow adapter; no keys or signed payloads are accepted in comments. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {gunzipSync,gzipSync} from 'node:zlib';
import {fixtureDay} from './fixture-builder.mjs';
const RUN='real-agents-20261013-seven-days-v1';
const MARKER='GUARANTEE_TRUST_REAL_AGENTS_V1';
const ARTIFACT='9589450dbe08cbf1907fd68e8dc82c341346163b7d19da9a4052f248e60c5612';
const BASE='experiments/guarantee-trust-real-agents-seven-days';
const sha=x=>createHash('sha256').update(x).digest('hex');
function safeJSON(value){const bytes=JSON.stringify(value);if(bytes.length>240000||/0x[0-9a-fA-F]{67,}|(?:private[_ -]?key|seed phrase|raw[_ -]?signed|session[_ -]?id|chatgpt\.com\/c\/|gh[pousr]_[a-zA-Z0-9]{20,})/i.test(bytes)||/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(bytes))throw Error('Unsafe public packet');return bytes;}
export function validateEvent(event,issue,head,executorHash){
 if(!Number.isSafeInteger(issue)||issue<1||event.action!=='created'||event.sender?.login!=='scottonchain'||event.comment?.user?.login!=='scottonchain'||event.issue?.number!==issue||event.issue.pull_request)throw Error('Trusted dedicated control issue required');
 const body=event.comment.body;if(typeof body!=='string'||!body.startsWith(MARKER+'\n')||Buffer.byteLength(body,'utf8')>64000)throw Error('Exact command marker required');
 let request=JSON.parse(body.slice(MARKER.length+1));
 if(request.encoding!==undefined){
  if(Object.keys(request).sort().join(',')!=='decodedBytes,decodedSha256,encoding,payloadBase64'||request.encoding!=='gzip-base64'||!Number.isInteger(request.decodedBytes)||request.decodedBytes<1||request.decodedBytes>240000||!/^([a-f0-9]{64})$/.test(request.decodedSha256)||typeof request.payloadBase64!=='string'||!/^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(request.payloadBase64))throw Error('Invalid compressed envelope');
  const compressed=Buffer.from(request.payloadBase64,'base64');if(compressed.toString('base64')!==request.payloadBase64)throw Error('Noncanonical base64');
  const decoded=gunzipSync(compressed,{maxOutputLength:240000});
  if(decoded.length!==request.decodedBytes||sha(decoded)!==request.decodedSha256)throw Error('Compressed payload hash/size mismatch');
  request=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(decoded));
 }
 const allowed=new Set(['command','runId','chainId','reviewedCodeCommit','executorSha256','artifactSha256','day','packet','consentRecords','days','fixture']);
 if(Object.keys(request).some(k=>!allowed.has(k))||request.runId!==RUN||request.chainId!==84532||request.reviewedCodeCommit!==head||!/^([a-f0-9]{40})$/.test(head)||request.executorSha256!==executorHash||request.artifactSha256!==ARTIFACT||!['bootstrap','fork_rehearsal','market-day'].includes(request.command))throw Error('Reviewed exact code/run/command binding required');
 if(request.fixture!==undefined&&(request.command!=='fork_rehearsal'||request.fixture!=='settlement-v1'||request.days!==undefined))throw Error('Deterministic fixture allowed only in localhost rehearsal');
 safeJSON(request);
 if(request.command==='market-day')validateDay(request.packet,request.consentRecords,request.day);
 if(request.command==='fork_rehearsal'&&request.days!==undefined){if(!Array.isArray(request.days)||request.days.length>7)throw Error('Bounded rehearsal days required');request.days.forEach((d,i)=>validateDay(d.packet,d.consentRecords,i+1));}
 return request;
}
function validateDay(packet,records,day){
 if(!Number.isInteger(day)||day<1||day>7||packet?.schema!=='real-agents-day/1'||packet.runId!==RUN||packet.day!==day||!Array.isArray(packet.actions)||packet.actions.length>80||records?.runId!==RUN||records.day!==day||records.packetSha256!==sha(JSON.stringify(packet))||!Array.isArray(records.records))throw Error('Day/consent packet mismatch');
 safeJSON(packet);safeJSON(records);
}
function redacted(value){if(Array.isArray(value))return value.map(redacted);if(value&&typeof value==='object'){const o={};for(const[k,v]of Object.entries(value)){if(k==='data'&&Array.isArray(value.topics)&&typeof value.address==='string')o.dataSha256=sha(v);else o[k]=redacted(v);}return o;}return value;}
function git(args){const r=spawnSync('git',args,{encoding:'utf8',stdio:['ignore','pipe','pipe']});if(r.status!==0)throw Error('Git operation failed');return r.stdout.trim();}
async function child(args,env){return await new Promise((resolve,reject)=>{const p=spawn(process.execPath,args,{env:{...process.env,...env},stdio:['ignore','ignore','ignore']});p.on('error',()=>reject(Error('Controlled child failed')));p.on('close',code=>code===0?resolve():reject(Error('Controlled executor halted; inspect redacted evidence')));});}
async function main(){
 const self=fs.readFileSync(`${BASE}/executor.mjs`),head=git(['rev-parse','HEAD']);
 const event=JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH));
 const request=validateEvent(event,Number(process.env.CONTROL_ISSUE_NUMBER),head,sha(self));
 if(process.env.GITHUB_REPOSITORY!=='scottonchain/microcredit-agent-testbed')throw Error('Repository binding mismatch');
 const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'real-agent-reviewed-'));let anvil;
 const rehearsal=request.command==='fork_rehearsal';
 const evidence=rehearsal?`${BASE}/evidence/rehearsals/${RUN}/${head}`:`${BASE}/evidence/${RUN}`;
 const env={RUN_ID:RUN,REVIEWED_ARTIFACT_SHA256:ARTIFACT,REVIEWED_SOURCE_PATH:'reviewed-contract/packages/foundry/contracts/GuaranteeTrust.sol',EVIDENCE_DIR:path.resolve(evidence),REHEARSAL:rehearsal?'1':'0',RPC_URL:rehearsal?'http://127.0.0.1:18545':'https://base-sepolia-rpc.publicnode.com'};

 if(!rehearsal&&request.command==='market-day'){
  const checkpoint=JSON.parse(fs.readFileSync(path.join(evidence,'checkpoint.json')));
  if(checkpoint.runId!==RUN||checkpoint.phase!=='bootstrap-only-complete'||(checkpoint.marketDay||0)!==request.day-1)throw Error('Prior committed exact run evidence required; no fresh bootstrap fallback');
  // Only files from the checkout may establish prior state, not new uncommitted caller writes.
  git(['ls-files','--error-unmatch',path.join(evidence,'checkpoint.json'),path.join(evidence,'deployment.json')]);
 }
 let status='failed';
 try{
  if(rehearsal){
   const binary=path.resolve('node_modules/@foundry-rs/anvil-linux-amd64/bin/anvil');
   anvil=spawn(binary,['--silent','--host','127.0.0.1','--port','18545','--chain-id','84532','--fork-url','https://base-sepolia-rpc.publicnode.com'],{stdio:'ignore'});
   await new Promise((resolve,reject)=>{let attempts=0;const timer=setInterval(async()=>{try{const r=await fetch('http://127.0.0.1:18545',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'eth_chainId',params:[]}),signal:AbortSignal.timeout(1000)});if((await r.json()).result==='0x14a34'){clearInterval(timer);resolve();}}catch{}if(++attempts>=30){clearInterval(timer);reject(Error('Local fork did not start'));}},1000);anvil.once('error',()=>{clearInterval(timer);reject(Error('Local fork failed'));});});
  }
  if(request.command!=='market-day')await child([`${BASE}/executor.mjs`],env);
  const days=request.command==='market-day'?[{packet:request.packet,consentRecords:request.consentRecords}]:(request.days||[]);
  const iterations=request.fixture==='settlement-v1'?Array.from({length:7},(_,i)=>({fixtureDay:i+1})):days;
  for(let d of iterations){
   if(d.fixtureDay){const blockResponse=await fetch('http://127.0.0.1:18545',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'eth_getBlockByNumber',params:['latest',false]}),signal:AbortSignal.timeout(3000)});const block=(await blockResponse.json()).result;if(!block?.timestamp)throw Error('Local fixture block unavailable');d=fixtureDay(d.fixtureDay,evidence,Number(BigInt(block.timestamp)));}
const packet=path.join(scratch,'packet.json'),records=path.join(scratch,'records.json');fs.writeFileSync(packet,JSON.stringify(d.packet),{mode:0o600});fs.writeFileSync(records,JSON.stringify(d.consentRecords),{mode:0o600});fs.writeFileSync(path.join(evidence,`day-${d.packet.day}-approved-packet.json`),safeJSON(d.packet)+'\n');fs.writeFileSync(path.join(evidence,`day-${d.packet.day}-consent-records.json`),safeJSON(d.consentRecords)+'\n');await child([`${BASE}/executor.mjs`,'--market'],{...env,APPROVED_ACTION_PACKET:packet,APPROVED_CONSENT_RECORDS:records});}
  status='completed-request';
 }finally{
  if(anvil)anvil.kill('SIGTERM');fs.rmSync(scratch,{recursive:true,force:true});
  fs.mkdirSync(evidence,{recursive:true});
  fs.writeFileSync(path.join(evidence,`request-${event.comment.id}.json`),JSON.stringify({schema:'real-agent-launch-receipt/1',commentId:event.comment.id,controlIssue:event.issue.number,requestSha256:sha(safeJSON(request)),reviewedCodeCommit:head,executorSha256:sha(self),runId:RUN,command:request.command,virtualDay:request.day||null,rehearsal,fixture:request.fixture||null,modelInvocations:request.fixture?0:null,status,note:'Request completion is not a seven-day experiment success or human impact claim'},null,2)+'\n');
  // Evidence only. No world-model, protected state, commentary, keys or signed payloads.
  for(const file of fs.readdirSync(evidence)){const p=path.join(evidence,file);if(!fs.statSync(p).isFile())continue;if(file.endsWith('.jsonl')){const rows=fs.readFileSync(p,'utf8').trim().split('\n').filter(Boolean).map(x=>redacted(JSON.parse(x)));for(const row of rows)safeJSON(row);fs.writeFileSync(p,rows.map(x=>JSON.stringify(x)).join('\n')+'\n');}else{const v=redacted(JSON.parse(fs.readFileSync(p,'utf8')));safeJSON(v);fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');}}
  git(['config','user.name','github-actions[bot]']);git(['config','user.email','41898282+github-actions[bot]@users.noreply.github.com']);
  git(['add','--',evidence]);const changes=git(['diff','--cached','--name-only']);
  if(changes&&changes.split('\n').every(p=>p.startsWith(evidence+'/'))){git(['commit','-m',`Record reviewed real-agent ${request.command} request`]);git(['push','origin','HEAD:main']);}
 }
 if(status!=='completed-request')throw Error('Request failed; preserve receipt, do not claim completion');
}
if(process.argv.includes('--self-test')){
 const h='a'.repeat(40),x='b'.repeat(64),r={command:'bootstrap',runId:RUN,chainId:84532,reviewedCodeCommit:h,executorSha256:x,artifactSha256:ARTIFACT};
 const e={action:'created',sender:{login:'scottonchain'},comment:{user:{login:'scottonchain'},body:MARKER+'\n'+JSON.stringify(r)},issue:{number:123}};
 assert.equal(validateEvent(e,123,h,x).command,'bootstrap');assert.throws(()=>validateEvent({...e,sender:{login:'intruder'}},123,h,x));assert.throws(()=>validateEvent(e,0,h,x));assert.throws(()=>validateEvent(e,123,'c'.repeat(40),x));assert.throws(()=>validateEvent({...e,comment:{...e.comment,body:MARKER+'\n'+JSON.stringify({...r,chainId:1})}},123,h,x));assert.throws(()=>safeJSON({key:'0x'+'a'.repeat(128)}));const bytes=Buffer.from(JSON.stringify(r));const packed={encoding:'gzip-base64',decodedBytes:bytes.length,decodedSha256:sha(bytes),payloadBase64:gzipSync(bytes).toString('base64')};
 const packedEvent={...e,comment:{...e.comment,body:MARKER+'\n'+JSON.stringify(packed)}};assert.equal(validateEvent(packedEvent,123,h,x).command,'bootstrap');
 assert.throws(()=>validateEvent({...packedEvent,comment:{...packedEvent.comment,body:MARKER+'\n'+JSON.stringify({...packed,decodedSha256:'0'.repeat(64)})}},123,h,x));
 assert.throws(()=>validateEvent({...packedEvent,comment:{...packedEvent.comment,body:MARKER+'\n'+JSON.stringify({...packed,extra:true})}},123,h,x));
 assert.throws(()=>validateEvent({...e,comment:{...e.comment,body:MARKER+'\n'+' '.repeat(64001)}},123,h,x));
 console.log(JSON.stringify({launcherOfflineChecks:10,passed:true}));
}else{main().catch(()=>{console.error('Reviewed launcher halted; sensitive failure details suppressed. Inspect preserved redacted receipts.');process.exitCode=1;});}
