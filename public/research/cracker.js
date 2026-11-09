const fs = require('fs');

// The full text provided by the user
const rawText = `Get some toxicity. Get some bitcoin. Open your heart to
Bitcoin. It's the freaking UTXO ghetto up in here, y'all.
It's funkier than a whole parallel universe full of nothing
but George Clinton and James Brown clones. It's Martin Luther
nailing the Vatican with ultimatums. It's the sound of skin being
ripped off live central bankers tied to a burning stake.
Gotta be this way. Forty years of dumb post-1971 fiat money
nonsense (and 10years of watching Peter Schiff miss buying bitcoin
since I started honey-badgering him to buy some at $1 back in 2011)
have dulled shitcoiners' and nocoiners' minds.
The collective unconscious, controlled now by psychotic
cats, plays "Friends" reruns all day in our heads.
Our imaginations and inventiveness have been euthanized
by the rancid catnip of fiat money. Fortunately, bitcoin
puts an end to the paper chase Manhattan Bank money
laundering lobotomy. It's a stun gun to the genitals.
A monetary defibrillator to the treasure chest.
Don't believe me?
Have you seen the president of El Salvador
trolling the International Monetary Fund (IMF) on Twitter?
He's taunting them, telling them he's "buying the dip."
I tweeted President Nayib Bukele when he announced
he was going to tap his nation's volcanoes to mine
$1 billion in bitcoin - that he should sell
billions worth of future bitcoin earnings
collateralized "Volcano Bonds" to pay off the IMF
loan and get rid of those leeches. I tagged Mike
Novogratz in the tweet, figuring he could sell a
bunch to his Wall Street crony pals, but so far he
hasn't moved on it. I don't really trust that guy.
Maybe because he's a shitcoiner at heart.
Meanwhile, back in El Salvador, 42% of the country
is now hyperbitcoinized (at the time of writing).
Jack Mallers' Strike app has gone from 20,000 new sign-ups
a day to a mind-bending 100,000 and growing. At this rate, the whole
country will be Toxic Bitcoin Maximalists within six months.
(Sorry Bhutan, you fell for that snake oil salesmen over
at XRP.          Get ready to experience shitcoin hell.
Has anyone heard from Roger Ver lately?
Big blockers got their heads ripped off during the Block
Size War of 2017 and it's been going downhill ever since.
Particularly for Faketoshi and his army of high-priced
London legal hacks who harass old women and children
(and Peter McCormack) for no other reason than the U.K.'s
legal system favors and protects demented shitcoiners,
useless Royals, career criminals and banksters.
London is a scammer paradise. Full Stop.
EVERY SINGLE ONE OF
THE BITCOIN WANNABES - BCH, BSV, ETH, XRP,
ADA, AND 12,000 OTHER SHITCOINS, PLUS FIAT
MONEY AND GOLD - IS FACING THE IGNOMINIOUS
FATE OF DEMONETIZATION VERSUS BITCOIN.
It's a guaranteed, mathematical certainty. Let me explain
why, and this might be the first time you're hearing this,
Bitcoin was designed to be a 51% attack on the world's
energy supply. Shitcoins, fiat and gold will
starve to death as the result of Bitcoin's
insatiable conquest of all available energy.
And as bitcoin starves shitcoins, fiat and gold to death,
it simultaneously demonetizes war, violence, hatred and
the state itself. It does this by monetizing, for the first
time in human history, peace, love and understanding
(Elvis Costello was right).
We've never had an economy and a money
that incentivizes love before until bitcoin.
Love opens up the collective unconscious and
our joint inner cosmic being. The economy of
love is infinitely more efficient than hate and war.
I listen to these eggheads - Michael Saylor, Nic Carter,
Marty Bent -        who spend their days pouring over spreadsheets
and gallons of iced espresso. The numbers don't lie.
The energy industry in its current form is gargantuanly wasteful
and requires money printing and wars to keep it going - all in
the service of an uber class of banksters who profit from war, poverty
and misery with their fiat money Ponzi schemes. America left $85
BILLION worth of hate toys in Afghanistan, for example, for a war
that some estimate cost $2 trillion fiat cuck-bucks.
BITCOIN FIXES ALL THIS by replacing oil-dripping,
corpse-ridden, poppy-harvesting fiat money with perfect bitcoin.
Remove the war incentive, and you remove the hate incentive.
Bitcoin fills the gap with love; our most natural tendency if given a chance.
The warmongers will start mining bitcoin for sure.
It's a fact baked into the game-theorized Bitcoin protocol,
observable by anyone choosing to see it,
right there in the Genesis Block.
To wrap this up, as we move from a war and violence
economy to a peace and love economy, the efficiencies
of love - because bitcoin is infinitely more efficient
to transact and store wealth in than fiat, shitcoins
or gold - the overall energy consumption, even while
Bitcoin makes its 51% attack on global energy supply,
drops by 95% or more. That's right, Bitcoin will take
all the energy. In so doing, our energy consumption
drops to near zero because our natural tendency toward
love and peace gets monetized for the first time in
our existence. Poverty disappears because the fear
of being poor disappears because Bitcoin allows us
to fully express ourselves individually in a cyber
sea of billions of souls all looking to connect and
express love for each other and the cost for this explosion
of peace is the same as a smile - virtually nothing.
Yes, for some, the Bitcoin rabbit hole ends up
in John and Yoko's hotel room in Amsterdam
during their 1969 bed-in.
Everyone will live their own experience in the rabbit hole.
We are getting our souls back and our minds.
Stacy and I have been living in here for 10 years.
We've seen some shit. Happy to share it all with you
- the agony and ecstasy - as Bitcoin conquers fear
and hate and replaces it with peace and love.`;

