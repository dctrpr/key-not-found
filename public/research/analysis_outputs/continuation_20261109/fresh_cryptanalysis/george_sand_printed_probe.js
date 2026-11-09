const fs=require('fs');
const crypto=require('crypto');
const bip39=require('bip39');
const wif=require('wif');
const OUT=__dirname;
const model=JSON.parse(fs.readFileSync(`${OUT}/printed_lines.json`,'utf8'));
const b39=new Set(bip39.wordlists.english);
function tokens(s){return s.split(/\s+/).map(t=>t.replace(/^[^A-Za-z0-9$]+|[^A-Za-z0-9]+$/g,'')).filter(t=>/[A-Za-z0-9]/.test(t));}
function displayRows(section){return model.optional_display_rows.filter(r=>r.section===section).map((r,i)=>({...r,id:`p${r.page}_${section}_${i}`,highlighted_printed_row:false,annotation_bold_any:false,annotation_bold_all:false}));}
function frame({title=false,graphic=false,signature=false}={}){
 const a=[];
 for(let p=75;p<=79;p++){
  if(title)a.push(...displayRows('title').filter(r=>r.page===p));
  a.push(...model.rows.filter(r=>r.page===p));
  if(graphic)a.push(...displayRows('graphic').filter(r=>r.page===p));
  if(signature)a.push(...displayRows('signature').filter(r=>r.page===p));
 }
 return a;
}
const frames={body:frame(),with_title:frame({title:true}),with_graphic:frame({graphic:true}),with_displays:frame({title:true,graphic:true,signature:true})};
const keep={all:r=>true,highlighted:r=>r.highlighted_printed_row,any_bold_annotation:r=>r.annotation_bold_any,bold_or_highlight:r=>r.annotation_bold_any||r.highlighted_printed_row,all_bold_annotation:r=>r.annotation_bold_all};
const candidates=new Map(),variants=[];
function add(s,meta){
 const key=crypto.createHash('sha256').update(s).digest('hex');
 if(!candidates.has(key))candidates.set(key,{sha256:key,text:s,variants:[]});
 candidates.get(key).variants.push(meta);variants.push(meta);
}
for(const [frameName,fr] of Object.entries(frames))for(const direction of ['down','up']){
 const ordered=direction==='down'?[...fr]:[...fr].reverse();
 for(const [subset,pred] of Object.entries(keep))for(const parityBase of ['all_printed_rows','eligible_rows'])for(const reset of ['global','page','paragraph'])for(const phase of ['all','odd','even']){
  const counters=new Map();const selected=[];
  for(const r of ordered){
   const k=reset==='global'?'all':reset==='page'?String(r.page):`${r.page}/${r.section}/${r.paragraph}`;
   const eligible=pred(r);
   let n=counters.get(k)||0;
   if(parityBase==='all_printed_rows'||eligible){n++;counters.set(k,n);}
   if(eligible&&(phase==='all'||(phase==='odd'&&n%2===1)||(phase==='even'&&n%2===0)))selected.push(r);
  }
  const words=selected.map(r=>tokens(r.text));
  const first=words.map(ws=>ws[0]||'');const last=words.map(ws=>ws.at(-1)||'');
  const projections={
   complete_lines:selected.map(r=>r.text).join('\n'),
   first_words:first.join(' '),last_words:last.join(' '),
   first_word_initials:first.map(w=>w[0]||'').join(''),
   first_word_finals:first.map(w=>w.at(-1)||'').join(''),
   last_word_initials:last.map(w=>w[0]||'').join(''),
   last_word_finals:last.map(w=>w.at(-1)||'').join(''),
  };
  for(const [projection,text] of Object.entries(projections)){
   const common={frame:frameName,direction,subset,parityBase,reset,phase,projection,selectedRows:selected.map(r=>r.id)};
   add(text,{...common,textDirection:'normal'});
   add([...text].reverse().join(''),{...common,textDirection:'character_reverse'});
  }
 }
}
const hits=[];const testedWif=new Set(),testedMnemonics=new Set(),testedMini=new Set();
let wifWindowOccurrences=0,hexWindowOccurrences=0,mnemonicWindowOccurrences=0,miniOccurrences=0;
for(const c of candidates.values()){
 for(const [form,s] of Object.entries({as_text:c.text,compact:c.text.replace(/\s/g,'')})){
  for(const size of [51,52])for(let i=0;i+size<=s.length;i++){
   const v=s.slice(i,i+size);if(!/^[5KL][1-9A-HJ-NP-Za-km-z]+$/.test(v))continue;
   wifWindowOccurrences++;testedWif.add(v);
   try{const d=wif.decode(v);if(d.version===128)hits.push({type:'WIF',candidateSha256:c.sha256,form,offset:i,value:v});}catch{}
  }
  for(const m of s.matchAll(/(?:^|[^0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])/g)){
   hexWindowOccurrences++;hits.push({type:'hex64',candidateSha256:c.sha256,form,offset:m.index,value:m[1]});
  }
  if(form==='compact'&&/^S[1-9A-HJ-NP-Za-km-z]{21}$|^S[1-9A-HJ-NP-Za-km-z]{29}$/.test(s)){
   miniOccurrences++;testedMini.add(s);if(crypto.createHash('sha256').update(`${s}?`).digest()[0]===0)hits.push({type:'minikey_weak_checksum',candidateSha256:c.sha256,form,value:s});
  }
 }
 const words=c.text.toLowerCase().match(/[a-z]+/g)||[];
 for(const n of [12,15,18,21,24])for(let i=0;i+n<=words.length;i++){
  const ws=words.slice(i,i+n);if(!ws.every(w=>b39.has(w)))continue;
  const v=ws.join(' ');mnemonicWindowOccurrences++;testedMnemonics.add(v);
  if(bip39.validateMnemonic(v))hits.push({type:'BIP39',candidateSha256:c.sha256,offset:i,value:v});
 }
}
const result={date:'2026-11-09',basis:'George Sand clue linked by Max Keiser December26 2022; CipherMysteries article explicitly shows alternate complete printed lines and first word of each printed line.',sourceModel:'printed_lines.json',sourceModelSha256:crypto.createHash('sha256').update(fs.readFileSync(`${OUT}/printed_lines.json`)).digest('hex'),
 scope:'Offline direct encodings only; no candidate private-key hashing, chain queries or wallet actions. Last-word, upward and character-reverse variants implement bounded mirror counterparts. Subset/font/display/parity reset variants are hypotheses, not instructions stated in the clue.',
 variantCount:variants.length,uniqueTextCount:candidates.size,wifWindowOccurrences,uniqueWifWindows:testedWif.size,hexWindowOccurrences,mnemonicWindowOccurrences,uniqueMnemonicWindows:testedMnemonics.size,miniOccurrences,uniqueMiniKeys:testedMini.size,hits,
 candidates:[...candidates.values()],limitations:model.limitations};
