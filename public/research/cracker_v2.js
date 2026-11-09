const fs = require('fs');

// The full text provided by the user (Same as before)
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

// BIP39 wordlist (short version for checking common ones, full list is 2048 words)
// We can't include the full list easily without a library or large array, 
// so we'll look for strings that *look* like a seed phrase (12 or 24 words).
// A simple heuristic: Are the words all lowercase and alpha-only?

function analyzeSequence(seq) {
    // Check if this sequence of words could be a mnemonic
    // e.g. "witch collapse practice feed shame open despair creek road again ice least"
    // We check if they are 12, 18, or 24 words long and valid looking words.
    if (seq.length !== 12 && seq.length !== 24) return null;
    
    // Check if words are reasonably standard
    const isStandard = seq.every(w => /^[a-z]+$/.test(w) && w.length >= 3);
    if (isStandard) return seq.join(' ');
    return null;
}

const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
const words = rawText.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(w => w.length > 0);

console.log("--- EXTENDED ANALYSIS ---\n");

// 1. First Letter of Every Word
const firstLetters = words.map(w => w[0]).join('');
console.log(`[First Letter All Words]: ${firstLetters.substring(0, 100)}...`);

// 2. First Letter of Every Line (Again, just to be sure)
const firstLetterLines = lines.map(l => l.replace(/[^a-zA-Z]/g, '')[0] || '').join('');
console.log(`[First Letter All Lines]: ${firstLetterLines}`);

// 3. Last Letter of Every Line
const lastLetterLines = lines.map(l => l.replace(/[^a-zA-Z]/g, '').slice(-1) || '').join('');
console.log(`[Last Letter All Lines]: ${lastLetterLines}`);

// 4. Check for "Mirror" clue more literally:
// Does any line contain a palindrome or reversed word?
console.log("\n[Reversed Words Check]:");
words.forEach(w => {
    if (w.length > 4 && w === w.split('').reverse().join('')) {
        console.log(`  Found palindrome: ${w}`);
    }
});

// 5. "George Sand" applied to WORDS instead of lines
// Read every 2nd word
const every2ndWord = words.filter((_, i) => i % 2 === 0).join(' ');
console.log(`\n[Every 2nd Word]: ${every2ndWord.substring(0, 100)}...`);

// 6. Look for "Private Key" text markers
const joinedText = rawText.replace(/\s+/g, '').toLowerCase();
if (joinedText.includes("5h") || joinedText.includes("5j") || joinedText.includes("5k")) {
    console.log("\n[Possible WIF Start Found]: '5H', '5J', or '5K' detected in condensed text.");
}

// 7. Bold text extraction (Manual simulation based on user input if they had bold)
// Since we don't have bold metadata in plain text, we skip.

// 8. Count word frequencies to see if any 12/24 words appear exactly once or in order?
// This is a weak check but might show if a specific set of words is "hidden"
// We'll skip for now.

// 9. Acrostic on the "George Sand" lines only (First letter of every 2nd line)
const sandLines = lines.filter((_, i) => i % 2 === 0);
const acrosticSand = sandLines.map(l => l.replace(/[^a-zA-Z]/g, '')[0] || '').join('');
console.log(`\n[Acrostic of George Sand Lines]: ${acrosticSand}`);

console.log("\nAnalysis Complete.");