// --- HELPER FUNCTIONS ---

// Basic Dictionary for scoring "English-ness"
const commonWords = new Set([
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "bitcoin", "key", "private", "wallet", "seed", "code", "satoshi", "block"
]);

function scoreText(text) {
    const words = text.toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/);
    let score = 0;
    let wordCount = 0;
    for (const w of words) {
        if (w.length > 2) {
            wordCount++;
            if (commonWords.has(w)) score += 1;
        }
    }
    return wordCount > 0 ? (score / wordCount) : 0;
}

function isPrivateKeyCandidate(text) {
    // Simple heuristics for now
    // WIF (Wallet Import Format): starts with 5, K, or L, approx 51-52 chars, Base58
    const wifRegex = /\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b/;
    
    // Hex Private Key: 64 chars hex
    const hexRegex = /\b[0-9a-fA-F]{64}\b/;

    // BIP39 Seed phrase (12 or 24 words) - hard to regex perfectly without a wordlist check
    // We will just return true if we find WIF or Hex for now
    if (wifRegex.test(text)) return "POSSIBLE WIF KEY";
    if (hexRegex.test(text)) return "POSSIBLE HEX KEY";
    return null;
}

// --- CIPHER STRATEGIES ---

const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
const words = rawText.split(/\s+/).filter(w => w.length > 0);
const chars = rawText.replace(/\s/g, '');

