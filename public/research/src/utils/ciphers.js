const { cleanText } = require('./text_processor');

const strategies = {
    original: (text) => text,
    
    georgeSand: (lines) => lines.filter((_, i) => i % 2 === 0).join(' '),
    
    georgeSandInverse: (lines) => lines.filter((_, i) => i % 2 !== 0).join(' '),
    
    firstLetter: (lines) => lines.map(l => l.trim()[0]).join(''),
    
    firstWord: (lines) => lines.map(l => {
        const words = cleanText(l);
        return words.length > 0 ? words[0] : '';
    }).join(' '),
    
    lastWord: (lines) => lines.map(l => {
        const words = cleanText(l);
        return words.length > 0 ? words[words.length - 1] : '';
    }).join(' '),
    
    reverseText: (text) => text.split('').reverse().join(''),
    
    reverseLines: (lines) => [...lines].reverse().join('\n'),
    
    everyNthWord: (words, n) => words.filter((_, i) => i % n === 0).join(' '),
    
    diagonal: (lines) => {
        let res = "";
        for(let i=0; i<lines.length; i++) {
            const l = lines[i].trim();
            if(i < l.length) res += l[i];
        }
        return res;
    }
};

module.exports = strategies;


