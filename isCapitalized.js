function isCapitalized(text) {
    const excludedWords = ["and", "and/or", "or", "the", "of", "to", "by", "in", "per", "at", "on", "for", "-", "(", "(%", ")", "/"];

    const words = text.split(' ');
    for (const word of words) {
        if (!word) continue; // skip empty strings from multiple spaces

        if (excludedWords.includes(word.toLowerCase())) continue;

        const firstChar = word.charAt(0);

        // Skip words that start with punctuation (e.g. "(15-34)", "- Quarterly")
        if (/^[(\[\-\/]/.test(firstChar)) continue;

        // Accept non-Latin scripts (Arabic, etc.) - no capitalization concept
        if (!/[A-Za-z]/.test(word)) continue;

        // For Latin text, require first letter to be uppercase or digit
        if (!/^[A-Z0-9]/.test(firstChar)) {
            return false;
        }
    }
    return true;
}

// Test cases
console.log(isCapitalized("المتعطلون (15-34) سنة المقيمون في إمارة أبوظبي حسب النوع - ربع سنوي")); // true
console.log(isCapitalized("Unemployed Persons Ages (15-34) Residing in the Emirate of Abu Dhabi by Gender - Quarterly")); // true
