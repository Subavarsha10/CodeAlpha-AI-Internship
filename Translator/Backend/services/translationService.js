const axios = require("axios");

const translate = async (text, source, target) => {
    try {
        console.log(`Sending to MyMemory API: "${text}" (${source} -> ${target})`);
        
        // MyMemory pairs languages using "source|target" format (e.g., "en|ta")
        const langPair = `${source}|${target}`;
        const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`;
        
        const response = await axios.get(url, { timeout: 5000 });

        if (response.data && response.data.responseData) {
            console.log("Translation successfully received!");
            return response.data.responseData.translatedText;
        } else {
            throw new Error("Invalid API response format");
        }
    } catch (error) {
        console.error("MyMemory API Error:", error.message);
        throw new Error("Translation service failed to respond");
    }
};

module.exports = { translate };