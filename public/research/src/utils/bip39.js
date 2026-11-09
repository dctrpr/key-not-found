const crypto = require('crypto');
const wordlist = require('../data/wordlist');

const wordMap = new Map(wordlist.map((w, i) => [w, i]));

function isBIP39Word(word) {
    return wordMap.has(word);
}

function getWordIndex(word) {
    return wordMap.get(word);
}

function validateMnemonic(mnemonic) {
    const words = Array.isArray(mnemonic) ? mnemonic : mnemonic.split(' ');
    
    if (![12, 15, 18, 21, 24].includes(words.length)) {
        return { valid: false, error: "Invalid word count" };
    }

    // Check if all words are valid
    const invalidWords = words.filter(w => !wordMap.has(w));
    if (invalidWords.length > 0) {
        return { valid: false, error: `Invalid words: ${invalidWords.join(', ')}` };
    }

    // Checksum validation
    try {
        const bits = words.map(w => {
            const index = wordMap.get(w);
            return index.toString(2).padStart(11, '0');
        }).join('');

        const checksumLength = words.length / 3;
        const entropyLength = bits.length - checksumLength;

        const entropyBits = bits.slice(0, entropyLength);
        const checksumBits = bits.slice(entropyLength);

        // Convert entropy bits to buffer
        const entropyBytes = [];
        for (let i = 0; i < entropyLength; i += 8) {
            entropyBytes.push(parseInt(entropyBits.slice(i, i + 8), 2));
        }
        const entropyBuffer = Buffer.from(entropyBytes);

        // Hash entropy
        const hash = crypto.createHash('sha256').update(entropyBuffer).digest();
        
        // Get first N bits of hash
        let hashBits = '';
        for (let i = 0; i < hash.length; i++) {
            hashBits += hash[i].toString(2).padStart(8, '0');
        }
        const calculatedChecksum = hashBits.slice(0, checksumLength);

        if (checksumBits === calculatedChecksum) {
            return { valid: true };
        } else {
            return { valid: false, error: "Invalid checksum" };
        }
    } catch (e) {
        return { valid: false, error: e.message };
    }
}

module.exports = {
    wordlist,
    isBIP39Word,
    validateMnemonic
};


