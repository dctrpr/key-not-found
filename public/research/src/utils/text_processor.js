const fs = require('fs');
const path = require('path');

function loadText(filePath) {
    try {
        return fs.readFileSync(filePath, 'utf8');
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error);
        return null;
    }
}

function cleanText(text) {
    if (!text) return [];
    // Remove non-alphabetic characters and split by whitespace
    return text.toLowerCase().replace(/[^a-z\s]/g, ' ').split(/\s+/).filter(w => w.length > 0);
}

function getLines(text) {
    if (!text) return [];
    return text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
}

function getLinesPreserveEmpty(text) {
    if (!text) return [];
    return text.split('\n');
}

module.exports = {
    loadText,
    cleanText,
    getLines,
    getLinesPreserveEmpty
};


