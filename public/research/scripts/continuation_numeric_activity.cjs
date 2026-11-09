// Read-only validation of four declared mirror-family forms of one256-bit number rule.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const filename = path.resolve(__dirname,'continue_printed_line_ascii_keys.js');
const prefix = fs.readFileSync(filename,'utf8').split('for (const [page, lines] of Object.entries(pages))')[0];
const taskOut = path.resolve(__dirname,'../analysis_outputs/continuation_20261109/numeric_inventory');
const spec = JSON.parse(fs.readFileSync(path.join(taskOut,'numeric_inventory.json'),'utf8'));
const tail = `
for (const rec of taskSpec.candidates) addCandidate({direction:rec.direction, scalarHex:rec.scalarHex}, Buffer.from(rec.scalarHex,'hex'));
vectorSink(candidates);
`;
let derived;
vm.runInNewContext(prefix+tail,{ require, Buffer, process, console, __dirname:path.dirname(filename), taskSpec:spec, vectorSink:r=>{derived=r;} },{filename});
async function query(address) {
 const url = 'https://blockstream.info/api/address/'+address;
 const r = await fetch(url,{signal:AbortSignal.timeout(25000)});
 if(!r.ok)throw new Error('HTTP '+r.status);
 const d=await r.json();
 if(!d.chain_stats||!d.mempool_stats)throw new Error('Missing statistics');
 return {address,url,chainStats:d.chain_stats,mempoolStats:d.mempool_stats,checkedAtUtc:new Date().toISOString()};
}
(async()=>{
 const previousPath=path.join(taskOut,'numeric_activity.json');
 const previous=fs.existsSync(previousPath)?JSON.parse(fs.readFileSync(previousPath,'utf8')):{};
 const cache=new Map((previous.addressChecks||[]).filter(r=>!r.error).map(r=>[r.address,r]));
 const out={method:spec.selectedRule,candidates:derived,checked:false,addressChecks:[]};
 const addrs=[...new Set(derived.flatMap(c=>Object.values(c.addresses)))];
 out.addressChecks=addrs.filter(a=>cache.has(a)).map(a=>cache.get(a));
 out.reusedAddressChecks=out.addressChecks.length;
 const remaining=addrs.filter(a=>!cache.has(a));
 for(let i=0;i<remaining.length;i+=2){
  const rs=await Promise.allSettled(remaining.slice(i,i+2).map(query));
  rs.forEach((v,j)=>out.addressChecks.push(v.status==='fulfilled'?v.value:{address:remaining[i+j],error:v.reason.message}));
  fs.writeFileSync(path.join(taskOut,'numeric_activity.json'),JSON.stringify(out,null,2)+'\n');
  if(i+2<remaining.length)await new Promise(r=>setTimeout(r,700));
 }
 out.checked=out.addressChecks.length===addrs.length&&out.addressChecks.every(r=>!r.error);
 out.activeAddresses=out.addressChecks.filter(r=>!r.error&&(r.chainStats.tx_count||r.mempoolStats.tx_count));
 out.checkedAtUtc=new Date().toISOString();
 fs.writeFileSync(path.join(taskOut,'numeric_activity.json'),JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({candidates:derived.length,addresses:addrs.length,checked:out.checked,reused:out.reusedAddressChecks,newChecks:remaining.length,errors:out.addressChecks.filter(r=>r.error),active:out.activeAddresses}));
})();
