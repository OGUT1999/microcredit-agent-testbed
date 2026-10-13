/** Deterministic EVM fixture only; NOT an LLM run or independent agent consent. */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const sha=x=>createHash('sha256').update(x).digest('hex');
const hex=x=>'0x'+sha(x);
const RUN='real-agents-20261013-seven-days-v1';
export function fixtureDay(day,evidence,timestamp){
 const manifest=JSON.parse(fs.readFileSync(path.join(evidence,'manifest.json')));
 if(manifest.rehearsal!==true)throw Error('Fixture forbidden outside fork evidence');
 const actor=id=>{const a=manifest.roster.find(a=>a.id===id);if(!a)throw Error('Fixture actor missing');return a;};
 const jobs=[1,2].map(i=>({acceptedJobId:`fixture-job-${i}`,workerId:`worker-0${i}`,clientId:`client-0${i}`,wageMicro:'200000',netWageMicro:'190000',guaranteeMicro:'100000',clientIdHash:hex(`fixture-client-${i}`),groupIdHash:'0x'+'0'.repeat(64),paymentDueVirtualDay:i===1?3:5,virtualDueTermsAccepted:true,withholdingAuthorized:true,termsHash:hex(JSON.stringify({fixture:true,job:i,wage:'200000',net:'190000',G:'100000',paymentDueVirtualDay:i===1?3:5}))}));
 const actions=[],records=[];
 function add(actorId,action,args,evidence={},job){
  const normalized={runId:RUN,intentId:`fixture-day-${day}-action-${String(actions.length+1).padStart(2,'0')}`,day,actorId,action,args};
  function record(id){const r={actorId:id,day,coordinatorApproved:true,actionPayload:normalized,transcript:{actorId:id,day,fixture:true,source:'deterministic-EVM-fixture',prompt:'Deterministic fixture validates the exact action; no model was invoked.',response:JSON.stringify({acceptedActionPayload:normalized,fixture:true}),acceptedActionPayload:normalized},...(job?{acceptedJob:job}:{}),...(action==='claim'?{nonpaymentDecision:{acceptedJobId:job.acceptedJobId,clientId:job.clientId,deliveredTextHash:evidence.deliveredTextHash,nonpaymentReviewHash:evidence.nonpaymentReviewHash}}:{})};const recordHash=sha(JSON.stringify(r));records.push({recordHash,record:r});return recordHash;}
  const consent={actorId,payloadHash:sha(JSON.stringify(normalized)),recordHash:record(actorId)};
  if(action==='open'){evidence={...evidence,issuerConsentHash:record('issuer-01'),clientConsentHash:record(job.clientId)};}
  if(action==='attest')evidence={...evidence,workerConsentHash:record(args[0])};
  actions.push({...normalized,consent,evidence});
 }
 function open(job){const acceptance={worker:actor(job.workerId).address,clientId:job.clientIdHash,groupId:job.groupIdHash,amount:job.guaranteeMicro,maxFromDues:'0',termsHash:job.termsHash,contributionBps:'500',contributionCap:'3000000',remitWindow:'1209600',settleBy:String(timestamp+86400+600),holdUntil:String(timestamp+172800),nonce:'1',deadline:String(timestamp+3600)};add(job.workerId,'open',[acceptance],{clientId:job.clientId,acceptedJobId:job.acceptedJobId},job);}
 if(day===1){add('sponsor-01','fund-reserve',['500000']);add('backer-01','stake',['300000']);for(const id of ['worker-01','worker-02']){add(id,'consent',['backer-01',true]);add('backer-01','attest',[id,'100000']);}}
 if(day===2)open(jobs[0]);
 if(day===3){open(jobs[1]);add('client-01','pay',['worker-01','190000'],{acceptedJobId:jobs[0].acceptedJobId,deliveredTextHash:hex('fixture-first-delivery'),clientReviewHash:hex('fixture-first-review')},jobs[0]);}
 if(day===4){const rows=fs.readFileSync(path.join(evidence,'journal.jsonl'),'utf8').trim().split('\n').map(x=>JSON.parse(x));const pay=rows.find(x=>x.kind==='market-action-result'&&x.day===3&&x.action==='pay');if(!pay)throw Error('Fixture requires actual prior payment receipt');add('adjudicator-01','mark-paid',['0','200000',hex('fixture-paid-evidence')],{verifiedPaymentHash:pay.hash,clientId:'client-01',workerId:'worker-01',paymentAmountMicro:'190000',deliveredTextHash:hex('fixture-first-delivery'),clientReviewHash:hex('fixture-first-review')},jobs[0]);add('client-01','remit',['0'],{},jobs[0]);}
 if(day===5)add('adjudicator-01','claim',['1',hex('fixture-nonpayment-evidence')],{deliveredTextHash:hex('fixture-second-delivery'),nonpaymentReviewHash:hex('fixture-second-reviewed-nonpayment')},jobs[1]);
 if(day===7)add('issuer-01','pause',[true]);
 const packet={schema:'real-agents-day/1',runId:RUN,day,actions};
 return {packet,consentRecords:{runId:RUN,day,packetSha256:sha(JSON.stringify(packet)),records},fixture:true,modelInvocations:0};
}
if(process.argv.includes('--self-test')&&process.argv[1]?.endsWith('fixture-builder.mjs')){
 const {default:assert}=await import('node:assert/strict');const {default:os}=await import('node:os');
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'fixture-shape-'));
 try{
  fs.writeFileSync(path.join(temp,'manifest.json'),JSON.stringify({rehearsal:true,roster:[{id:'worker-01',address:'0x0000000000000000000000000000000000000011'},{id:'worker-02',address:'0x0000000000000000000000000000000000000012'}]}));
  fs.writeFileSync(path.join(temp,'journal.jsonl'),JSON.stringify({kind:'market-action-result',day:3,action:'pay',hash:'0x'+'1'.repeat(64)})+'\n');
  const days=Array.from({length:7},(_,i)=>fixtureDay(i+1,temp,2000000000));
  assert.deepEqual(days.map(x=>x.packet.actions.length),[6,1,2,2,1,0,1]);
  for(const d of days){assert.equal(d.consentRecords.packetSha256,sha(JSON.stringify(d.packet)));for(const r of d.consentRecords.records){assert.equal(r.recordHash,sha(JSON.stringify(r.record)));assert.deepEqual(JSON.parse(r.record.transcript.response).acceptedActionPayload,r.record.actionPayload);assert.equal(r.record.transcript.fixture,true);}}
  assert.equal(days[4].packet.actions[0].action,'claim');assert.equal(days[6].packet.actions[0].action,'pause');
  fs.writeFileSync(path.join(temp,'manifest.json'),JSON.stringify({rehearsal:false,roster:[]}));assert.throws(()=>fixtureDay(1,temp,2000000000));
  console.log(JSON.stringify({fixtureShape:'passed',sevenDays:true,modelInvocations:0,EVMExecuted:false}));
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
}
