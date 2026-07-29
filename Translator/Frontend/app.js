// ================================
// DOM Elements
// ================================
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");

const sourceLanguage = document.getElementById("sourceLanguage");
const targetLanguage = document.getElementById("targetLanguage");

const translateBtn = document.getElementById("translateBtn");
const swapBtn = document.getElementById("swapBtn");
const copyBtn = document.getElementById("copyBtn");
const speakBtn = document.getElementById("speakBtn");

// ================================
// Load Languages
// ================================
function loadLanguages() {
    sourceLanguage.innerHTML = "";
    targetLanguage.innerHTML = "";

    for (const code in languages) {
        const option1 = document.createElement("option");
        option1.value = code;
        option1.textContent = languages[code];

        const option2 = document.createElement("option");
        option2.value = code;
        option2.textContent = languages[code];

        sourceLanguage.appendChild(option1);
        targetLanguage.appendChild(option2);
    }

    // Default setups: English to Tamil
    sourceLanguage.value = "en";
    targetLanguage.value = "ta";
}

loadLanguages();

// ================================
// Translate Function
// ================================
translateBtn.addEventListener("click", translateText);

async function translateText() {
    const text = inputText.value.trim();

    if (!text) {
        alert("Please enter some text.");
        return;
    }

    outputText.value = "Translating...";

    // --- STEP 1: Send to local backend server ---
    try {
        const response = await fetch("http://127.0.0.1:3000/api/translate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                source: sourceLanguage.value,
                target: targetLanguage.value
            })
        });

        const data = await response.json();

        if (data.success) {
            outputText.value = data.translatedText;
            return; // Successfully translated, stop here!
        }
    } catch (backendError) {
        console.warn("Backend server not responding. Trying browser fallback translation...", backendError.message);
    }

    // --- STEP 2: Browser Fallback Engine (Runs if server is offline) ---
    try {
        const langPair = `${sourceLanguage.value}|${targetLanguage.value}`;
        const fallbackUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`;
        
        const fallbackResponse = await fetch(fallbackUrl);
        const fallbackData = await fallbackResponse.json();

        if (fallbackData && fallbackData.responseData) {
            outputText.value = fallbackData.responseData.translatedText;
        } else {
            outputText.value = "Translation service returned an empty response.";
        }
    } catch (fallbackError) {
        console.error("All translation endpoints failed:", fallbackError);
        outputText.value = "Translation Failed.";
    }
}

// ================================
// Swap Languages
// ================================
swapBtn.addEventListener("click", () => {
    const temp = sourceLanguage.value;
    sourceLanguage.value = targetLanguage.value;
    targetLanguage.value = temp;
});

// ================================
// Copy to Clipboard
// ================================
copyBtn.addEventListener("click", () => {
    const textToCopy = outputText.value.trim();
    
    // Ignore if empty or still processing
    if (!textToCopy || textToCopy.toLowerCase().includes("translating")) {
        return;
    }
    
    navigator.clipboard.writeText(textToCopy)
        .then(() => alert("Copied to clipboard!"))
        .catch(err => console.error("Could not copy text: ", err));
});

