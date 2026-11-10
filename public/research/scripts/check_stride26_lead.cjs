// Separate, bounded stride26 follow-up. Target work requires public registration.
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const os=require('node:os');
const ROOT=fs.existsSync(path.join(__dirname,'minikey26_address_audit.cjs'))?path.resolve(__dirname,'..'):path.resolve(__dirname,'../../..','site/public/research');
const SITE=path.resolve(ROOT,'..','..');
const SELF='scripts/check_stride26_lead.cjs';
const PROTOCOL='analysis_outputs/continuation_20261110/stride26_history/PROTOCOL.json';
const SOURCE_RESULT='analysis_outputs/continuation_20261110/columns_compatibility/RESULT.json';
const SOURCE_WITNESS='analysis_outputs/continuation_20261110/columns_compatibility/SOURCE_WITNESS_REVIEW.json';
const RESULT_SHA='0f1d2cbac0695e1328e878b9e3e080479c6405a65ff82a5d51019543b133fe6d';
const WITNESS_SHA='f61a514cf4c839574646a3c459032af91b8246e727006418c133e2d7f6ccef58';
const FORMS_SHA='a634eef32022587b1a1c178474e7c2347f9db03a1da2c8ef300ed4f203e72823';
const VALIDATION_SHA='69978ce65b2655860717b86fc575f7c92295bbacf5891419df1151e7b0d3f99e';
const LOCK_SHA='e2754b2bbb763bd18670735b4b317dd9235e34f1d961123dbe551603657551a8';
const NODE_CORE='scripts/minikey26_address_audit.cjs';
const PY_CORE='scripts/independent_minikey26_addresses.py';
const CLASSIFIER='scripts/check_minikey26_lead.cjs';
const FIXED_CODE={
 [NODE_CORE]:'a351e20f4bb5b9ab20fdd97dc07f8d87afe48962fb25dff20a008a56e83b7a64',
 [PY_CORE]:'27f1de62281f4c4e43906acd65f9ae8fa6b264d5dc4cf54a3faf998719479ba8',
 [CLASSIFIER]:'98146d0f97b359b5830991048974474290cac4f1cd97218986af9b334f744e44'};
