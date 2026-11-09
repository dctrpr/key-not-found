const bip39 = require('../src/utils/bip39');

const channels = {
  orange: [
    'they are the sum of',
    'all our neuroses',
    'layer 1',
    'fact',
    "it's layer 1 for every great thing",
    "that's ever been invented or discovered",
    'maximalist',
    'keep your dignity',
    'layer 1',
    'get some toxicity get some bitcoin open your heart to',
    'bitcoin',
    'by the rancid catnip of fiat money',
    'buying the dip',
    'shitcoiner at heart',
    'toxic bitcoin maximalists within six months',
    'harass old women and children',
    "the numbers don't lie",
    'america left 85',
    'billion worth of hate toys in afghanistan',
    '2 trillion fiat cuck bucks',
    'the game theorized bitcoin protocol',
    'infinitely more efficient',
    'to transact and store wealth in than fiat shitcoins',
    'or gold',
    "that's right bitcoin will take",
    'all the energy',
    'everyone will live their own experience in the rabbit hole',
    'we are getting our souls back and our minds',
  ],
  inverted: [
    'money printers banking terrorists stock traders central bank arsonists',
    "don't fall for shitcoinery",
    'gotta be this way forty years of dumb post 1971 fiat money nonsense',
    "it's a stun gun to the genitals",
    '1 billion',
    'volcano bonds',
    'sorry bhutan you fell for that snake oil salesmen over at xrp get ready to experience shitcoin hell',
    'shitcoiners useless royals',
    'it does this by monetizing',
    'gargantuanly wasteful',
    'money printing',
    'wars to keep it going',
    'war and violence',
    'economy',
  ],
};

function words(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean);
}

function bipWords(list) {
  return list.filter((word) => bip39.isBIP39Word(word));
}

function groupWord(groups, mode) {
  return groups
    .map((group) => {
      const filtered = bipWords(words(group));
      if (filtered.length === 0) return null;
      if (mode === 'first') return filtered[0];
      if (mode === 'last') return filtered[filtered.length - 1];
      if (mode === 'middle') return filtered[Math.floor(filtered.length / 2)];
      return null;
    })
    .filter(Boolean);
}

function interleave(a, b) {
  const out = [];
  const len = Math.max(a.length, b.length);
  for (let i = 0; i < len; i++) {
    if (i < a.length) out.push(a[i]);
    if (i < b.length) out.push(b[i]);
  }
  return out;
}

function candidateSequences() {
  const seqs = [];
  for (const [name, groups] of Object.entries(channels)) {
    const flattened = bipWords(words(groups.join(' ')));
    seqs.push([`${name}:all-bip39`, flattened]);
    seqs.push([`${name}:first-bip39-per-group`, groupWord(groups, 'first')]);
    seqs.push([`${name}:last-bip39-per-group`, groupWord(groups, 'last')]);
    seqs.push([`${name}:middle-bip39-per-group`, groupWord(groups, 'middle')]);
  }

  for (const mode of ['first', 'last', 'middle']) {
    seqs.push([
      `combined:${mode}-orange-then-inverted`,
      groupWord(channels.orange, mode).concat(groupWord(channels.inverted, mode)),
    ]);
    seqs.push([
      `combined:${mode}-inverted-then-orange`,
      groupWord(channels.inverted, mode).concat(groupWord(channels.orange, mode)),
    ]);
    seqs.push([
      `combined:${mode}-interleaved`,
      interleave(groupWord(channels.orange, mode), groupWord(channels.inverted, mode)),
    ]);
  }

  const orangeAll = bipWords(words(channels.orange.join(' ')));
  const invertedAll = bipWords(words(channels.inverted.join(' ')));
  seqs.push(['combined:all-orange-then-inverted', orangeAll.concat(invertedAll)]);
  seqs.push(['combined:all-inverted-then-orange', invertedAll.concat(orangeAll)]);
  seqs.push(['combined:all-interleaved', interleave(orangeAll, invertedAll)]);

  return seqs.flatMap(([name, seq]) => [
    [name, seq],
    [`${name}:reverse`, [...seq].reverse()],
  ]);
}

function* variants(seq) {
  const validLengths = [12, 15, 18, 21, 24];
  for (const len of validLengths) {
    if (seq.length === len) yield { words: seq, edit: 'exact' };
    for (let start = 0; start <= seq.length - len; start++) {
      yield { words: seq.slice(start, start + len), edit: `window-${start}-${len}` };
    }
  }

  // A common puzzle error mode is one extra non-seed signal word in a 13-token clue.
  for (let start = 0; start <= seq.length - 13; start++) {
    const window = seq.slice(start, start + 13);
    for (let drop = 0; drop < window.length; drop++) {
      yield {
        words: window.filter((_, index) => index !== drop),
        edit: `window-${start}-13-drop-${drop}:${window[drop]}`,
      };
    }
  }
}

function main() {
  const jsonOnly = process.argv.includes('--json');
  const seen = new Set();
  const hits = [];

  for (const [name, seq] of candidateSequences()) {
    if (!jsonOnly) {
      console.log(`${name.padEnd(42)} ${seq.length.toString().padStart(3)}  ${seq.join(' ')}`);
    }
    for (const variant of variants(seq)) {
      const phrase = variant.words.join(' ');
      if (seen.has(phrase)) continue;
      seen.add(phrase);

      const result = bip39.validateMnemonic(variant.words);
      if (result.valid) {
        hits.push({ source: name, edit: variant.edit, phrase });
      }
    }
  }

  if (jsonOnly) {
    console.log(JSON.stringify(hits, null, 2));
    return;
  }

  console.log(`\nValid BIP39 candidates: ${hits.length}`);
  for (const hit of hits) {
    console.log(`\n[${hit.source}] ${hit.edit}`);
    console.log(hit.phrase);
  }
}

main();
