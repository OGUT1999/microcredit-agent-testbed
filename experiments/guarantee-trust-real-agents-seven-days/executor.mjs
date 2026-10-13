/** Bootstrap-only controlled executor. Never prints keys or signed payloads. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
import {createHash,createHmac} from 'node:crypto';
import {Wallet,JsonRpcProvider,Contract,ContractFactory,Transaction,verifyTypedData,keccak256,getAddress,parseEther,Interface,version} from 'ethers';
const TOKEN=getAddress('0x036CbD53842c5426634e7929541eC2318f3dCF7e');
const ROOT=getAddress('0x38e9845A1Df22c59Bfc693bf2CEAa3361158d6d1');
const SOURCE='ec93c76779b5e2d52ab7b87cf82b3fd400205969';
const roles=[['client',40,800000n],['worker',40,0n],['backer',14,300000n],['sponsor',4,500000n]];
const sha=x=>createHash('sha256').update(x).digest('hex');
const serial=x=>JSON.stringify(x,(_,v)=>typeof v==='bigint'?v.toString():v,2)+'\n';
const validation={schema:'real-agents-executor/1',chainId:84532,token:TOKEN,root:ROOT,sourceCommit:SOURCE,sourceGitBlob:'98630ab1d9273e01772b7be484c7fdec97795946',roles:Object.fromEntries(roles.map(([r,n])=>[r,n])),virtualDays:7,bootstrapTokenTotal:'38.2',maxTokenSpend:'40',maxFeesETH:'0.005',maxGasFundingETH:'0.002',implemented:['fresh-contract','character-token-funding','receipt-verification','balance-snapshot','review-gated-market-packets'],unsupported:['automatic-market-resume','automatic-settlement-shutdown'],marketReady:false};
if(version!=='6.15.0')throw Error('ethers version mismatch');
function validateConsentRecord(entry,actorId,day,normalized){
 if(!entry||!entry.record||sha(JSON.stringify(entry.record))!==entry.recordHash)throw Error('Consent record content/hash missing');
 const record=entry.record;
 if(typeof record.transcript?.prompt!=='string'||typeof record.transcript?.response!=='string')throw Error('Original prompt and model response required');
 let response;try{response=JSON.parse(record.transcript.response);}catch{throw Error('Original model response must parse as JSON');}
 if(JSON.stringify(response.acceptedActionPayload)!==JSON.stringify(normalized))throw Error('Original model response lacks exact action acceptance');
 if(record.actorId!==actorId||record.day!==day||record.coordinatorApproved!==true||!record.transcript||record.transcript.actorId!==actorId||record.transcript.day!==day||JSON.stringify(record.actionPayload)!==JSON.stringify(normalized)||JSON.stringify(record.transcript.acceptedActionPayload)!==JSON.stringify(normalized))throw Error('Transcript actor/day/exact payload approval mismatch');
 return record;
}
function verifyUnusedActor(state){if(state.nonce!==0||state.tokenBalance!==0n)throw Error('Run-derived actor already used or funded: reconcile existing run, never redeploy');}
if(process.argv.includes('--self-test')){
 const normalized={runId:'real-agents-offline-test',intentId:'test-consent-001',day:1,actorId:'worker-01',action:'consent',args:['backer-01',true]};
 const record={actorId:'worker-01',day:1,coordinatorApproved:true,actionPayload:normalized,transcript:{actorId:'worker-01',day:1,prompt:'Accept or refuse the exact bounded action',response:JSON.stringify({acceptedActionPayload:normalized}),acceptedActionPayload:normalized}};
 const entry={recordHash:sha(JSON.stringify(record)),record};
 assert.equal(validateConsentRecord(entry,'worker-01',1,normalized),record);
 assert.throws(()=>validateConsentRecord(entry,'worker-02',1,normalized));
 assert.throws(()=>validateConsentRecord(entry,'worker-01',2,normalized));
 assert.throws(()=>validateConsentRecord(entry,'worker-01',1,{...normalized,args:['backer-01',false]}));
 assert.throws(()=>validateConsentRecord({recordHash:entry.recordHash,record:{...record,coordinatorApproved:false}},'worker-01',1,normalized));
 const signer=Wallet.createRandom();
 const domain={name:'GuaranteeTrust',version:'2',chainId:84532,verifyingContract:'0x0000000000000000000000000000000000000001'};
 const types={Consent:[['member','address'],['attester','address'],['allowed','bool'],['nonce','uint256'],['deadline','uint256']].map(([name,type])=>({name,type}))};
 const values={member:signer.address,attester:ROOT,allowed:true,nonce:0,deadline:2000000000};
 const signature=await signer.signTypedData(domain,types,values);
 assert.equal(verifyTypedData(domain,types,values,signature),signer.address);
 assert.notEqual(verifyTypedData({...domain,version:'1'},types,values,signature),signer.address);
 assert.notEqual(verifyTypedData({...domain,chainId:1},types,values,signature),signer.address);
 assert.notEqual(verifyTypedData(domain,types,{...values,allowed:false},signature),signer.address);
 verifyUnusedActor({nonce:0,tokenBalance:0n});
 assert.throws(()=>verifyUnusedActor({nonce:1,tokenBalance:0n}));
 assert.throws(()=>verifyUnusedActor({nonce:0,tokenBalance:1n}));
 console.log(JSON.stringify({offlineValidation:'passed',checks:12,liveTransactions:0}));process.exit(0);
}
if(process.argv.includes('--validate')){console.log(serial(validation));process.exit(0);}
const MARKET=process.argv.includes('--market');
const runId=process.env.RUN_ID;
if(!runId||!/^real-agents-[a-z0-9-]{8,80}$/.test(runId))throw Error('Explicit unique run ID required');
const out=path.resolve(process.env.EVIDENCE_DIR||'real-agents-evidence');
if(!MARKET&&fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('Existing evidence: no replay or automatic resume permitted');
const artifactBytes=fs.readFileSync(process.env.ARTIFACT_PATH||'experiments/guarantee-trust-circle-coldstart/artifact.json');
const artifact=JSON.parse(artifactBytes), bytecode=typeof artifact.bytecode==='string'?artifact.bytecode:artifact.bytecode.object;
if(sha(artifactBytes)!==process.env.REVIEWED_ARTIFACT_SHA256)throw Error('Explicit reviewed artifact SHA256 required');
if(artifact.sourceCommit!==SOURCE)throw Error('Artifact source commit mismatch');
const sourceBytes=fs.readFileSync(process.env.REVIEWED_SOURCE_PATH||'packages/foundry/contracts/GuaranteeTrust.sol');
const gitBlobHash=createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${sourceBytes.length}\0`),sourceBytes])).digest('hex');
if(gitBlobHash!=='98630ab1d9273e01772b7be484c7fdec97795946')throw Error('Source Git blob does not match pinned reviewed commit');
if(artifact.sourceHashes?.['contracts/GuaranteeTrust.sol']!==keccak256(sourceBytes))throw Error('Compiler input source hash mismatch: rebuild or resolve provenance before execution');
const provider=new JsonRpcProvider(process.env.RPC_URL||'https://sepolia.base.org');
async function read(fn){let last;for(let i=0;i<3;i++){try{return await fn();}catch(e){last=e;await new Promise(r=>setTimeout(r,1000*(i+1)));}}throw Error('RPC read failed after bounded retries');}
if((await read(()=>provider.getNetwork())).chainId!==84532n)throw Error('Chain mismatch');
const root=new Wallet(process.env.TEST_WALLET_PRIVATE_KEY,provider);
if(root.address!==ROOT)throw Error('Root identity mismatch');
const token=new Contract(TOKEN,['function decimals() view returns(uint8)','function balanceOf(address) view returns(uint256)','function transfer(address,uint256) returns(bool)','event Transfer(address indexed from,address indexed to,uint256 value)'],root);
if(await read(()=>token.decimals())!==6n||await read(()=>provider.getCode(TOKEN))==='0x')throw Error('Token identity mismatch');
fs.mkdirSync(out,{recursive:true,mode:0o700});
const write=(name,value)=>{let p=path.join(out,name);fs.writeFileSync(p+'.tmp',serial(value),{mode:0o600});fs.renameSync(p+'.tmp',p);};
const append=value=>fs.appendFileSync(path.join(out,'journal.jsonl'),serial(value).replace(/\n\s*/g,'')+'\n',{mode:0o600});
const actors=roles.flatMap(([role,n,amount])=>Array.from({length:n},(_,i)=>{const id=`${role}-${String(i+1).padStart(2,'0')}`;let key=createHmac('sha256',Buffer.from(root.privateKey.slice(2),'hex')).update(`guarantee-trust:${runId}:${id}`).digest('hex');let wallet=new Wallet('0x'+key,provider);key=null;return{id,role,amount,address:wallet.address,signer:wallet};}));
if(!MARKET)write('manifest.json',{...validation,runId,artifactSha256:sha(artifactBytes),roster:actors.map(({id,role,address,amount})=>({id,role,address,initialFunding:amount})),issuer:ROOT,adjudicator:ROOT,note:'98 character wallets plus issuer/adjudicator roles sharing root; no agent decisions or market operations executed'});
let feeBound=0n,gasFunding=0n,tokenSpend=0n;
const priorJournalPath=path.join(out,'journal.jsonl');
const usedTransactionIds=new Set(fs.existsSync(priorJournalPath)?fs.readFileSync(priorJournalPath,'utf8').trim().split('\n').filter(Boolean).map(x=>JSON.parse(x)).filter(x=>x.kind==='intent-before-broadcast').map(x=>x.id):[]);
async function send(id,request,expectedTransfer,signer=root){
 const sender=signer.address;
 if(usedTransactionIds.has(id))throw Error('Transaction intent ID already used: no replay permitted');
 const pending=await read(()=>provider.getTransactionCount(sender,'pending')), latest=await read(()=>provider.getTransactionCount(sender,'latest'));
 if(pending!==latest)throw Error('Pending root transaction: reconcile before proceeding');
 const fees=await read(()=>provider.getFeeData());if(!fees.maxFeePerGas||!fees.maxPriorityFeePerGas)throw Error('Missing fee quote');
 const estimate=await read(()=>provider.estimateGas({...request,from:sender})),gasLimit=estimate*120n/100n;
 // Base L1 data fee gets a conservative per-transaction reserve, never counted as zero.
 const unsigned=Transaction.from({...request,nonce:latest,chainId:84532,gasLimit,maxFeePerGas:fees.maxFeePerGas,maxPriorityFeePerGas:fees.maxPriorityFeePerGas,type:2});
 const oracle=new Contract('0x420000000000000000000000000000000000000F',['function getL1FeeUpperBound(uint256) view returns(uint256)'],provider);
 const l1Upper=await read(()=>oracle.getL1FeeUpperBound(BigInt((unsigned.unsignedSerialized.length-2)/2+68)));
 const bound=gasLimit*fees.maxFeePerGas+l1Upper*2n+parseEther('0.00002');
 if(feeBound+bound>parseEther('0.005'))throw Error('Fee budget exhausted before broadcast');
 if(gasFunding+(request.value||0n)>parseEther('0.002'))throw Error('Gas funding cap');
 const balance=await read(()=>provider.getBalance(sender));if(balance<bound+(request.value||0n))throw Error('Insufficient ETH');
 const txRequest={...request,nonce:latest,chainId:84532,gasLimit,maxFeePerGas:fees.maxFeePerGas,maxPriorityFeePerGas:fees.maxPriorityFeePerGas};
 const intent={id,runId,chainId:84532,from:sender,to:request.to||null,calldataSha256:sha(request.data||'0x'),value:request.value||0n,nonce:latest,feeBound:bound,expectedTransfer};
 usedTransactionIds.add(id);append({kind:'intent-before-broadcast',...intent});feeBound+=bound;gasFunding+=request.value||0n;
 // sendTransaction called exactly once. Ambiguous broadcast errors halt; no blind resend.
 let tx;try{tx=await signer.sendTransaction(txRequest);}catch{append({kind:'ambiguous-broadcast',id,nonce:latest});throw Error('Broadcast uncertainty: manual nonce/hash reconciliation required');}
 append({kind:'broadcast',id,hash:tx.hash});
 let receipt;for(let i=0;i<40;i++){receipt=await read(()=>provider.getTransactionReceipt(tx.hash));if(receipt)break;await new Promise(r=>setTimeout(r,1500));}
 if(!receipt)throw Error('Receipt timeout: reconcile hash without resending');
 const chainTx=await read(()=>provider.getTransaction(tx.hash));
 if(receipt.status!==1||receipt.hash!==tx.hash||getAddress(receipt.from)!==sender||chainTx.chainId!==84532n||chainTx.nonce!==latest||chainTx.data!==(request.data||'0x')||chainTx.value!==(request.value||0n)||chainTx.to!==(request.to||null))throw Error('Receipt/transaction identity mismatch');
 if(expectedTransfer){let matched=receipt.logs.some(l=>{if(getAddress(l.address)!==TOKEN)return false;try{let p=token.interface.parseLog(l);return p.name==='Transfer'&&getAddress(p.args.from)===sender&&getAddress(p.args.to)===expectedTransfer.to&&p.args.value===expectedTransfer.amount;}catch{return false;}});if(!matched)throw Error('Expected exact token Transfer log missing');}
 const rawReceipt=await read(()=>provider.send('eth_getTransactionReceipt',[tx.hash]));
 const l1Fee=rawReceipt.l1Fee?BigInt(rawReceipt.l1Fee):null;
 if(l1Fee===null)throw Error('Base L1 receipt fee missing');
 if(receipt.fee+l1Fee>bound)throw Error('Actual fee exceeded preflight upper budget; halt and reconcile');
 append({kind:'verified-receipt',id,hash:tx.hash,status:receipt.status,from:receipt.from,to:receipt.to,blockNumber:receipt.blockNumber,gasUsed:receipt.gasUsed,fee:receipt.fee,l1Fee,totalFee:receipt.fee+l1Fee,logs:receipt.logs.map(l=>({address:l.address,topics:l.topics,data:l.data}))});return receipt;
}
async function snapshot(name,contract){let block=await read(()=>provider.getBlockNumber());write(name,{blockNumber:block,rootETH:await read(()=>provider.getBalance(ROOT,block)),rootUSDC:await read(()=>token.balanceOf(ROOT,{blockTag:block})),balances:await Promise.all(actors.map(async a=>({id:a.id,address:a.address,USDC:await read(()=>token.balanceOf(a.address,{blockTag:block})),ETH:await read(()=>provider.getBalance(a.address,block))}))),contract,feeBound,gasFunding,tokenSpend});}
if(MARKET){await runMarket();process.exit(0);}
for(const a of actors){verifyUnusedActor({nonce:await read(()=>provider.getTransactionCount(a.address,'pending')),tokenBalance:await read(()=>token.balanceOf(a.address))});}
if(await read(()=>token.balanceOf(ROOT))<38200000n)throw Error('Bootstrap needs 38.2 test USDC');
await snapshot('balances-before.json',null);
const factory=new ContractFactory(artifact.abi,bytecode,root);
const deploy=await factory.getDeployTransaction(TOKEN,ROOT,ROOT,ROOT,6000000n,1000000n);
const receipt=await send('fresh-deployment',deploy);
if(!receipt.contractAddress)throw Error('Missing fresh contract address');
const gt=new Contract(receipt.contractAddress,artifact.abi,provider);
for(const [method,value]of [['token',TOKEN],['owner',ROOT],['issuer',ROOT],['adjudicator',ROOT]])if(getAddress(await read(()=>gt[method]()))!==value)throw Error('Contract role identity mismatch');
for(const method of ['reserve','totalStake','outstanding','totalDues','guaranteeCount'])if(await read(()=>gt[method]())!==0n)throw Error('Fresh contract is not empty');
write('deployment.json',{address:receipt.contractAddress,hash:receipt.hash,sourceCommit:SOURCE,artifactSha256:sha(artifactBytes),chainId:84532,token:TOKEN});
for(const a of actors){if(!a.amount)continue;if(tokenSpend+a.amount>40000000n)throw Error('Token budget');const request=await token.transfer.populateTransaction(a.address,a.amount);await send(`fund-${a.id}`,request,{to:a.address,amount:a.amount});tokenSpend+=a.amount;}
await snapshot('balances-after-bootstrap.json',receipt.contractAddress);
write('checkpoint.json',{phase:'bootstrap-only-complete',marketReady:false,runId,contract:receipt.contractAddress,tokenSpend,feeBound,gasFunding,virtualDaysExecuted:0,outstandingGuarantees:0,next:'Review and implement consent-gated market operations before seven-day experiment. No success claim permitted.'});

