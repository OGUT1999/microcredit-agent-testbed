/** Read-only receipt verifier. Expects registered quantities, never caller-supplied probes. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import {JsonRpcProvider,Interface,Contract,getAddress,verifyTypedData,version} from 'ethers';
const req=JSON.parse(fs.readFileSync(0,'utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const check=(b,m)=>{if(!b)throw Error(m);};
const eq=(a,b)=>String(a).toLowerCase()===String(b).toLowerCase();
check(version==='6.15.0','Unreviewed ethers version');
const bytes=fs.readFileSync(req.pin.artifactPath);check(sha(bytes)===req.pin.artifactSha256,'ABI artifact pin mismatch');
const artifact=JSON.parse(bytes),gtI=new Interface(artifact.abi);
check(artifact.sourceCommit==='ec93c76779b5e2d52ab7b87cf82b3fd400205969'&&artifact.sourceCommit===req.pin.sourceCommit,'Source revision mismatch');
const tokenI=new Interface(['function transfer(address,uint256) returns(bool)','event Transfer(address indexed from,address indexed to,uint256 value)']);
const provider=new JsonRpcProvider(process.env.BASE_SEPOLIA_RPC_URL||'https://sepolia.base.org');
check((await provider.getNetwork()).chainId===84532n,'Chain mismatch');
if(req.operation==='bootstrap'){
 const pin=req.pin,proofs=req.fundingTransactions;
 check(Array.isArray(proofs),'Bootstrap funding hashes required');
 const expected=Object.entries(pin.actors).filter(([,a])=>['client','backer','sponsor'].includes(a.role));
 check(proofs.length===expected.length&&new Set(proofs.map(p=>p.actorId)).size===expected.length&&new Set(proofs.map(p=>p.transactionHash)).size===expected.length,'Bootstrap coverage/replay mismatch');
 const transfers=[];
 for(const [actorId,actor] of expected){
  const ref=proofs.find(p=>p.actorId===actorId);check(ref,'Actor funding receipt absent');
  const [tx,r]=await Promise.all([provider.getTransaction(ref.transactionHash),provider.getTransactionReceipt(ref.transactionHash)]);
  const amount={client:800000n,backer:300000n,sponsor:500000n}[actor.role];
  check(tx&&r&&r.status===1&&eq(r.hash,tx.hash)&&eq(tx.hash,ref.transactionHash)&&tx.chainId===84532n
   &&eq(tx.from,pin.issuer)&&eq(r.from,pin.issuer)&&eq(tx.to,pin.token)&&eq(r.to,pin.token)&&tx.value===0n
   &&eq(tx.blockHash,r.blockHash)&&eq((await provider.getBlock(r.blockNumber)).hash,r.blockHash),'Bootstrap transaction identity mismatch');
  check(eq(tx.data,tokenI.encodeFunctionData('transfer',[actor.address,amount])),'Bootstrap exact transfer calldata mismatch');
  check(r.logs.filter(l=>{try{const p=tokenI.parseLog(l);return eq(l.address,pin.token)&&p.name==='Transfer'&&eq(p.args.from,pin.issuer)&&eq(p.args.to,actor.address)&&p.args.value===amount;}catch{return false;}}).length===1,'Bootstrap exact transfer log mismatch');
  transfers.push({actorId,address:actor.address,amount:amount.toString(),transactionHash:tx.hash,blockNumber:r.blockNumber,blockHash:r.blockHash});
 }
 check(transfers.reduce((n,t)=>n+BigInt(t.amount),0n)===38200000n,'Bootstrap total mismatch');
 console.log(JSON.stringify({schema:'verified-real-agents-bootstrap/1',chainId:84532,runId:pin.runId,token:pin.token,totalMicro:'38200000',transfers}));
 process.exit(0);
}

const [tx,receipt]=await Promise.all([provider.getTransaction(req.transactionHash),provider.getTransactionReceipt(req.transactionHash)]);
check(tx&&receipt&&receipt.status===1,'Successful mined receipt required');
check(eq(tx.hash,req.transactionHash)&&eq(receipt.hash,tx.hash)&&eq(tx.blockHash,receipt.blockHash)&&tx.blockNumber===receipt.blockNumber,'Receipt identity mismatch');
check(tx.chainId===84532n&&tx.value===0n&&eq(tx.from,req.expected.sender)&&eq(receipt.from,req.expected.sender),'Sender chain/value mismatch');
const pin=req.pin,e=req.expected,block=receipt.blockNumber;
const deployed=await provider.getTransactionReceipt(pin.deploymentTransactionHash);
check(deployed&&deployed.status===1&&eq(deployed.contractAddress,pin.contract)&&deployed.blockNumber<=block,'Fresh deployment receipt mismatch');
const deploymentTx=await provider.getTransaction(pin.deploymentTransactionHash);
const bytecode=typeof artifact.bytecode==='string'?artifact.bytecode:artifact.bytecode.object;
check(deploymentTx.to===null&&eq(deploymentTx.from,pin.issuer)&&deploymentTx.chainId===84532n&&deploymentTx.value===0n
 &&eq(deploymentTx.data,bytecode+gtI.encodeDeploy([pin.token,pin.issuer,pin.adjudicator,pin.issuer,6000000n,1000000n]).slice(2)), 'Exact source constructor deployment mismatch');
check(eq((await provider.getBlock(block)).hash,receipt.blockHash),'Canonical block mismatch');
const runtime=await provider.getCode(pin.contract,block);
check(sha(runtime)===pin.runtimeSha256,'Runtime code mismatch');
const mask=code=>{let b=Buffer.from(code.replace(/^0x/,''),'hex');for(const refs of Object.values(artifact.immutableReferences))for(const r of refs)b.fill(0,r.start,r.start+r.length);return b.toString('hex');};
const compiledRuntime=typeof artifact.deployedBytecode==='string'?artifact.deployedBytecode:artifact.deployedBytecode.object;
check(mask(runtime)===mask(compiledRuntime),'Runtime differs from exact source artifact outside known immutables');
const gt=new Contract(pin.contract,artifact.abi,provider);
for(const [name,value] of [['token',pin.token],['owner',pin.issuer],['issuer',pin.issuer],['adjudicator',pin.adjudicator]])check(eq(await gt[name]({blockTag:block}),value),'Role/token binding mismatch');
const expectedTarget=e.action==='pay'?pin.token:pin.contract;
check(eq(tx.to,expectedTarget)&&eq(receipt.to,expectedTarget),'Transaction target mismatch');
const iface=e.action==='pay'?tokenI:gtI;
const parsed=iface.parseTransaction({data:tx.data,value:tx.value});check(parsed,'Unknown calldata');
const name={'fund-reserve':'fundReserve',stake:'stake',attest:'attest',open:'openGuarantee',pay:'transfer','mark-paid':'markPaid',claim:'claim',cancel:'cancelGuarantee'}[e.action];
check(parsed.name===name,'Operation mismatch');
let guaranteeId=e.guaranteeId;
if(e.action==='open'){
 const a=parsed.args[0],components=gtI.getFunction('openGuarantee').inputs[0].components;
 for(const f of components)check(eq(a[f.name],e.acceptance[f.name]),'Acceptance field mismatch: '+f.name);
 const fields=components.map(f=>({name:f.name,type:f.type}));
 const recovered=verifyTypedData({name:'GuaranteeTrust',version:'2',chainId:84532,verifyingContract:pin.contract},{Acceptance:fields},e.acceptance,parsed.args[1]);
 check(eq(recovered,e.worker),'Worker signature mismatch');
}else{
 const expectedArgs=e.args;
 check(parsed.args.length===expectedArgs.length,'Argument count mismatch');
 for(let i=0;i<expectedArgs.length;i++)check(eq(parsed.args[i],expectedArgs[i]),'Calldata argument mismatch');
}
const logs=[];
for(const raw of receipt.logs){
 let p;try{if(eq(raw.address,pin.contract))p=gtI.parseLog(raw);else if(eq(raw.address,pin.token))p=tokenI.parseLog(raw);}catch{}
 if(!p)continue;
 const args={};p.fragment.inputs.forEach((f,i)=>args[f.name]=typeof p.args[i]==='bigint'?p.args[i].toString():p.args[i]);
 logs.push({address:raw.address,name:p.name,args});
}
const eventName={'fund-reserve':'ReserveFunded',stake:'Staked',attest:'Attested',open:'GuaranteeOpened',pay:'Transfer','mark-paid':'GuaranteePaid',claim:'Claimed',cancel:'GuaranteeCancelled'}[e.action];
const matching=logs.filter(l=>l.name===eventName&&eq(l.address,e.action==='pay'?pin.token:pin.contract));
check(matching.length===1,'Exactly one operation event required');
const ev=matching[0].args;
const assertField=(key,val)=>check(eq(ev[key],val),'Event field mismatch: '+key);
if(e.action==='fund-reserve'){assertField('from',e.sender);assertField('amount',e.amount);}
if(e.action==='stake'){assertField('member',e.sender);assertField('amount',e.amount);}
if(e.action==='attest'){assertField('attester',e.sender);assertField('member',e.worker);assertField('amount',e.amount);
 check(await gt.consent(e.worker,e.sender,{blockTag:block}),'Worker live consent absent');
 check(eq(await gt.backing(e.sender,e.worker,{blockTag:block}),ev.backing),'Backing state mismatch');}
if(e.action==='open'){guaranteeId=ev.id;for(const k of ['worker','clientId','amount','termsHash','settleBy'])assertField(k,e.acceptance[k]);
 const group=e.acceptance.groupId==='0x'+'0'.repeat(64)?e.acceptance.clientId:e.acceptance.groupId;assertField('groupId',group);
 for(const p of ['contributionBps','contributionCap','remitWindow'])check(eq(await gt[p]({blockTag:block}),e.acceptance[p]),'Live contribution policy mismatch');}
if(e.action==='pay'){assertField('from',e.sender);assertField('to',e.worker);assertField('value',e.amount);}
if(e.action==='mark-paid'){assertField('id',e.guaranteeId);assertField('wage',e.grossWage);}
if(e.action==='claim'){assertField('id',e.guaranteeId);assertField('worker',e.worker);assertField('amount',e.amount);assertField('evidenceHash',e.args[1]);}
if(e.action==='cancel'){assertField('id',e.guaranteeId);assertField('resolutionHash',e.args[1]);}
if(['fund-reserve','stake','pay','claim'].includes(e.action)){
 const from=e.action==='claim'?pin.contract:e.sender,to=['fund-reserve','stake'].includes(e.action)?pin.contract:e.worker;
 check(logs.filter(l=>l.name==='Transfer'&&eq(l.address,pin.token)&&eq(l.args.from,from)&&eq(l.args.to,to)&&eq(l.args.value,e.amount)).length===1,'Exact token transfer required');
}
let guarantee=null;
if(guaranteeId!==undefined&&guaranteeId!==null){
 const g=await gt.guarantee(guaranteeId,{blockTag:block});
 const fields=gtI.getFunction('guarantee').outputs[0].components;
 guarantee={};for(const f of fields)guarantee[f.name]=typeof g[f.name]==='bigint'?g[f.name].toString():g[f.name];
 check(eq(g.worker,e.worker)&&eq(g.amount,e.guaranteeAmount)&&eq(g.termsHash,e.termsHash),'Exact guarantee readback mismatch');
 const expectedState={open:'1','mark-paid':'2',claim:'3',cancel:'4'}[e.action];
 if(expectedState)check(eq(g.state,expectedState),'Guarantee terminal state mismatch');
 if(e.action==='mark-paid')check(eq(g.wage,e.grossWage),'Gross wage readback mismatch');
}
const state={};for(const key of ['reserve','totalStake','sponsorCapital','totalDues','outstanding'])state[key]=(await gt[key]({blockTag:block})).toString();
const token=new Contract(pin.token,['function balanceOf(address) view returns(uint256)'],provider);
state.contractTokenBalance=(await token.balanceOf(pin.contract,{blockTag:block})).toString();
check(BigInt(state.reserve)+BigInt(state.totalStake)===BigInt(state.contractTokenBalance),'Token accounting mismatch');
check(BigInt(state.sponsorCapital)+BigInt(state.totalDues)===BigInt(state.reserve),'Reserve accounting mismatch');
console.log(JSON.stringify({schema:'verified-real-agents-action/1',registrationHash:req.registrationHash,transactionHash:tx.hash,chainId:84532,
 blockNumber:block,blockHash:receipt.blockHash,status:1,from:tx.from,to:tx.to,value:tx.value.toString(),
 action:e.action,method:parsed.name,event:matching[0],tokenTransfers:logs.filter(l=>l.name==='Transfer'),
 guaranteeId:guaranteeId??null,guarantee,state}));
