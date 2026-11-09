const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const bip39 = require('bip39');
const bitcoin = require('bitcoinjs-lib');
const { BIP32Factory } = require('bip32');
const ecc = require('tiny-secp256k1');
const bip32 = BIP32Factory(ecc);
const ECPair = require('ecpair').ECPairFactory(ecc);
const axios = require('axios');

const app = express();
const PORT = 3000;

app.use(bodyParser.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, '.')));

// --- BITCOIN LOGIC ---

function deriveAddresses(mnemonic) {
    if (!bip39.validateMnemonic(mnemonic)) return [];
    
    const seed = bip39.mnemonicToSeedSync(mnemonic);
    const root = bip32.fromSeed(seed);
    const addresses = [];

    try {
        // 1. Legacy (P2PKH) - m/44'/0'/0'/0/0
        const path44 = "m/44'/0'/0'/0/0";
        const child44 = root.derivePath(path44);
        const { address: p2pkh } = bitcoin.payments.p2pkh({ pubkey: child44.publicKey });
        addresses.push({ type: 'Legacy', address: p2pkh });

        // 2. Segwit (P2SH-P2WPKH) - m/49'/0'/0'/0/0
        const path49 = "m/49'/0'/0'/0/0";
        const child49 = root.derivePath(path49);
        const { address: p2sh } = bitcoin.payments.p2sh({
            redeem: bitcoin.payments.p2wpkh({ pubkey: child49.publicKey }),
        });
        addresses.push({ type: 'Segwit', address: p2sh });

        // 3. Native Segwit (P2WPKH) - m/84'/0'/0'/0/0
        const path84 = "m/84'/0'/0'/0/0";
        const child84 = root.derivePath(path84);
        const { address: p2wpkh } = bitcoin.payments.p2wpkh({ pubkey: child84.publicKey });
        addresses.push({ type: 'Native', address: p2wpkh });
    } catch (e) {
        console.error("Derivation error:", e);
    }

    return addresses;
}

const API_DELAY_MS = 200;
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Batch check addresses
async function checkBalances(addresses) {
    try {
        const uniqueAddrs = [...new Set(addresses)];
        // Chunking (blockchain.info supports multiple, but let's keep it safe with ~10-20 max per call if possible, 
        // actually multiaddr endpoint usually handles more but let's be safe)
        
        // Note: We are receiving candidates. Each candidate generates 3 addresses.
        // We should check them.
        
        // Let's use mempool.space one by one for reliability OR blockchain.info multiaddr for speed.
        // Since user wants automation, speed is key.
        
        const addressList = uniqueAddrs.join('|');
        const url = `https://blockchain.info/multiaddr?active=${addressList}`;
        
        // console.log(`Checking balances for ${uniqueAddrs.length} addresses...`);
        const response = await axios.get(url);
        const data = response.data;
        
        let results = [];
        
        if (data.addresses) {
            for (const addrData of data.addresses) {
                if (addrData.final_balance > 0 || addrData.total_received > 0) {
                    results.push({
                        address: addrData.address,
                        balance: addrData.final_balance,
                        received: addrData.total_received
                    });
                }
            }
        }
        return results;
    } catch (error) {
        // console.error("API Error:", error.message);
        return [];
    }
}

// --- API ENDPOINTS ---

app.post('/check-balance', async (req, res) => {
    const candidates = req.body.candidates;
    if (!candidates || !Array.isArray(candidates)) {
        return res.status(400).json({ error: "Invalid candidates list" });
    }

    console.log(`Received ${candidates.length} candidates to check.`);
    
    const found = [];
    
    // Separate WIFs from Mnemonics
    const wifCandidates = [];
    const mnemonicCandidates = [];
    
    candidates.forEach(c => {
        // Simple WIF heuristic (Base58 check could be better but regex is fast)
        if (/[5KL][1-9A-HJ-NP-Za-km-z]{50,51}/.test(c)) {
            wifCandidates.push(c);
        } else if (c.split(' ').length >= 12) {
            if (bip39.validateMnemonic(c)) mnemonicCandidates.push(c);
        }
    });

    console.log(`Valid Mnemonics: ${mnemonicCandidates.length}, Possible WIFs: ${wifCandidates.length}`);

    // Stats to return
    const stats = {
        totalReceived: candidates.length,
        mnemonicsChecked: mnemonicCandidates.length,
        wifsChecked: wifCandidates.length,
        brainwalletsChecked: 0
    };

    // 1. Check WIFs
    for (const wif of wifCandidates) {
        try {
            const keyPair = ECPair.fromWIF(wif);
            const { address } = bitcoin.payments.p2pkh({ pubkey: keyPair.publicKey });
            const results = await checkBalances([address]);
            results.forEach(r => found.push({ phrase: wif, address: r.address, balance: r.balance, received: r.received, type: 'WIF' }));
        } catch (e) { }
    }

    // 2. Check Mnemonics
    const CHUNK_SIZE = 10;
    for (let i = 0; i < mnemonicCandidates.length; i += CHUNK_SIZE) {
        const chunk = mnemonicCandidates.slice(i, i + CHUNK_SIZE);
        let allAddresses = [];
        let addrToMnemonicMap = {};

        chunk.forEach(m => {
            const addrs = deriveAddresses(m);
            addrs.forEach(a => {
                allAddresses.push(a.address);
                addrToMnemonicMap[a.address] = m;
            });
        });

        if (allAddresses.length > 0) {
            const results = await checkBalances(allAddresses);
            results.forEach(r => {
                found.push({
                    phrase: addrToMnemonicMap[r.address],
                    address: r.address,
                    balance: r.balance,
                    received: r.received,
                    type: 'Mnemonic'
                });
            });
        }
        await sleep(200); 
    }

    // 3. Check Brainwallets (SHA256 of every candidate)
    // This is fast to generate, but API calls are the bottleneck.
    // Let's only do this for "likely" candidates (e.g. > 10 chars) or limiting to a subset if too many?
    // For now, let's try top 100 longest candidates or just check the bold text candidates specifically?
    // Actually, checking 6000 addresses for brainwallets will kill the rate limit.
    // Let's just check the ones that look like sentences (space separated)?
    // Or just pure candidates.
    
    // Limit brainwallet checks to avoid rate limiting hell for now, or just check distinct unique addresses.
    // Let's skip bulk brainwallet for "Every Nth word" garbage.
    
    res.json({ results: found, stats });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
