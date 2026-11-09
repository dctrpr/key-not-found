const fs = require('fs');
const bip39 = require('bip39');
const bitcoin = require('bitcoinjs-lib');
const { BIP32Factory } = require('bip32');
const ecc = require('tiny-secp256k1');
const bip32 = BIP32Factory(ecc);
const ECPair = require('ecpair').ECPairFactory(ecc); // Need ECPair for WIF
const axios = require('axios');

// --- CONFIGURATION ---
// Adjust path to point to the file in the parent directory if running from legacy/
// or assume we run from root and the file is in root.
// Since the script is in legacy/, but we run from root usually, let's check both.
const TEXT_FILE_NAME = 'full_article_corrected.txt';
let TEXT_FILE = TEXT_FILE_NAME;
if (!fs.existsSync(TEXT_FILE)) {
    TEXT_FILE = '../' + TEXT_FILE_NAME;
}

const API_DELAY_MS = 1000; // Delay between API calls to avoid rate limits

// --- HELPERS ---
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Function to derive addresses from a mnemonic
function deriveAddresses(mnemonic) {
    const seed = bip39.mnemonicToSeedSync(mnemonic);
    const root = bip32.fromSeed(seed);
    const addresses = [];

    // 1. Legacy (P2PKH) - m/44'/0'/0'/0/0
    const path44 = "m/44'/0'/0'/0/0";
    const child44 = root.derivePath(path44);
    const { address: p2pkh } = bitcoin.payments.p2pkh({ pubkey: child44.publicKey });
    addresses.push({ type: 'Legacy (P2PKH)', path: path44, address: p2pkh });

    // 2. Segwit Compatible (P2SH-P2WPKH) - m/49'/0'/0'/0/0
    const path49 = "m/49'/0'/0'/0/0";
    const child49 = root.derivePath(path49);
    const { address: p2sh } = bitcoin.payments.p2sh({
        redeem: bitcoin.payments.p2wpkh({ pubkey: child49.publicKey }),
    });
    addresses.push({ type: 'Segwit (P2SH)', path: path49, address: p2sh });

    // 3. Native Segwit (P2WPKH) - m/84'/0'/0'/0/0
    const path84 = "m/84'/0'/0'/0/0";
    const child84 = root.derivePath(path84);
    const { address: p2wpkh } = bitcoin.payments.p2wpkh({ pubkey: child84.publicKey });
    addresses.push({ type: 'Native Segwit (P2WPKH)', path: path84, address: p2wpkh });

    return addresses;
}

// Function to check balances for multiple addresses in one call
async function checkBalances(addresses) {
    try {
        const addressList = addresses.map(a => a.address).join('|');
        const url = `https://blockchain.info/multiaddr?active=${addressList}`;
        const response = await axios.get(url);
        const data = response.data;
        
        let totalBalance = 0;
        let totalReceived = 0;
        
        if (data.addresses) {
            for (const addrData of data.addresses) {
                totalBalance += addrData.final_balance;
                totalReceived += addrData.total_received;
            }
        }

        return { totalReceived, finalBalance: totalBalance };
    } catch (error) {
        if (error.response && error.response.status === 429) {
            console.log("Rate limited. Waiting 5 seconds...");
            await sleep(5000);
            return checkBalances(addresses); // Retry
        }
        // console.error(`Error checking balances: ${error.message}`);
        return null;
    }
}

// --- STRATEGIES ---

function extractWords(text) {
    return text.toLowerCase().replace(/[^a-z\s]/g, ' ').split(/\s+/).filter(w => w.length > 0);
}

function getStrategies(rawText) {
    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    const allWords = extractWords(rawText);
    
    const strategies = [];

    // 1. Raw Text
    strategies.push({ name: "Raw Text", words: allWords });

    // 2. George Sand (Every 2nd line starting from 1)
    const sand1 = lines.filter((_, i) => i % 2 === 0).join(' ');
    strategies.push({ name: "George Sand (Lines 1,3,5...)", words: extractWords(sand1) });

    // 3. George Sand Inverse (Every 2nd line starting from 2)
    const sand2 = lines.filter((_, i) => i % 2 !== 0).join(' ');
    strategies.push({ name: "George Sand Inverse (Lines 2,4,6...)", words: extractWords(sand2) });

    // 4. First Word of Each Line
    const firstWords = lines.map(l => extractWords(l)[0]).filter(w => w);
    strategies.push({ name: "First Word of Each Line", words: firstWords });

    // 5. Last Word of Each Line
    const lastWords = lines.map(l => {
        const w = extractWords(l);
        return w[w.length - 1];
    }).filter(w => w);
    strategies.push({ name: "Last Word of Each Line", words: lastWords });

    // 6. Acrostic (First letter of each line -> check if they form words? No, usually letters. 
    // But maybe the letters spell out BIP39 words? Unlikely for 12 words. Skipping for now.)

    // 7. Every Nth Word (1 to 50)
    for (let n = 2; n <= 50; n++) {
        const nthWords = allWords.filter((_, i) => i % n === 0);
        strategies.push({ name: `Every ${n}th Word`, words: nthWords });
    }

    // 8. Mirror (Reverse Text)
    const reversedText = rawText.split('').reverse().join('');
    strategies.push({ name: "Mirror Text", words: extractWords(reversedText) });

    return strategies;
}