const strategies = [
    {
        name: "Original Text",
        fn: () => rawText
    },
    {
        name: "George Sand (Lines 1, 3, 5...)",
        fn: () => lines.filter((_, i) => i % 2 === 0).join(' ')
    },
    {
        name: "George Sand Inverse (Lines 2, 4, 6...)",
        fn: () => lines.filter((_, i) => i % 2 !== 0).join(' ')
    },
    {
        name: "First Letter of Each Line (Acrostic)",
        fn: () => lines.map(l => l[0]).join('')
    },
    {
        name: "First Word of Each Line",
        fn: () => lines.map(l => l.split(' ')[0]).join(' ')
    },
    {
        name: "Last Letter of Each Line",
        fn: () => lines.map(l => l[l.length-1]).join('')
    },
    {
        name: "Last Word of Each Line",
        fn: () => lines.map(l => {
             const parts = l.split(' ');
             return parts[parts.length-1];
        }).join(' ')
    },
    {
        name: "Reverse Text (Mirror)",
        fn: () => rawText.split('').reverse().join('')
    },
    {
        name: "Reverse Lines Order",
        fn: () => [...lines].reverse().join('\n')
    },
    {
        name: "Sand + Mirror (Reverse Lines -> Every 2nd)",
        fn: () => [...lines].reverse().filter((_, i) => i % 2 === 0).join(' ')
    },
    {
        name: "Every Nth Character (Skip 2)",
        fn: () => chars.split('').filter((_, i) => i % 2 === 0).join('')
    },
    {
        name: "Every Nth Character (Skip 3)",
        fn: () => chars.split('').filter((_, i) => i % 3 === 0).join('')
    },
    {
        name: "Every Nth Character (Skip 4)",
        fn: () => chars.split('').filter((_, i) => i % 4 === 0).join('')
    },
    {
        name: "Every Nth Word (Skip 2)",
        fn: () => words.filter((_, i) => i % 2 === 0).join(' ')
    },
    {
        name: "Every Nth Word (Skip 3)",
        fn: () => words.filter((_, i) => i % 3 === 0).join(' ')
    },
    {
        name: "Every Nth Word (Skip 5)",
        fn: () => words.filter((_, i) => i % 5 === 0).join(' ')
    },
    {
        name: "Every Nth Word (Skip 7)",
        fn: () => words.filter((_, i) => i % 7 === 0).join(' ')
    },
    {
        name: "Diagonal (Lines shift by 1 char)",
        fn: () => {
            let res = "";
            for(let i=0; i<lines.length; i++) {
                if(i < lines[i].length) res += lines[i][i];
            }
            return res;
        }
    },
    {
        name: "Reverse Diagonal (Lines shift by 1 char from end)",
        fn: () => {
            let res = "";
            for(let i=0; i<lines.length; i++) {
                if(i < lines[i].length) res += lines[i][lines[i].length - 1 - i];
            }
            return res;
        }
    }
];

// --- MAIN EXECUTION ---

console.log("Running Cipher Cracker on Keiser Text...\n");

let potentialKeys = [];
let interestingResults = [];

strategies.forEach(strat => {
    try {
        const result = strat.fn();
        const keyCheck = isPrivateKeyCandidate(result);
        const score = scoreText(result);

        if (keyCheck) {
            potentialKeys.push({ name: strat.name, type: keyCheck, content: result.substring(0, 60) + "..." });
        }
        
        // If it looks somewhat like English or has specific keywords, flag it
        if (score > 0.3 || result.toLowerCase().includes("private key") || result.toLowerCase().includes("satoshi")) {
             interestingResults.push({ name: strat.name, score: score, content: result.substring(0, 100).replace(/\n/g, ' ') + "..." });
        }
    } catch (e) {
        // Ignore errors in strategies
    }
});

console.log("--- POTENTIAL KEYS FOUND ---");
if (potentialKeys.length === 0) console.log("None found directly.");
else console.log(potentialKeys);

console.log("\n--- INTERESTING READABLE TEXT (High 'English' Score) ---");
interestingResults.sort((a,b) => b.score - a.score).slice(0, 5).forEach(r => {
    console.log(`[${r.name}] (Score: ${r.score.toFixed(2)}): ${r.content}`);
});

// Specifically check for 'every Nth word' brute force up to 50
console.log("\n--- BRUTE FORCE Nth WORD CHECK (Looking for hidden phrases) ---");
for (let step = 2; step < 50; step++) {
    let attempt = words.filter((_, i) => i % step === 0).join(' ');
    if (attempt.toLowerCase().includes("bitcoin") || attempt.toLowerCase().includes("key")) {
        console.log(`[Every ${step}th Word]: ${attempt.substring(0, 100)}...`);
    }
}

console.log("\nDone.");


