const { translate } = require("../services/translationService");

const translateText = async (req, res) => {
    try {
        const { text, source, target } = req.body;

        // Backend Log to make sure the server receives the correct data
        console.log(`Backend processing request: "${text}" from [${source}] to [${target}]`);

        if (!text || !source || !target) {
            return res.status(400).json({
                success: false,
                message: "Please provide text, source language, and target language."
            });
        }

        // Fetch the actual translation using our translation service
        const translatedResult = await translate(text, source, target);

        return res.json({
            success: true,
            translatedText: translatedResult
        });

    } catch (error) {
        console.error("Translation Controller Error:", error.message);
        return res.status(500).json({
            success: false,
            message: "Translation Failed on the server."
        });
    }
};

module.exports = {
    translateText
};