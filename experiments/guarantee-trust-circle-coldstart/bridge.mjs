import {JsonRpcProvider, Wallet, NonceManager, Contract, parseEther, formatEther, zeroPadValue, ZeroHash} from 'ethers';
import fs from 'node:fs';
process.on('uncaughtException',e=>{console.error('Bridge stopped: '+(e.code||e.message.split(' (')[0].slice(0,140)));process.exit(1);});
process.on('unhandledRejection',e=>{console.error('Bridge stopped: '+(e?.code||'promise failure'));process.exit(1);});
const out='bridge-evidence'; fs.mkdirSync(out,{recursive:true});
const expected='0x38e9845A1Df22c59Bfc693bf2CEAa3361158d6d1';
const p1=new JsonRpcProvider('https://ethereum-sepolia-rpc.publicnode.com');
const p2=new JsonRpcProvider('https://sepolia.base.org');
const signer1=new NonceManager(new Wallet(process.env.TEST_WALLET_PRIVATE_KEY,p1));
const signer2=new NonceManager(new Wallet(process.env.TEST_WALLET_PRIVATE_KEY,p2));
if((await signer1.getAddress()).toLowerCase()!==expected.toLowerCase()) throw Error('Unexpected funded wallet');
if((await p1.getNetwork()).chainId!==11155111n || (await p2.getNetwork()).chainId!==84532n) throw Error('Testnet chain mismatch');
const abi=['function balanceOf(address) view returns(uint256)','function approve(address,uint256) returns(bool)'];
const sourceUSDC='0x1c7d4b196cb0c7b01d743fbc6116a902379c7238';
const baseUSDC='0x036cbd53842c5426634e7929541ec2318f3dcf7e';
const messenger='0x8fe6b999dc680ccfdd5bf7eb0974218be2542daa';
const transmitter='0xe737e5cebeeba77efe34d4aa090756590b1ce275';
const bridge='0xfd0bf71f60660e2f608ed56e1659c450eb113120';
const token1=new Contract(sourceUSDC,abi,signer1), token2=new Contract(baseUSDC,abi,p2);
const evidence={wallet:expected,sourceChain:11155111,destinationChain:84532,amount:'1000000000',transactions:[]};
function save(){fs.writeFileSync(out+'/bridge.json',JSON.stringify(evidence,null,2));}
async function send(label,promise){const tx=await promise; console.log('TX '+label+' '+tx.hash);evidence.transactions.push({label,hash:tx.hash,chainId:Number(tx.chainId)});save();const r=await tx.wait();if(r.status!==1)throw Error(label+' failed');Object.assign(evidence.transactions.at(-1),{block:r.blockNumber,status:r.status,gasUsed:r.gasUsed.toString()});save();return r;}
evidence.before={sourceUSDC:(await token1.balanceOf(expected)).toString(),baseUSDC:(await token2.balanceOf(expected)).toString(),sourceETH:formatEther(await p1.getBalance(expected)),baseETH:formatEther(await p2.getBalance(expected))};save();console.log('BEFORE '+JSON.stringify(evidence.before));
for(const [p,a] of [[p1,sourceUSDC],[p1,messenger],[p1,bridge],[p2,baseUSDC],[p2,transmitter]])if(await p.getCode(a)==='0x')throw Error('Missing expected testnet contract');
if(await p1.getBalance(expected)<parseEther('0.05'))throw Error('Insufficient Sepolia test gas');
if(await p2.getBalance(expected)<parseEther('0.02'))await send('bridge-test-ETH',new Contract(bridge,['function depositETH(uint32,bytes) payable'],signer1).depositETH(200000,'0x',{value:parseEther('0.03')}));
if(await token1.balanceOf(expected)<1000000000n)throw Error('Insufficient source test USDC');
await send('approve-CCTP',token1.approve(messenger,1000000000n));
const burnReceipt=await send('burn-CCTP',new Contract(messenger,['function depositForBurn(uint256,uint32,bytes32,address,bytes32,uint256,uint32)'],signer1).depositForBurn(1000000000n,6,zeroPadValue(expected,32),sourceUSDC,ZeroHash,0,2000));
evidence.burnHash=burnReceipt.hash;save();
let att;
for(let i=0;i<180;i++){
 const resp=await fetch('https://iris-api-sandbox.circle.com/v2/messages/0?transactionHash='+evidence.burnHash);
 if(resp.ok){const data=await resp.json();att=data.messages?.find(x=>x.status==='complete'&&x.message&&x.attestation);if(att)break;}
 if(i%6===0)console.log('Waiting for Circle standard-transfer attestation');
 await new Promise(r=>setTimeout(r,10000));
}
if(!att)throw Error('Attestation pending; resume ONLY from recorded burn hash');
const msg=att.message;
const domainSource=Number(BigInt('0x'+msg.slice(10,18))),domainDest=Number(BigInt('0x'+msg.slice(18,26)));
if(domainSource!==0||domainDest!==6)throw Error('CCTP message domain mismatch');
const recipient='0x'+msg.slice(2+184*2,2+216*2); // V2 header 148 bytes, mint recipient at burn-body byte 36.
const amount=BigInt('0x'+msg.slice(2+216*2,2+248*2));
if(recipient.toLowerCase()!==zeroPadValue(expected,32).toLowerCase()||amount!==1000000000n)throw Error('CCTP mint recipient/amount mismatch');
evidence.attestation={eventNonce:att.eventNonce,status:att.status,messageHash:att.messageHash};save();
for(let i=0;i<120&&await p2.getBalance(expected)<parseEther('0.01');i++){if(i%6===0)console.log('Waiting for Base Sepolia test ETH deposit');await new Promise(r=>setTimeout(r,10000));}
if(await p2.getBalance(expected)<parseEther('0.01'))throw Error('Base test ETH deposit pending');
await send('mint-CCTP',new Contract(transmitter,['function receiveMessage(bytes,bytes) returns(bool)'],signer2).receiveMessage(att.message,att.attestation));
evidence.after={sourceUSDC:(await token1.balanceOf(expected)).toString(),baseUSDC:(await token2.balanceOf(expected)).toString(),sourceETH:formatEther(await p1.getBalance(expected)),baseETH:formatEther(await p2.getBalance(expected))};
if(BigInt(evidence.after.baseUSDC)-BigInt(evidence.before.baseUSDC)!==1000000000n)throw Error('Mint balance did not reconcile');
save();console.log('BRIDGE_COMPLETE '+JSON.stringify(evidence));