// Function to check WIF key
function checkWIF(text) {
    try {
        const keyPair = ECPair.fromWIF(text);
        const { address } = bitcoin.payments.p2pkh({ pubkey: keyPair.publicKey });
        return address;
    } catch (e) {
        return null;
    }
}

// --- MAIN ---

async function main() {
    console.log("Starting Max Keiser Puzzle Solver...");
    
    if (!fs.existsSync(TEXT_FILE)) {
        console.error(`Error: Could not find text file at ${TEXT_FILE}`);
        process.exit(1);
    }

    const rawText = fs.readFileSync(TEXT_FILE, 'utf8');
    
    // 0. Check for WIF keys in raw text
    console.log("Scanning for WIF keys...");
    const wifRegex = /[5KL][1-9A-HJ-NP-Za-km-z]{50,51}/g;
    const wifMatches = rawText.match(wifRegex) || [];
    for (const wif of wifMatches) {
        const address = checkWIF(wif);
        if (address) {
            console.log(`[POSSIBLE WIF KEY FOUND]: ${wif}`);
            const balance = await checkBalances([{ address }]);
            if (balance && (balance.totalReceived > 0 || balance.finalBalance > 0)) {
                const msg = `\n!!! FOUND FUNDS (WIF) !!!\nKey: ${wif}\nAddress: ${address}\nBalance: ${balance.finalBalance} sats\n`;
                console.log(msg);
                fs.appendFileSync('found_funds.txt', msg);
            }
        }
    }

    const strategies = getStrategies(rawText);
    const wordlist = bip39.wordlists.english;
    const wordSet = new Set(wordlist);

    const testedMnemonics = new Set();
    let foundValid = 0;

    for (const strat of strategies) {
        // Filter only valid BIP39 words
        const validWords = strat.words.filter(w => wordSet.has(w));
        
        if (validWords.length < 12) continue;

        // console.log(`Strategy: ${strat.name} (${validWords.length} BIP39 words)`);

        // Sliding Window for 12 and 24 words
        const lengths = [12, 24];
        
        for (const len of lengths) {
            if (validWords.length < len) continue;

            for (let i = 0; i <= validWords.length - len; i++) {
                const candidate = validWords.slice(i, i + len).join(' ');
                
                if (testedMnemonics.has(candidate)) continue;
                testedMnemonics.add(candidate);

                if (bip39.validateMnemonic(candidate)) {
                    console.log(`\n[VALID MNEMONIC FOUND]`);
                    console.log(`Strategy: ${strat.name}`);
                    console.log(`Phrase: ${candidate}`);
                    foundValid++;
                    
                    // Check Balance
                    const addresses = deriveAddresses(candidate);
                    // console.log(`  Checking ${addresses.length} addresses...`);
                    
                    const balance = await checkBalances(addresses);
                    if (balance && (balance.totalReceived > 0 || balance.finalBalance > 0)) {
                        const msg = `\n!!! FOUND FUNDS !!!\nStrategy: ${strat.name}\nPhrase: ${candidate}\nBalance: ${balance.finalBalance} sats\nTotal Received: ${balance.totalReceived} sats\n`;
                        console.log(msg);
                        fs.appendFileSync('found_funds.txt', msg);
                    }
                    await sleep(API_DELAY_MS);
                }
            }
        }

        // Special Case: 13 words (1 extra) -> Try removing 1
        if (validWords.length >= 13) {
             for (let i = 0; i <= validWords.length - 13; i++) {
                const chunk = validWords.slice(i, i + 13);
                for (let removeIdx = 0; removeIdx < 13; removeIdx++) {
                    const temp = [...chunk];
                    temp.splice(removeIdx, 1);
                    const candidate = temp.join(' ');
                    
                    if (testedMnemonics.has(candidate)) continue;
                    testedMnemonics.add(candidate);

                    if (bip39.validateMnemonic(candidate)) {
                        console.log(`\n[VALID MNEMONIC (13-1)]`);
                        console.log(`Strategy: ${strat.name} (Removed word at index ${removeIdx}: ${chunk[removeIdx]})`);
                        console.log(`Phrase: ${candidate}`);
                        
                        const addresses = deriveAddresses(candidate);
                        const balance = await checkBalances(addresses);
                        if (balance && (balance.totalReceived > 0 || balance.finalBalance > 0)) {
                            const msg = `\n!!! FOUND FUNDS (13-1) !!!\nStrategy: ${strat.name}\nPhrase: ${candidate}\nBalance: ${balance.finalBalance} sats\n`;
                            console.log(msg);
                            fs.appendFileSync('found_funds.txt', msg);
                        }
                        await sleep(API_DELAY_MS);
                    }
                }
             }
        }
    }

    console.log(`\nDone. Tested ${testedMnemonics.size} candidates.`);
}

main().catch(console.error);
