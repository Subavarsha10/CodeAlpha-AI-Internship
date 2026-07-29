import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data resources quietly
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class TextPreprocessor:
    """
    Handles standard NLP preprocessing including lowercasing, punctuation removal,
    tokenization, stopword filtering, and lemmatization.
    """
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess(self, text: str) -> str:
        """
        Preprocesses an input text string.
        Returns a cleaned, lemmatized string joined by spaces.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Lowercase text
        text = text.lower().strip()

        # 2. Remove special characters and punctuation using Regex
        text = re.sub(r'[^a-z0-9\s]', '', text)

        # 3. Tokenize text into words
        tokens = word_tokenize(text)

        # 4. Filter stopwords and perform lemmatization
        cleaned_tokens = [
            self.lemmatizer.lemmatize(word)
            for word in tokens
            if word not in self.stop_words and len(word) > 1
        ]

        # 5. Fallback: If all tokens were filtered out, retain original tokens lowercased
        if not cleaned_tokens and tokens:
            cleaned_tokens = tokens

        return " ".join(cleaned_tokens)