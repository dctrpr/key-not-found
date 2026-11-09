const fs = require('fs');
const crypto = require('crypto');
const bip39 = require('bip39');
const ROOT = process.cwd();
const OUT = `${ROOT}/analysis_outputs/continuation_20261109/fresh_cryptanalysis`;
const canonical = JSON.parse(fs.readFileSync(`${ROOT}/analysis_outputs/3d_article_map/canonical_char_model.json`, 'utf8'));
const wordset = new Set(bip39.wordlists.english);
const sources = {
  full_article_corrected: fs.readFileSync(`${ROOT}/full_article_corrected.txt`, 'utf8'),
  canonical_whole: Object.values(canonical.pages).map(p=>p.plain).join('\n'),
};
for (const p of Object.values(canonical.pages)) sources[`canonical_p${p.articlePage}`]=p.plain;
const runs=[];
const rev=s=>[...s].reverse().join('');
function transform(s, mode) {
 const lines=s.split(/\r?\n/).map(l=>l.trim()).filter(Boolean);
 switch(mode){
  case 'normal': return lines.join('\n');
  case 'mirror_each_line': return lines.map(rev).join('\n');
  case 'bottom_to_top': return lines.reverse().join('\n');
  case 'whole_reverse': return rev(lines.join('\n'));
  case 'reverse_word_order_each_line': return lines.map(l=>l.split(/\s+/).reverse().join(' ')).join('\n');
  case 'reverse_each_word': return lines.map(l=>l.split(/\s+/).map(rev).join(' ')).join('\n');
  case 'boustrophedon_even': return lines.map((l,i)=>i%2?rev(l):l).join('\n');
  case 'boustrophedon_odd': return lines.map((l,i)=>i%2?l:rev(l)).join('\n');
  case 'boustrophedon_even_up': return lines.reverse().map((l,i)=>i%2?rev(l):l).join('\n');
  case 'boustrophedon_odd_up': return lines.reverse().map((l,i)=>i%2?l:rev(l)).join('\n');
 }
}
const BASE58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
function b58decode(s){ let n=0n;for(const c of s){const i=BASE58.indexOf(c);if(i<0)return null;n=n*58n+BigInt(i);}let h=n.toString(16);if(h.length%2)h='0'+h;let b=n?Buffer.from(h,'hex'):Buffer.alloc(0);let z=0;while(s[z]==='1')z++;return Buffer.concat([Buffer.alloc(z),b]); }
function sha(b){return crypto.createHash('sha256').update(b).digest();}
function validWif(s){const b=b58decode(s);if(!b||![37,38].includes(b.length)||b[0]!==128)return false;const d=b.subarray(0,-4);return sha(sha(d)).subarray(0,4).equals(b.subarray(-4))&&(b.length===37||b[33]===1);}
const hits=[]; let wifChecks=0, hexChecks=0,mnemonicChecks=0;
for(const [source,original] of Object.entries(sources)){
 for(const mode of ['normal','mirror_each_line','bottom_to_top','whole_reverse','reverse_word_order_each_line','reverse_each_word','boustrophedon_even','boustrophedon_odd','boustrophedon_even_up','boustrophedon_odd_up']){
  const t=transform(original,mode);const lines=t.split('\n');const words=t.match(/[A-Za-z]+(?:['’][A-Za-z]+)*/g)||[];
  const projections={
   text:t,
   remove_whitespace:t.replace(/\s/g,''),
   letters:t.replace(/[^A-Za-z]/g,''),
   alphanumeric:t.replace(/[^A-Za-z0-9]/g,''),
   word_initials:words.map(x=>x[0]).join(''),
   word_finals:words.map(x=>x.at(-1)).join(''),
   line_initials:lines.map(x=>(x.match(/[A-Za-z0-9]/)||[''])[0]).join(''),
   line_finals:lines.map(x=>(x.match(/[A-Za-z0-9](?=[^A-Za-z0-9]*$)/)||[''])[0]).join(''),
   first_word_each_line:lines.map(x=>(x.match(/[A-Za-z]+/g)||[''])[0]).join(' '),
   last_word_each_line:lines.map(x=>(x.match(/[A-Za-z]+/g)||['']).at(-1)).join(' '),
  };
  for(const [projection,s] of Object.entries(projections)){
   const before=hits.length;
   for(const n of [51,52])for(let i=0;i+n<=s.length;i++){const v=s.slice(i,i+n);if(!/^[5KL][1-9A-HJ-NP-Za-km-z]+$/.test(v))continue;wifChecks++;if(validWif(v))hits.push({source,mode,projection,type:'WIF',offset:i,value:v});}
   for(const m of s.matchAll(/(?:^|[^0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])/g)){hexChecks++;hits.push({source,mode,projection,type:'hex64',offset:m.index,value:m[1]});}
   const ws=s.toLowerCase().match(/[a-z]+/g)||[];
   for(const n of [12,15,18,21,24])for(let i=0;i+n<=ws.length;i++){const w=ws.slice(i,i+n);if(!w.every(x=>wordset.has(x)))continue;mnemonicChecks++;const v=w.join(' ');if(bip39.validateMnemonic(v))hits.push({source,mode,projection,type:'BIP39',offset:i,value:v});}
   runs.push({source,mode,projection,characters:s.length,hits:hits.length-before});
  }
 }
}
const partial={};const letterCounts={};
for(const p of Object.values(canonical.pages)){
 let allChars=0,alnum=0,letters=0,positions=0,partialWords=0;
 for(const w of p.words.filter(w=>w.partialBold)){
  partialWords++;
  for(const c of p.chars.slice(w.start,w.end)){
   if(/[A-Za-z]/.test(c.c)){
    positions++; const k=c.c.toLowerCase();letterCounts[k]??={regular:0,bold:0};letterCounts[k][c.bold?'bold':'regular']++;
   }
   if(c.bold){allChars++;if(/[A-Za-z0-9]/.test(c.c))alnum++;if(/[A-Za-z]/.test(c.c))letters++;}
  }
 }
 partial[p.articlePage]={partialWords,letterPositions:positions,boldLetters:letters,boldAlphanumeric:alnum,boldCharacters:allChars};
}
const counts=Object.values(partial).reduce((a,v)=>{for(const k of Object.keys(v))a[k]=(a[k]||0)+v[k];return a;},{});
const report={date:'2026-11-09',scope:'Offline literal mirror/transposition and direct checksum checks only. No hashing into candidate private keys, no network queries, no transactions.',sources:Object.fromEntries(Object.entries(sources).map(([k,s])=>[k,{characters:s.length,sha256:crypto.createHash('sha256').update(s).digest('hex')}])),runs:runs.length,wifChecks,hexChecks,mnemonicChecks,hits,partialBoldCounts:partial,partialBoldTotal:counts,partialBoldLetterContingency:letterCounts,limitations:['Canonical line breaks were supplied by an investigator and sometimes merge printed lines. This is a bounded textual test, not a faithful physical page mirror.','Partial-bold labels are investigator annotations. Letter dependence is consistent with Typeka Mix glyph behavior, but cannot alone prove no hidden message exists.','A valid BIP39 checksum alone is weak evidence, approximately one in sixteen for arbitrary twelve-word sequences. No checksum match is a claim of solving or funds.']};
fs.writeFileSync(`${OUT}/transcript_mirror_probe.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({runs:report.runs,wifChecks,hexChecks,mnemonicChecks,hits,partialBoldTotal:counts},null,2));