const TYPES=['P2PKH uncompressed','P2PKH compressed','P2SH-P2WPKH','P2WPKH','P2TR key-path with BIP341 TapTweak'];
const PROVIDERS=['blockstream','mempool'];
const COHORTS=['funky-sand-direct','issue26-first-words','issue27-body-stride12','issue27-frozen-stream-coverage'];
const SURFACE={requiresWhitespaceCompaction:true,presentInSavedStrictKnownCompactedForm:true,contiguousInAnyUnmodifiedOriginalReading:false,physicalPrintedKeyAuthenticated:false};
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function inside(file,root){return file===root||file.startsWith(root+path.sep);}
function publicFile(relative){
 assert.ok(typeof relative==='string'&&!path.isAbsolute(relative)&&!relative.split(/[\\/]/).includes('..'),'Relative public path required');
 const file=fs.realpathSync(path.join(ROOT,relative));assert.ok(inside(file,ROOT)&&fs.statSync(file).isFile(),'Public path escape');return file;
}
function readCapped(file,cap){const st=fs.statSync(file);assert.ok(st.isFile()&&st.size<=cap,'File cap exceeded');const raw=fs.readFileSync(file);assert.ok(raw.length<=cap,'File grew beyond cap');return raw;}
function privatePath(value,fresh=false){
 const raw=path.resolve(value);
 const file=fs.existsSync(raw)?fs.realpathSync(raw):path.join(fs.realpathSync(path.dirname(raw)),path.basename(raw));
 assert.ok(!inside(raw,SITE)&&!inside(file,SITE)&&![...raw.split(path.sep),...file.split(path.sep)].some(p=>p.toLowerCase()==='public'),'Private path outside entire checkout required');
 if(fresh)assert.ok(!fs.existsSync(file)&&!fs.existsSync(raw),'Fresh output required');
 return file;
}
function writePrivate(file,value){fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n',{flag:'wx',mode:0o600});fs.chmodSync(file,0o600);}
function frozenHelpers(){
 for(const [relative,pin]of Object.entries(FIXED_CODE))assert.equal(hash(readCapped(publicFile(relative),2000000)),pin,'Frozen helper changed');
 return {audit:require(publicFile(NODE_CORE)),classifier:require(publicFile(CLASSIFIER))};
}
function python(args){
 const helper=publicFile(PY_CORE);assert.equal(hash(readCapped(helper,2000000)),FIXED_CODE[PY_CORE]);
 const r=spawnSync('python3',['-B',helper,...args],{encoding:'utf8',timeout:30000,maxBuffer:65536});
 assert.equal(r.status,0,'Independent implementation failed');return JSON.parse(r.stdout);
}
function dependencyVersion(name){
 let dir=path.dirname(require.resolve(name,{paths:[ROOT]}));
 while(path.dirname(dir)!==dir){const file=path.join(dir,'package.json');if(fs.existsSync(file)){const p=JSON.parse(fs.readFileSync(file,'utf8'));if(p.name===name)return p.version;}dir=path.dirname(dir);}
 throw new Error('Dependency metadata unavailable');
}
function validateFrozenResult(result){
 assert.equal(result.version,1);assert.equal(result.testId,'columns-fixed-output-compatibility');
 assert.equal(result.registrationCommit,'d95986156cd785c3836ad060fdcaeabdebabcb01');
 assert.equal(result.protocolSha256,'7e7868d2fa93110cced1ab8f6f8ff5e71c2235aabdc662f558ffcbf90f504cc5');
 for(const f of ['scopeComplete','compatibilityGatesComplete','allOriginalArtifactIdentitiesVerified','privateReviewRequired'])assert.equal(result[f],true);
 for(const f of ['newSelectorIntroduced','ocrRerun','sourceRepairs','semanticReviewPerformed'])assert.equal(result[f],false);
 assert.equal(result.privateArtifactIntegrity['VALIDATION.private.json'],VALIDATION_SHA);
 assert.equal(result.counts.sumNominalValidRecords,1);
 assert.deepEqual(result.cohorts.map(c=>c.id),COHORTS);
 for(const c of result.cohorts){
  assert.ok(Object.values(c.common.validCounts).every(n=>n===0));
  assert.equal(c.minikey26.validCount,c.id==='issue27-body-stride12'?1:0);
 }
 const stride=result.cohorts[2];assert.equal(stride.recordCount,72);assert.equal(stride.formCount,96);
 assert.equal(stride.strictKnown.recordCount,60);assert.equal(stride.strictKnown.formCount,78);
 assert.equal(stride.strictKnown.nestedInNominal,true);assert.equal(stride.strictKnown.physicalSourceComplete,false);
 assert.equal(stride.strictKnown.minikey26.validCount,1);assert.equal(stride.strictKnown.minikey26.checksumCalls,0);
 assert.equal(stride.strictKnown.minikey26.status,'derived-from-nominal-validation');
 return true;
}
function validateProtocolHeader(p,registration){
 assert.match(registration,/^[a-f0-9]{40}$/);assert.equal(p.schemaVersion,1);assert.equal(p.testId,'stride26-history');
 assert.equal(p.candidateLength,26);assert.ok(!Object.hasOwn(p,'candidateFingerprint'));
 assert.deepEqual(p.sourceSurface,SURFACE);assert.deepEqual(p.addressTypes,TYPES);assert.deepEqual(p.providers,PROVIDERS);
 assert.equal(p.requestsMaximum,10);assert.equal(p.concurrencyMaximum,2);assert.equal(p.retries,0);assert.equal(p.httpStatusRequired,200);
 assert.deepEqual(Object.keys(p.sourceHashes).sort(),[SOURCE_RESULT,SOURCE_WITNESS,'package-lock.json'].sort());
 assert.equal(p.sourceHashes[SOURCE_RESULT],RESULT_SHA);assert.equal(p.sourceHashes['package-lock.json'],LOCK_SHA);
 assert.equal(p.sourceHashes[SOURCE_WITNESS],WITNESS_SHA);
 assert.deepEqual(Object.keys(p.scriptHashes).sort(),[SELF,...Object.keys(FIXED_CODE)].sort());
 for(const [file,pin]of Object.entries(FIXED_CODE))assert.equal(p.scriptHashes[file],pin);
 assert.ok(Object.values(p.scriptHashes).every(s=>/^[a-f0-9]{64}$/.test(s)));
 assert.deepEqual(p.dependencyVersions,{'bitcoinjs-lib':'7.0.0','tiny-secp256k1':'2.2.4'});
}
function gitBlob(registration,relative){
 const name=registration+':public/research/'+relative;
 const size=spawnSync('git',['cat-file','-s',name],{cwd:ROOT,encoding:'utf8',timeout:30000,maxBuffer:64});
 assert.equal(size.status,0,'Missing registration object');assert.match(size.stdout,/^[0-9]+\n$/);const n=Number(size.stdout);assert.ok(n<=2000000,'Git blob cap');
 const r=spawnSync('git',['cat-file','blob',name],{cwd:ROOT,timeout:30000,maxBuffer:2000001});assert.equal(r.status,0);assert.equal(r.stdout.length,n);return r.stdout;
}
function verifyRegistered(p,pbytes,registration,currentReader,blobReader){
 assert.deepEqual(blobReader(registration,PROTOCOL),pbytes,'Protocol not registered');
 const files={};for(const [relative,pin]of Object.entries({...p.sourceHashes,...p.scriptHashes})){
  const registered=blobReader(registration,relative);assert.equal(hash(registered),pin,'Registered file pin differs');
  const current=currentReader(relative);assert.deepEqual(current,registered,'Current bytes differ from registration');files[relative]=current;
 }return files;
}
function validateProtocol(file,registration){
 assert.equal(fs.realpathSync(__filename),publicFile(SELF),'Fixed public script required');
 assert.equal(fs.realpathSync(file),publicFile(PROTOCOL),'Fixed public protocol required');
 const pbytes=readCapped(publicFile(PROTOCOL),1000000),p=JSON.parse(pbytes);validateProtocolHeader(p,registration);
 const kind=spawnSync('git',['cat-file','-t',registration],{cwd:ROOT,encoding:'utf8',timeout:30000,maxBuffer:64});assert.equal(kind.status,0);assert.equal(kind.stdout,'commit\n','Actual Git commit required');
 const files=verifyRegistered(p,pbytes,registration,r=>readCapped(publicFile(r),2000000),gitBlob);
 for(const [name,v]of Object.entries(p.dependencyVersions))assert.equal(dependencyVersion(name),v);
 validateFrozenResult(JSON.parse(files[SOURCE_RESULT]));
 // validateSourceWitness is bound to the finalized safe receipt, never a guessed source interpretation.
 validateSourceWitness(JSON.parse(files[SOURCE_WITNESS]));
 return {protocol:p,protocolSha256:hash(pbytes)};
}
function selectSingle(bundle,audit,classifier){
 assert.equal(bundle.schemaVersion,1);assert.equal(bundle.testId,'columns-fixed-output-compatibility');
 assert.deepEqual(bundle.cohorts.map(c=>c.id),COHORTS);
 const positives=[];
 for(const c of bundle.cohorts){
  assert.equal(c.evaluationAll.rawPositives.length,0,'Unexpected other-format positive');
  for(const p of c.evaluationAll.minikey26Positives)positives.push({cohort:c.id,record:p});
 }
 assert.equal(positives.length,1);assert.equal(positives[0].cohort,'issue27-body-stride12');
 const stride=bundle.cohorts[2],record=positives[0].record;
 assert.equal(stride.evaluationAll.minikey26.validCount,1);assert.equal(stride.evaluationStrictKnown.minikey26.validCount,1);
 assert.equal(stride.evaluationStrictKnown.rawPositives.length,0);
 assert.deepEqual(stride.evaluationStrictKnown.minikey26Positives,[record],'Nominal/strict lead mismatch');
 assert.deepEqual(Object.keys(record).sort(),['format','length','checkBits','private','fingerprint','value'].sort());
 assert.equal(record.format,'minikey');assert.equal(record.length,26);assert.equal(record.checkBits,8);assert.equal(record.private,true);
 assert.ok(typeof record.value==='string'&&record.value.length===26&&audit.checkMinikey(record.value).formatValid);
 assert.equal(record.fingerprint,classifier.fingerprint(record.value),'Domain fingerprint mismatch');
 return record.value;
}
async function queryFive(addresses,audit,fetcher){
 assert.deepEqual(addresses.map(a=>a.type),TYPES);assert.equal(addresses.length,5);
 const counters={requestsAttempted:0};const requests=addresses.flatMap(a=>PROVIDERS.map(provider=>({...a,provider})));
 const results=await audit.mapTwo(requests,async r=>{
  assert.ok(counters.requestsAttempted<10,'Attempt budget exceeded');
  const result=await audit.requestStats(r.provider,r.address,counters,fetcher);
  // Exact200 is this new protocol's explicit policy; the frozen helper accepts other2xx.
  if(result.status==='ok'&&result.httpStatus!==200)return {type:r.type,...result,status:'error',error:'Unexpected success status'};
  return {type:r.type,...result};
 });
 assert.equal(counters.requestsAttempted,10,'Incomplete attempt scope');return {results,counters};
}
function validateSourceWitness(w){
 assert.equal(w.version,1);assert.equal(w.status,'PASS-scoped-saved-form-association');
 assert.equal(w.registrationCommit,'d95986156cd785c3836ad060fdcaeabdebabcb01');
 assert.equal(w.protocolSha256,'7e7868d2fa93110cced1ab8f6f8ff5e71c2235aabdc662f558ffcbf90f504cc5');
 assert.equal(w.primaryResultSha256,RESULT_SHA);assert.equal(w.privateValidationArtifactSha256,VALIDATION_SHA);assert.equal(w.privateFormsArtifactSha256,FORMS_SHA);
 assert.equal(w.cohort,'issue27-body-stride12');
 assert.deepEqual(w.checks,{literal26SBase58Syntax:true,nominalEqualsCachedStrictPositive:true,presentInSavedStrictKnownCompactedForm:true,contiguousInAnyUnmodifiedOriginalReading:false,compactionRegeneratedByReviewer:false,newGlyphMappingPerformed:false});
 assert.deepEqual(w.sourceKnownScope,{nominalReadings:72,strictKnownReadings:60,strictKnownForms:78,nestedSubset:true,physicalSourceComplete:false});
 assert.ok(Object.values(w.activity).every(n=>n===0));return true;
}
function safeResult(protocol,protocolSha256,registration,startedAtUTC,results,counters,controls,classifier){
 return {schemaVersion:1,testId:'stride26-history',startedAtUTC,completedAtUTC:new Date().toISOString(),registrationCommit:registration,
  protocolSha256,sourceHashes:protocol.sourceHashes,scriptHashes:protocol.scriptHashes,
  sourceResultSha256:RESULT_SHA,sourceWitnessSha256:WITNESS_SHA,privateValidationArtifactSha256:VALIDATION_SHA,
  candidateLength:26,sourceSurface:{...SURFACE},checksumIndependentlyVerified:true,addressImplementationsAgree:true,addressCount:5,
  ...classifier.publicSummary(results,counters),controls,transactions:0,walletImports:0,limitations:protocol.limitations};
}
async function main(argv){
 process.umask(0o077);
 if(argv.length===1&&argv[0]==='--self-test'){console.log(JSON.stringify(await selfTest()));return;}
 const args={};for(let i=0;i<argv.length;i+=2){assert.ok(['--validation','--protocol','--registration-commit','--out'].includes(argv[i]));assert.ok(argv[i+1]&&!Object.hasOwn(args,argv[i]));args[argv[i]]=argv[i+1];}
 assert.equal(Object.keys(args).length,4);
 const {protocol,protocolSha256}=validateProtocol(path.resolve(args['--protocol']),args['--registration-commit']);
 const controls=await selfTest(); // Only published/synthetic controls, before target private input.
 const input=privatePath(args['--validation']),out=privatePath(args['--out'],true);
 assert.equal(fs.statSync(path.dirname(input)).mode&0o777,0o700,'Private input parent required');assert.equal(fs.statSync(input).mode&0o077,0,'Private input mode required');
 assert.equal(fs.statSync(path.dirname(out)).mode&0o777,0o700,'Private output parent required');
 const bytes=readCapped(input,64000000);assert.equal(hash(bytes),VALIDATION_SHA,'Whole validation artifact differs');
 const {audit,classifier}=frozenHelpers();const candidate=selectSingle(JSON.parse(bytes),audit,classifier);
 fs.mkdirSync(out,{recursive:false,mode:0o700});fs.chmodSync(out,0o700);const startedAtUTC=new Date().toISOString();
 const lead=path.join(out,'LEAD.private.json');writePrivate(lead,{format:'minikey',value:candidate});
 const independentPath=path.join(out,'ADDRESSES.python.private.json');python(['--lead',lead,'--out',independentPath]);
 const independent=JSON.parse(readCapped(independentPath,65536)).addresses;
 const addresses=audit.deriveAddresses(candidate);assert.deepEqual(addresses,independent,'Address implementations disagree');assert.deepEqual(addresses.map(a=>a.type),TYPES);
 // No network call occurs until the full ordered type/address vectors agree.
 const {results,counters}=await queryFive(addresses,audit);
 writePrivate(path.join(out,'HISTORY.private.json'),{addresses,results});
 const result=safeResult(protocol,protocolSha256,args['--registration-commit'],startedAtUTC,results,counters,controls,classifier);
 const serialized=JSON.stringify(result);assert.ok(!serialized.includes(candidate));for(const item of addresses)assert.ok(!serialized.includes(item.address));
 // A direct allowlist and value omission check need no extra bare target SHA.
 writePrivate(path.join(out,'RESULT.json'),result);
 console.log(JSON.stringify({outcome:result.outcome,scopeComplete:result.scopeComplete,addressCount:5,addressImplementationsAgree:true,requestsAttempted:counters.requestsAttempted,successfulResponses:results.filter(r=>r.status==='ok').length,transactions:0}));
}
function protocolTemplate(){
 return {schemaVersion:1,testId:'stride26-history',candidateLength:26,
  candidateSelection:'The single unchanged26-character minikey positive in the registered combined validation artifact, identical in nominal and cached strict-known stride12 records. No edited candidates and no public candidate fingerprint.',
  sourceSurface:{...SURFACE},addressTypes:[...TYPES],providers:[...PROVIDERS],requestsMaximum:10,concurrencyMaximum:2,retries:0,httpStatusRequired:200,
  endpointPaths:['https://blockstream.info/api/address/:address','https://mempool.space/api/address/:address'],
  queryPolicy:'GET all five constructions at both fixed providers; exactHTTP200 required;20-second timeout, redirects rejected, no-cache/no-store. Validate matching address and all ten nonnegative safe integer statistics per response. Any failure/disagreement is inconclusive, never zero.',
  addressDerivationPolicy:'Require exact ordered Node/Python five-address agreement before requests. Standard ASCII minikey SHA256 scalar only inside the address helpers; no scalar output/identifier. P2TR even-Y x-only lift with BIP341 TapTweak, no script tree. No HD paths/passwords/script guessing.',
  zeroCriterion:'All ten attempts returnHTTP200 with valid, matching all-zero chain/mempool statistics at both providers for every construction, at recorded times only.',
  failurePolicy:'Any source/code/registration/control/input/derivation/request/statistics/provider failure is inconclusive. Any validated activity requires private review; never ownership/funding/prize authentication.',
  sourceHashes:{[SOURCE_RESULT]:RESULT_SHA,[SOURCE_WITNESS]:WITNESS_SHA,'package-lock.json':LOCK_SHA},
  scriptHashes:{[SELF]:hash(fs.readFileSync(__filename)),...FIXED_CODE},dependencyVersions:{'bitcoinjs-lib':'7.0.0','tiny-secp256k1':'2.2.4'},
  controls:['Published30-character and Python scalar-one five-construction vectors','Synthetic26 Node/Python exact ordered address agreement','Synthetic frozen result/witness/single nominal=strict input guards','ActualGitcommit/current-byte/containment/private modes','Mock exactly10 attempts, concurrency2, no retries, exact200 policy, malformed/failed statistics','Explicit public allowlist omits raw value, fingerprint and address association'],
  publication:'Root verifies a separate public registration before target input, target scalar/address derivation or live requests. Fixed localGitcommit/current-byte checks are mandatory. Frozen historical scripts stay unchanged.',walletImports:0,transactions:0,
  limitations:['This is one weak8bit checksum lead, not creator intent or a solved puzzle.','The lead depends on a registered whitespace-compacted saved form; no unmodified original reading contains it contiguously and no printed key is demonstrated.','Strict-known refers to the declared source/projection flags, not fresh pixel proof or full physical-source certification.','Zero history would exclude only these five mainnet constructions according to two explorer operators at recorded times; other constructions/future funding remain outside scope.','No authenticated prize address is known; activity alone does not establish ownership or20BTC.','Python arithmetic is variable-time and memory clearing is best effort; raw scalar material is never persisted or used as an identifier.']};
}
function mockFrozen(){
 const cohorts=COHORTS.map(id=>({id,common:{validCounts:{address:0}},minikey26:{validCount:id==='issue27-body-stride12'?1:0}}));
 Object.assign(cohorts[2],{recordCount:72,formCount:96,strictKnown:{recordCount:60,formCount:78,nestedInNominal:true,physicalSourceComplete:false,minikey26:{validCount:1,checksumCalls:0,status:'derived-from-nominal-validation'}}});
 return {version:1,testId:'columns-fixed-output-compatibility',registrationCommit:'d95986156cd785c3836ad060fdcaeabdebabcb01',protocolSha256:'7e7868d2fa93110cced1ab8f6f8ff5e71c2235aabdc662f558ffcbf90f504cc5',scopeComplete:true,compatibilityGatesComplete:true,allOriginalArtifactIdentitiesVerified:true,privateReviewRequired:true,newSelectorIntroduced:false,ocrRerun:false,sourceRepairs:false,semanticReviewPerformed:false,privateArtifactIntegrity:{'VALIDATION.private.json':VALIDATION_SHA},counts:{sumNominalValidRecords:1},cohorts};
}
function mockWitness(){return {version:1,status:'PASS-scoped-saved-form-association',registrationCommit:'d95986156cd785c3836ad060fdcaeabdebabcb01',protocolSha256:'7e7868d2fa93110cced1ab8f6f8ff5e71c2235aabdc662f558ffcbf90f504cc5',primaryResultSha256:RESULT_SHA,privateValidationArtifactSha256:VALIDATION_SHA,privateFormsArtifactSha256:FORMS_SHA,cohort:'issue27-body-stride12',checks:{literal26SBase58Syntax:true,nominalEqualsCachedStrictPositive:true,presentInSavedStrictKnownCompactedForm:true,contiguousInAnyUnmodifiedOriginalReading:false,compactionRegeneratedByReviewer:false,newGlyphMappingPerformed:false},sourceKnownScope:{nominalReadings:72,strictKnownReadings:60,strictKnownForms:78,nestedSubset:true,physicalSourceComplete:false},activity:{derivations:0,network:0}};}
async function selfTest(){
 const {audit,classifier}=frozenHelpers();let checks=0,rejects=0;
 function reject(fn){assert.throws(fn);rejects++;}
 const independent=python(['--self-test']);assert.equal(independent.status,'PASS');assert.equal(independent.targetInputRead,false);checks++;
 const published='S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy';
 const expected=['1CciesT23BNionJeXrbxmjc7ywfiyM4oLW','1PZuicD1ACRfBuKEgp2XaJhVvnwpeETDyn','3FJeDuA15H3LZuYR4E4MikQDKjTxy6DjFS','bc1q77xpty0n7d8arl3nnhphzp5m0dyjhumsv7usuc','bc1ptrn8c2fuy92nczpejtjlwpj7h73hgftkjshhmuqdch0hr943mg8sykpkcx'];
 assert.deepEqual(audit.deriveAddresses(published).map(a=>a.address),expected);checks++;
 const alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';let sample=null;
 for(let n=0;n<65536;n++){let x=n,suffix='';do{suffix=alphabet[x%58]+suffix;x=Math.floor(x/58);}while(x);const c='S'+'2'.repeat(19)+suffix.padStart(6,'2');if(audit.checkMinikey(c).formatValid){sample=c;break;}}
 assert.ok(sample&&sample.length===26);checks++;
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'key404-stride26-control-'));fs.chmodSync(dir,0o700);
 try{
  const lead=path.join(dir,'CONTROL.private.json'),output=path.join(dir,'CONTROL_ADDRESSES.private.json');writePrivate(lead,{format:'minikey',value:sample});python(['--lead',lead,'--out',output]);
  assert.deepEqual(audit.deriveAddresses(sample),JSON.parse(readCapped(output,65536)).addresses);checks++;
  assert.equal(fs.statSync(lead).mode&0o777,0o600);assert.equal(fs.statSync(output).mode&0o777,0o600);checks++;
  reject(()=>privatePath(path.join(SITE,'dist','private-control'),true));reject(()=>privatePath(path.join(dir,'public','control')));
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
 const record={format:'minikey',length:26,checkBits:8,private:true,fingerprint:classifier.fingerprint(sample),value:sample};
 const bundle={schemaVersion:1,testId:'columns-fixed-output-compatibility',cohorts:COHORTS.map(id=>({id,evaluationAll:{rawPositives:[],minikey26Positives:id==='issue27-body-stride12'?[{...record}]:[],minikey26:{validCount:id==='issue27-body-stride12'?1:0}},evaluationStrictKnown:id==='issue27-body-stride12'?{rawPositives:[],minikey26Positives:[{...record}],minikey26:{validCount:1}}:null}))};
 assert.equal(selectSingle(bundle,audit,classifier),sample);checks++;
 for(const change of [b=>b.schemaVersion=2,b=>b.cohorts[2].evaluationStrictKnown.minikey26Positives=[],b=>b.cohorts[0].evaluationAll.minikey26Positives=[{...record}],b=>b.cohorts[2].evaluationAll.rawPositives=[{format:'address'}],b=>{b.cohorts[2].evaluationAll.minikey26Positives[0].fingerprint='0'.repeat(64);b.cohorts[2].evaluationStrictKnown.minikey26Positives[0].fingerprint='0'.repeat(64);},b=>b.cohorts[2].evaluationStrictKnown.minikey26.validCount=0]){const bad=structuredClone(bundle);change(bad);reject(()=>selectSingle(bad,audit,classifier));}
 const frozen=mockFrozen();validateFrozenResult(frozen);checks++;
 for(const change of [r=>r.scopeComplete=false,r=>r.counts.sumNominalValidRecords=2,r=>r.cohorts[0].minikey26.validCount=1,r=>r.cohorts[2].strictKnown.physicalSourceComplete=true,r=>r.privateArtifactIntegrity['VALIDATION.private.json']='0'.repeat(64),r=>r.cohorts[2].strictKnown.minikey26.validCount=0]){const bad=structuredClone(frozen);change(bad);reject(()=>validateFrozenResult(bad));}
 const witness=mockWitness();validateSourceWitness(witness);checks++;
 for(const change of [w=>w.status='other',w=>w.checks.contiguousInAnyUnmodifiedOriginalReading=true,w=>w.checks.presentInSavedStrictKnownCompactedForm=false,w=>w.sourceKnownScope.physicalSourceComplete=true,w=>w.privateValidationArtifactSha256='0'.repeat(64),w=>w.activity.network=1]){const bad=structuredClone(witness);change(bad);reject(()=>validateSourceWitness(bad));}
 const p=protocolTemplate();validateProtocolHeader(p,'0'.repeat(40));checks++;
 for(const change of [p=>p.requestsMaximum=11,p=>p.concurrencyMaximum=3,p=>p.retries=1,p=>p.httpStatusRequired=201,p=>p.candidateFingerprint='0'.repeat(64),p=>p.sourceHashes[SOURCE_WITNESS]='0'.repeat(64),p=>p.scriptHashes[PY_CORE]='0'.repeat(64),p=>p.sourceSurface.requiresWhitespaceCompaction=false]){const bad=structuredClone(p);change(bad);reject(()=>validateProtocolHeader(bad,'0'.repeat(40)));}
 reject(()=>validateProtocolHeader(p,'main'));
 const rawfiles=Object.fromEntries(Object.keys({...p.sourceHashes,...p.scriptHashes}).map(f=>[f,Buffer.from('source-free-control:'+f)]));const fake={sourceHashes:{},scriptHashes:{}};
 for(const f of Object.keys(p.sourceHashes))fake.sourceHashes[f]=hash(rawfiles[f]);for(const f of Object.keys(p.scriptHashes))fake.scriptHashes[f]=hash(rawfiles[f]);
 const pb=Buffer.from('control protocol');rawfiles[PROTOCOL]=pb;let reads=0;
 const blob=(reg,f)=>rawfiles[f],current=f=>{reads++;return rawfiles[f];};verifyRegistered(fake,pb,'0'.repeat(40),current,blob);assert.equal(reads,7);checks++;
 reads=0;reject(()=>verifyRegistered(fake,Buffer.from('changed'),'0'.repeat(40),current,blob));assert.equal(reads,0);checks++;
 reject(()=>verifyRegistered(fake,pb,'0'.repeat(40),f=>Buffer.concat([rawfiles[f],Buffer.from('changed')]),blob));
 const zeros={funded_txo_count:0,funded_txo_sum:0,spent_txo_count:0,spent_txo_sum:0,tx_count:0};
 const controlAddresses=TYPES.map((type,i)=>({type,address:'CONTROL-'+i}));let active=0,maxActive=0,mockCalls=0;
 function fetcher(statusFirst=200,malformed=false){return async(url,options)=>{const ordinal=++mockCalls;active++;maxActive=Math.max(maxActive,active);assert.equal(options.redirect,'error');assert.equal(options.cache,'no-store');await new Promise(r=>setImmediate(r));active--;const status=ordinal===1?statusFirst:200;return {ok:status>=200&&status<300,status,text:async()=>malformed?'bad-json':JSON.stringify({address:decodeURIComponent(url.split('/').pop()),chain_stats:{...zeros},mempool_stats:{...zeros}})};};}
 const allZero=await queryFive(controlAddresses,audit,fetcher());assert.equal(allZero.counters.requestsAttempted,10);assert.equal(mockCalls,10);assert.equal(maxActive,2);assert.equal(classifier.classify(allZero.results).outcome,'zero-history-in-scope');checks++;
 mockCalls=0;const non200=await queryFive(controlAddresses,audit,fetcher(206));assert.equal(mockCalls,10);assert.equal(classifier.classify(non200.results).outcome,'inconclusive');checks++;
 for(const mode of ['http','malformed','wrong-address','negative','inconsistent-zero','timeout']){
  let calls=0;const counters={requestsAttempted:0};const result=await audit.requestStats('blockstream','CONTROL',counters,async()=>{calls++;if(mode==='timeout'){const e=new Error('mock');e.name='AbortError';throw e;}const part={...zeros};if(mode==='negative')part.funded_txo_sum=-1;if(mode==='inconsistent-zero')part.funded_txo_sum=1;return {ok:mode!=='http',status:mode==='http'?500:200,text:async()=>mode==='malformed'?'bad-json':JSON.stringify({address:mode==='wrong-address'?'WRONG':'CONTROL',chain_stats:part,mempool_stats:{...zeros}})};});assert.equal(result.status,'error');assert.equal(calls,1);assert.equal(counters.requestsAttempted,1);checks++;
 }
 const invalid=structuredClone(allZero.results);invalid[1].statistics.chain_stats.tx_count=-1;assert.equal(classifier.classify(invalid).outcome,'inconclusive');checks++;
 const mismatch=structuredClone(allZero.results);mismatch[0].provider='mempool';assert.equal(classifier.classify(mismatch).outcome,'inconclusive');checks++;
 const activity=structuredClone(allZero.results);activity[0].statistics.chain_stats={...zeros,tx_count:1,funded_txo_count:1,funded_txo_sum:1};activity[0].activity=true;assert.equal(classifier.classify(activity).outcome,'activity-detected-private-review');checks++;
 const safe=safeResult(p,'0'.repeat(64),'0'.repeat(40),'control',allZero.results,allZero.counters,{passed:true,targetInputRead:false},classifier);const serialized=JSON.stringify(safe);
 assert.ok(!serialized.includes(sample)&&!serialized.includes(record.fingerprint)&&!serialized.includes('CONTROL-')&&!Object.hasOwn(safe,'candidateFingerprint'));checks++;
 assert.ok(!serialized.includes('address":"')&&!serialized.includes('LEAD.private'));checks++;
 return {passed:true,checksPassed:checks,rejectedGuards:rejects,independentPythonChecks:independent.checksPassed,controlAddressSets:2,synthetic26NodePythonAgreement:true,mockRequestsAttempted:10,mockConcurrencyMaximum:2,non200PolicyTested:true,targetInputRead:false,targetDerivations:0,liveRequests:0,walletImports:0,transactions:0};
}
module.exports={protocolTemplate,validateFrozenResult,validateSourceWitness,validateProtocolHeader,verifyRegistered,selectSingle,queryFive,safeResult,selfTest};
if(require.main===module)main(process.argv.slice(2)).catch(()=>{console.error('Follow-up failed before a conclusive result; inspect private files locally.');process.exitCode=1;});