async function runMarket(){
 const checkpoint=JSON.parse(fs.readFileSync(path.join(out,'checkpoint.json')));
 const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 if(checkpoint.runId!==runId||manifest.artifactSha256!==sha(artifactBytes)||checkpoint.phase!=='bootstrap-only-complete')throw Error('Market requires exact same completed fresh bootstrap');
 feeBound=BigInt(checkpoint.feeBound);gasFunding=BigInt(checkpoint.gasFunding);tokenSpend=BigInt(checkpoint.tokenSpend);
 const deployment=JSON.parse(fs.readFileSync(path.join(out,'deployment.json')));
 const deploymentReceipt=await read(()=>provider.getTransactionReceipt(deployment.hash));
 if(!deploymentReceipt||deploymentReceipt.status!==1||deploymentReceipt.contractAddress!==deployment.address||getAddress(deploymentReceipt.from)!==ROOT)throw Error('Deployment identity mismatch');
 const gt=new Contract(deployment.address,artifact.abi,provider);
 for(const [method,value]of [['token',TOKEN],['owner',ROOT],['issuer',ROOT],['adjudicator',ROOT]])if(getAddress(await read(()=>gt[method]()))!==value)throw Error('Contract binding mismatch');
 const packet=JSON.parse(fs.readFileSync(process.env.APPROVED_ACTION_PACKET));
 if(packet.schema!=='real-agents-day/1'||packet.runId!==runId||!Number.isInteger(packet.day)||packet.day<1||packet.day>7||!Array.isArray(packet.actions)||packet.actions.length>80)throw Error('Bad day packet');
 const previous=checkpoint.marketDay||0;
 if(packet.day!==previous+1)throw Error('Virtual days must run exactly once, sequentially');
 const startMarker=`day-${packet.day}-started.json`;
 if(fs.existsSync(path.join(out,startMarker)))throw Error('Day already started: no automatic replay; reconcile its hashes');
 write(startMarker,{runId,day:packet.day,packetSha256:sha(JSON.stringify(packet)),virtualDaysAreCompressed:true});
 const approvals=JSON.parse(fs.readFileSync(process.env.APPROVED_CONSENT_RECORDS));
 if(approvals.runId!==runId||approvals.day!==packet.day||approvals.packetSha256!==sha(JSON.stringify(packet))||!Array.isArray(approvals.records))throw Error('Coordinator-approved consent file binding absent');
 function authorize(recordHash,actorId,normalized){
  const entry=approvals.records.find(x=>x.recordHash===recordHash);
  return validateConsentRecord(entry,actorId,packet.day,normalized);
 }
 let openedToday=0;
 const seen=new Set();
 const lookup=id=>{if(['issuer','issuer-01','adjudicator','adjudicator-01'].includes(id))return{id,role:id.startsWith('issuer')?'issuer':'adjudicator',address:ROOT,signer:root};let a=actors.find(x=>x.id===id);if(!a)throw Error('Unknown actor');return a;};
 const address=id=>lookup(id).address;
 const integer=v=>{if(typeof v!=='string'||!/^\d{1,20}$/.test(v))throw Error('Exact positive decimal string required');return BigInt(v);};
 const eHash=v=>{if(typeof v!=='string'||!/^0x[0-9a-fA-F]{64}$/.test(v))throw Error('Evidence hash required');return v;};
 async function gas(a){if(a.address===ROOT)return;let balance=await read(()=>provider.getBalance(a.address));if(balance<parseEther('0.000015'))await send(`gas-${packet.day}-${a.id}`,{to:a.address,value:parseEther('0.000025')});}
 async function call(a,id,method,args){await gas(a);let req=await gt.connect(a.signer)[method].populateTransaction(...args);return send(id,req,null,a.signer);}
 async function approve(a,id,amount){await gas(a);const c=new Contract(TOKEN,['function approve(address,uint256) returns(bool)'],a.signer);const req=await c.approve.populateTransaction(deployment.address,amount);return send(id+'-approve',req,null,a.signer);}
 for(const action of packet.actions){
  const {runId:arun,intentId,day,actorId,action:kind,args,consent,evidence}=action;
  if(arun!==runId||day!==packet.day||typeof intentId!=='string'||!/^[a-z0-9-]{8,100}$/.test(intentId)||seen.has(intentId)||!Array.isArray(args))throw Error('Action envelope invalid');seen.add(intentId);
  const normalized={runId,intentId,day,actorId,action:kind,args};
  if(!consent||consent.actorId!==actorId||consent.payloadHash!==sha(JSON.stringify(normalized))||!/^[a-f0-9]{64}$/.test(consent.recordHash||''))throw Error('Exact private consent binding absent');
  const a=lookup(actorId);const consentRecord=authorize(consent.recordHash,actorId,normalized);let receipt;
  // Each private record is an operator-reviewed consent record, not untrusted agent text authority.
  if(kind==='fund-reserve'||kind==='stake'){
   const amount=integer(args[0]);if(args.length!==1||amount===0n||amount>500000n||!(kind==='fund-reserve'?a.role==='sponsor':a.role==='backer'))throw Error('Funding role/amount guard');
   if(await read(()=>token.balanceOf(a.address))<amount)throw Error('Actor funding insufficient');
   await approve(a,intentId,amount);receipt=await call(a,intentId,kind==='stake'?'stake':'fundReserve',[amount]);
  }else if(kind==='consent'){
   if(a.role!=='worker'||args.length!==2||typeof args[1]!=='boolean'||lookup(args[0]).role!=='backer')throw Error('Consent role guard');
   const nonce=await read(()=>gt.consentNonce(a.address,address(args[0])));const block=await read(()=>provider.getBlock('latest'));const deadline=BigInt(block.timestamp)+3600n;
   const fields=[['member','address'],['attester','address'],['allowed','bool'],['nonce','uint256'],['deadline','uint256']].map(([name,type])=>({name,type}));
   const domain={name:'GuaranteeTrust',version:'2',chainId:84532,verifyingContract:deployment.address};
   const values={member:a.address,attester:address(args[0]),allowed:args[1],nonce,deadline};
   const signature=await a.signer.signTypedData(domain,{Consent:fields},values);
   receipt=await call(lookup('issuer'),intentId,'setConsentBySig',[a.address,address(args[0]),args[1],nonce,deadline,signature]);
  }else if(kind==='attest'){
   if(a.role!=='backer'||args.length!==2||lookup(args[0]).role!=='worker'||!evidence?.workerConsentHash)throw Error('Attestation role guard');authorize(evidence.workerConsentHash,args[0],normalized);receipt=await call(a,intentId,'attest',[address(args[0]),integer(args[1])]);
  }else if(kind==='set-line'){
   if(a.role!=='issuer'||args.length!==2||lookup(args[0]).role!=='worker'||integer(args[1])>100000n)throw Error('Issuer line guard');receipt=await call(a,intentId,'setLine',[address(args[0]),integer(args[1])]);
  }else if(kind==='open'){
   if(a.role!=='worker'||args.length!==1||!evidence?.issuerConsentHash||!evidence?.clientConsentHash||!evidence?.clientId||lookup(evidence.clientId).role!=='client')throw Error('Open requires worker, issuer and client exact private consent');
   if(packet.day>4||openedToday>=6)throw Error('New guarantees limited to six/day through day4');
   const issuerRecord=authorize(evidence.issuerConsentHash,'issuer-01',normalized),clientRecord=authorize(evidence.clientConsentHash,evidence.clientId,normalized);
   const acceptance=args[0];
   const job=consentRecord.acceptedJob;
   if(JSON.stringify(job)!==JSON.stringify(clientRecord.acceptedJob)||JSON.stringify(job)!==JSON.stringify(issuerRecord.acceptedJob))throw Error('Worker/client/issuer agreed job differs');
   if(!job||job.workerId!==actorId||job.clientId!==evidence.clientId||job.acceptedJobId!==evidence.acceptedJobId||job.guaranteeMicro!==acceptance.amount||job.termsHash!==acceptance.termsHash||job.clientIdHash!==acceptance.clientId||job.groupIdHash!==acceptance.groupId||!/^\d+$/.test(job.wageMicro||''))throw Error('Acceptance not bound to agreed job/wage/guarantee/terms');
   const fields=[['worker','address'],['clientId','bytes32'],['groupId','bytes32'],['amount','uint256'],['maxFromDues','uint256'],['termsHash','bytes32'],['contributionBps','uint256'],['contributionCap','uint256'],['remitWindow','uint256'],['settleBy','uint64'],['holdUntil','uint64'],['nonce','uint256'],['deadline','uint256']].map(([name,type])=>({name,type}));
   if(!acceptance||Object.keys(acceptance).sort().join(',')!==fields.map(x=>x.name).sort().join(',')||getAddress(acceptance.worker)!==a.address)throw Error('Acceptance schema mismatch');
   for(const f of fields){if(f.type.startsWith('uint'))integer(acceptance[f.name]);if(f.type==='bytes32')eHash(acceptance[f.name]);}
   const block=await read(()=>provider.getBlock('latest')),reserve=await read(()=>gt.reserve()),outstanding=await read(()=>gt.outstanding()),amount=integer(acceptance.amount);
   if(amount===0n||amount>reserve/5n||outstanding+3n*amount>reserve||amount>100000n||integer(acceptance.settleBy)<=BigInt(block.timestamp)||integer(acceptance.holdUntil)<integer(acceptance.settleBy)||integer(acceptance.deadline)<=BigInt(block.timestamp)||integer(acceptance.contributionBps)>500n||integer(acceptance.contributionCap)>3000000n)throw Error('Acceptance bounds or real deadlines invalid');
   if(integer(acceptance.contributionBps)!==await read(()=>gt.contributionBps())||integer(acceptance.contributionCap)!==await read(()=>gt.contributionCap())||integer(acceptance.remitWindow)!==await read(()=>gt.remitWindow()))throw Error('Acceptance must equal live contract contribution policy');
   const signature=await a.signer.signTypedData({name:'GuaranteeTrust',version:'2',chainId:84532,verifyingContract:deployment.address},{Acceptance:fields},acceptance);
   const id=await read(()=>gt.connect(root).openGuarantee.staticCall(acceptance,signature));
   receipt=await call(lookup('issuer'),intentId,'openGuarantee',[acceptance,signature]);
   const opened=await read(()=>gt.guarantee(id));if(getAddress(opened.worker)!==a.address||opened.amount!==amount||opened.termsHash!==acceptance.termsHash)throw Error('Opened guarantee state mismatch');
   openedToday++;write(`job-${id}.json`,{...job,guaranteeId:id,acceptance,openedHash:receipt.hash});
   append({kind:'opened-guarantee-readback',intentId,guaranteeId:id,worker:opened.worker,amount:opened.amount,termsHash:opened.termsHash,receiptHash:receipt.hash});
  }else if(kind==='claim'){
   if(a.role!=='adjudicator'||args.length!==2||!evidence?.deliveredTextHash||!evidence?.nonpaymentReviewHash)throw Error('Claim requires actual delivery and reviewed nonpayment evidence');
   const g=await read(()=>gt.guarantee(integer(args[0]))),block=await read(()=>provider.getBlock('latest'));
   const job=JSON.parse(fs.readFileSync(path.join(out,`job-${args[0]}.json`)));
   if(BigInt(block.timestamp)>(g.disputed?g.holdUntil:g.settleBy))throw Error('Real chain hard settlement deadline passed');
   if(!Number.isInteger(job.paymentDueVirtualDay)||job.paymentDueVirtualDay>packet.day||job.paymentDueVirtualDay<1||job.virtualDueTermsAccepted!==true||!consentRecord.nonpaymentDecision||consentRecord.nonpaymentDecision.acceptedJobId!==job.acceptedJobId||consentRecord.nonpaymentDecision.deliveredTextHash!==evidence.deliveredTextHash||consentRecord.nonpaymentDecision.clientId!==job.clientId||consentRecord.nonpaymentDecision.nonpaymentReviewHash!==evidence.nonpaymentReviewHash)throw Error('Claim lacks adjudicator evidence of mutually accepted compressed payment-due terms');
   receipt=await call(a,intentId,'claim',[integer(args[0]),eHash(args[1])]);
  }else if(kind==='pay'){
   if(a.role!=='client'||args.length!==2||lookup(args[0]).role!=='worker'||!evidence?.deliveredTextHash||!evidence?.clientReviewHash)throw Error('Delivered worker text/client review required');
   const agreedJob=consentRecord.acceptedJob;
   if(!agreedJob||agreedJob.clientId!==actorId||agreedJob.workerId!==args[0]||integer(agreedJob.wageMicro)>800000n||integer(args[1])!==integer(agreedJob.netWageMicro)||agreedJob.withholdingAuthorized!==true)throw Error('Payment actor/gross/net withholding terms mismatch');
   const amount=integer(args[1]);if(!evidence.acceptedJobId||consentRecord.acceptedJob?.acceptedJobId!==evidence.acceptedJobId||consentRecord.acceptedJob?.workerId!==args[0])throw Error('Pay must bind to exact accepted hiring job');if(amount>800000n)throw Error('Payment cap');await gas(a);const req=await token.connect(a.signer).transfer.populateTransaction(address(args[0]),amount);receipt=await send(intentId,req,{to:address(args[0]),amount},a.signer);
  }else if(kind==='mark-paid'){
   if(a.role!=='adjudicator'||args.length!==3||!evidence?.verifiedPaymentHash||!evidence?.deliveredTextHash||!evidence?.clientReviewHash)throw Error('Adjudicator paid evidence missing');
   const paymentBindingFile=path.join(out,`payment-${evidence.verifiedPaymentHash}.json`);
   if(!/^0x[0-9a-fA-F]{64}$/.test(evidence.verifiedPaymentHash))throw Error('Malformed payment hash');
   if(fs.existsSync(paymentBindingFile)){const binding=JSON.parse(fs.readFileSync(paymentBindingFile));if(binding.guaranteeId!==args[0])throw Error('Payment receipt already bound to another guarantee');throw Error('Payment already reserved; reconcile rather than replay');}
   const wageReceipt=await read(()=>provider.getTransactionReceipt(evidence.verifiedPaymentHash));if(!wageReceipt||wageReceipt.status!==1)throw Error('Payment receipt absent');
   const g=await read(()=>gt.guarantee(integer(args[0])));
   const job=JSON.parse(fs.readFileSync(path.join(out,`job-${args[0]}.json`)));
   if(job.clientId!==evidence.clientId||job.wageMicro!==args[1]||job.workerId!==evidence.workerId)throw Error('Payment not bound to actual accepted hiring job');
   if(!evidence.clientId||lookup(evidence.clientId).role!=='client')throw Error('Exact paying client identity missing');
   const paymentTx=await read(()=>provider.getTransaction(evidence.verifiedPaymentHash));
   const expectedAmount=integer(evidence.paymentAmountMicro),wage=integer(args[1]);
   const contribution=wage*g.contributionBps/10000n;const due=contribution<g.contributionCap?contribution:g.contributionCap;
   if(wage>800000n||expectedAmount!==wage-due)throw Error('Wage and net payment do not reconcile');
   if(paymentTx.to!==TOKEN||getAddress(paymentTx.from)!==address(evidence.clientId)||paymentTx.data!==token.interface.encodeFunctionData('transfer',[g.worker,expectedAmount])||!wageReceipt.logs.some(l=>{try{let p=token.interface.parseLog(l);return getAddress(l.address)===TOKEN&&p.name==='Transfer'&&getAddress(p.args.from)===address(evidence.clientId)&&getAddress(p.args.to)===getAddress(g.worker)&&p.args.value===expectedAmount;}catch{return false;}}))throw Error('Exact worker payment receipt mismatch');
   write(`payment-${evidence.verifiedPaymentHash}.json`,{guaranteeId:args[0],intentId,hash:evidence.verifiedPaymentHash,reservedBeforeBroadcast:true});
   receipt=await call(a,intentId,'markPaid',[integer(args[0]),integer(args[1]),eHash(args[2])]);
  }else if(kind==='remit'){
   if(!['worker','client'].includes(a.role)||args.length!==1)throw Error('Remit role guard');
   const g=await read(()=>gt.guarantee(integer(args[0])));
   const job=JSON.parse(fs.readFileSync(path.join(out,`job-${args[0]}.json`)));
   if((a.role==='worker'&&job.workerId!==actorId)||(a.role==='client'&&(job.clientId!==actorId||job.withholdingAuthorized!==true)))throw Error('Remitter lacks exact job withholding authority');
   await approve(a,intentId,g.contributionDue);receipt=await call(a,intentId,'remit',[integer(args[0])]);
  }else if(kind==='cancel'){
   if(a.role!=='adjudicator'||args.length!==2||!evidence?.reviewHash)throw Error('Cancel adjudication missing');receipt=await call(a,intentId,'cancelGuarantee',[integer(args[0]),eHash(args[1])]);
  }else if(kind==='pause'){
   if(a.role!=='issuer'||args.length!==1||args[0]!==true||packet.day!==7)throw Error('Shutdown only pause guard');receipt=await call(a,intentId,'setPaused',[true]);
  }else{
   throw Error('Unsupported action: open and claim require completed acceptance/deadline/evidence guard review');
  }
  append({kind:'market-action-result',runId,intentId,day,actorId,action:kind,hash:receipt.hash,blockNumber:receipt.blockNumber,consentRecordHash:consent.recordHash,payloadHash:consent.payloadHash});
 }
 await snapshot(`balances-day-${packet.day}.json`,deployment.address);
 const state={reserve:await read(()=>gt.reserve()),outstanding:await read(()=>gt.outstanding()),totalStake:await read(()=>gt.totalStake()),totalDues:await read(()=>gt.totalDues()),guaranteeCount:await read(()=>gt.guaranteeCount())};
 write(`state-day-${packet.day}.json`,{runId,day:packet.day,state,actualBlock:await read(()=>provider.getBlockNumber()),note:'Virtual day does not advance chain settlement deadlines'});
 if(packet.day===7){
  if(!await read(()=>gt.paused()))throw Error('Day7 requires pause-origination action');
  const count=await read(()=>gt.guaranteeCount());if(count>24n)throw Error('Guarantee count exceeds experiment admission cap');
  const positions=[];for(let id=0n;id<count;id++){const g=await read(()=>gt.guarantee(id));positions.push({id,worker:g.worker,amount:g.amount,state:g.state,settleBy:g.settleBy,holdUntil:g.holdUntil,remitted:g.remitted,contributionDue:g.contributionDue});}
  const unresolved=positions.filter(g=>g.state===1n),unremitted=positions.filter(g=>g.state===2n&&!g.remitted);
  const contractBalance=await read(()=>token.balanceOf(deployment.address));
  if(contractBalance<state.reserve+state.totalStake)throw Error('Contract token accounting mismatch');
  write('shutdown-reconciliation.json',{runId,originationPaused:true,settlementComplete:unresolved.length===0,unresolved,unremitted,retainedStake:state.totalStake,retainedDues:state.totalDues,contractBalance,strayTokenBalance:contractBalance-state.reserve-state.totalStake,note:'No forced claims, withdrawals or synthetic timestamp expiry. Unresolved positions remain explicitly outstanding.'});
 }
 write('checkpoint.json',{...checkpoint,marketDay:packet.day,feeBound,gasFunding,tokenSpend,marketReady:false,phase:'bootstrap-only-complete',unsupported:[],state});
}
