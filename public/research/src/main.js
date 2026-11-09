const fs = require('fs');
const path = require('path');
const { loadText, cleanText, getLines, getLinesPreserveEmpty } = require('./utils/text_processor');
const bip39 = require('./utils/bip39');
const ciphers = require('./utils/ciphers');

const TEXT_FILE = path.join(__dirname, '../full_article_corrected.txt');

function run() {
    console.log("Loading text from:", TEXT_FILE);
    const rawText = loadText(TEXT_FILE);
    if (!rawText) {
        console.error("Failed to load text.");
        return;
    }

    const words = cleanText(rawText);
    const lines = getLines(rawText);
    const linesPreserved = getLinesPreserveEmpty(rawText);

    console.log(`Loaded ${lines.length} lines, ${words.length} words.`);

    // 1. Basic Stats
    const bipWordsFound = words.filter(w => bip39.isBIP39Word(w));
    console.log(`Total BIP39 words found in raw text: ${bipWordsFound.length}`);
    
    // 2. Check Candidates from candidates.js (Hardcoded check)
    const candidates = ["now", "keep", "since", "sorry", "useless", "energy", "time", "that", "economy", "all", "love", "sea", "during"];
    console.log("\n--- Checking Hardcoded Candidates ---");
    // Try to find a valid 12-word subset
    if (candidates.length >= 12) {
        // This is a simple brute force for 1 removal if length is 13
        if (candidates.length === 13) {
            for (let i = 0; i < candidates.length; i++) {
                const subset = [...candidates];
                subset.splice(i, 1);
                const res = bip39.validateMnemonic(subset);
                if (res.valid) {
                    console.log(`FOUND VALID MNEMONIC (Removed '${candidates[i]}'):`, subset.join(' '));
                }
            }
        }
    }

    // 3. Run Ciphers and Check for BIP39 Chains
    console.log("\n--- Running Ciphers ---");
    
    const strategies = [
        { name: "Raw Text", fn: () => words.join(' ') },
        { name: "George Sand (Odd Lines)", fn: () => ciphers.georgeSand(lines) },
        { name: "George Sand (Even Lines)", fn: () => ciphers.georgeSandInverse(lines) },
        { name: "First Word (Odd Lines)", fn: () => ciphers.firstWord(lines.filter((_, i) => i % 2 === 0)) },
        { name: "First Word (Even Lines)", fn: () => ciphers.firstWord(lines.filter((_, i) => i % 2 !== 0)) },
        { name: "Reverse Text", fn: () => ciphers.reverseText(rawText) },
        { name: "Reverse Lines -> First Word", fn: () => ciphers.firstWord([...lines].reverse()) }
    ];

    strategies.forEach(strat => {
        const result = strat.fn();
        const stratWords = cleanText(result);
        const bipMatches = stratWords.filter(w => bip39.isBIP39Word(w));
        
        if (bipMatches.length > 10) {
            console.log(`\n[${strat.name}]`);
            console.log(`Found ${bipMatches.length} BIP39 words.`);
            
            // Check for consecutive chains
            let currentChain = [];
            let maxChain = [];
            
            stratWords.forEach(w => {
                if (bip39.isBIP39Word(w)) {
                    currentChain.push(w);
                } else {
                    if (currentChain.length > maxChain.length) maxChain = [...currentChain];
                    currentChain = [];
                }
            });
            if (currentChain.length > maxChain.length) maxChain = [...currentChain];

            if (maxChain.length > 2) {
                console.log(`Longest Consecutive Chain: ${maxChain.length} words`);
                console.log(`Chain: ${maxChain.join(' ')}`);
            }
            
            // If exactly 12 or 24 matches, validate
            if (bipMatches.length >= 12 && bipMatches.length <= 24) {
                console.log(`\nPotential Candidate (${bipMatches.length} words):`);
                console.log(bipMatches.join(' '));
                
                if (bipMatches.length === 12 || bipMatches.length === 24) {
                    const valid = bip39.validateMnemonic(bipMatches);
                    if (valid.valid) {
                        console.log("!!! VALID MNEMONIC FOUND !!!");
                    } else {
                        console.log(`(Invalid Checksum: ${valid.error})`);
                    }
                }
            }
        }
    });

    // 4. Nth Word Check
    console.log("\n--- Nth Word Check ---");
    for (let n = 2; n < 50; n++) {
        const nthWords = words.filter((_, i) => i % n === 0);
        const bipMatches = nthWords.filter(w => bip39.isBIP39Word(w));
        if (bipMatches.length > 10 && (bipMatches.length / nthWords.length > 0.5)) {
             console.log(`Every ${n}th word: ${bipMatches.length} BIP39 words found.`);
             // Check if they form a valid mnemonic?
             if (bipMatches.length === 12 || bipMatches.length === 24) {
                 const valid = bip39.validateMnemonic(bipMatches);
                 if (valid.valid) console.log("!!! VALID MNEMONIC !!!");
             }
        }
    }
}

run();