fs.writeFileSync(`${OUT}/george_sand_printed_probe.json`,JSON.stringify(result,null,2)+'\n');
const md=['# Actual printed-line George Sand probe','',`Body rows: ${Object.entries(model.counts).map(([p,n])=>`${p}: ${n}`).join('; ')}. Total142.`, '',`Variants ${result.variantCount}; unique text streams ${result.uniqueTextCount}; WIF-shaped windows ${result.wifWindowOccurrences} (${result.uniqueWifWindows} unique); 64-hex windows ${result.hexWindowOccurrences}; all-BIP39word windows ${result.mnemonicWindowOccurrences}; checksum hits ${hits.length}.`,'','## Direct first/last words by page',''];
for(let p=75;p<=79;p++){
 const rs=model.rows.filter(r=>r.page===p);
 md.push(`### Page${p}`,'',`First words: ${rs.map(r=>r.first_word).join(' ')}`,'',`Last words: ${rs.map(r=>r.last_word).join(' ')}`,'',`First-word initials: ${rs.map(r=>r.first_word[0]).join('')}`,'');
}
md.push('## Whole-body alternating-line readings','','The following literal odd/even printed-line readings keep page parity continuous. Other page/paragraph reset variants and mirrored readings are preserved in the JSON.','');
for(const phase of ['odd','even']){
 const selected=model.rows.filter((r,i)=>phase==='odd'?i%2===0:i%2===1);
 md.push(`### ${phase} lines`,'','```text',...selected.map(r=>r.text),'```','');
}
md.push('## Limits','',...model.limitations.map(s=>`- ${s}`),'','No solution is claimed. All literal clue-backed readings and additional bounded hypotheses are kept distinguishable in candidate metadata.','');
fs.writeFileSync(`${OUT}/george_sand_printed_probe.md`,md.join('\n'));
console.log(JSON.stringify(Object.fromEntries(Object.entries(result).filter(([k])=>!['candidates','limitations'].includes(k))),null,2));
