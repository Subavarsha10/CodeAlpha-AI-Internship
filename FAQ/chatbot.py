import os
import json
import logging
import nltk
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from preprocess import TextPreprocessor

# Ensure required NLTK resources are downloaded automatically
NLTK_RESOURCES = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet")
]

for path, resource_id in NLTK_RESOURCES:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource_id, quiet=True)

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FAQChatbot")

load_dotenv()


class FAQChatbot:
    """
    Hybrid FAQ Engine combining local NLP (TF-IDF + Cosine Similarity)
    with Groq API (Llama 3 model) as an automatic generative fallback.
    """

    def __init__(
        self,
        faq_file_path: str = "faq.json",
        similarity_threshold: float = 0.40,
        threshold: float = None,  # Supports threshold as an alias argument
    ):
        self.faq_file_path = faq_file_path
        # Use threshold if explicitly passed, otherwise fallback to similarity_threshold
        self.similarity_threshold = (
            threshold if threshold is not None else similarity_threshold
        )

        self.preprocessor = TextPreprocessor()

        # Internal Storage
        self.questions_raw = []
        self.answers_raw = []
        self.preprocessed_questions = []

        # Scikit-learn Vectorizer
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

        # Load FAQ dataset & initialize model
        self._load_and_index_faqs()

        # Initialize Groq Client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq API Client successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq API client: {e}")

    def _load_and_index_faqs(self):
        """Loads FAQ JSON dataset and indexes preprocessed questions with TF-IDF."""
        if not os.path.exists(self.faq_file_path):
            raise FileNotFoundError(
                f"FAQ file not found at path: {self.faq_file_path}"
            )

        try:
            with open(self.faq_file_path, "r", encoding="utf-8") as f:
                faq_data = json.load(f)

            for item in faq_data:
                q = item.get("question", "").strip()
                a = item.get("answer", "").strip()
                if q and a:
                    self.questions_raw.append(q)
                    self.answers_raw.append(a)
                    # Preprocess for vectorization
                    clean_q = self.preprocessor.preprocess(q)
                    self.preprocessed_questions.append(clean_q)

            if not self.preprocessed_questions:
                raise ValueError(
                    "FAQ dataset is empty or formatted incorrectly."
                )

            # Compute TF-IDF Matrix for all stored questions
            self.tfidf_matrix = self.vectorizer.fit_transform(
                self.preprocessed_questions
            )
            logger.info(
                f"Successfully loaded and vectorized {len(self.questions_raw)} FAQ items."
            )

        except Exception as e:
            logger.error(f"Error loading FAQ JSON file: {e}")
            raise e

    def _search_faq(self, user_query: str) -> Tuple[str, float]:
        """
        Calculates cosine similarity between user query and stored FAQ vectors.
        Returns matching answer and similarity score if threshold met.
        """
        clean_user_query = self.preprocessor.preprocess(user_query)
        if not clean_user_query:
            return "", 0.0

        # Vectorize user query using pre-fitted TF-IDF
        query_vector = self.vectorizer.transform([clean_user_query])

        # Compute cosine similarity against all indexed FAQs
        similarities = cosine_similarity(
            query_vector, self.tfidf_matrix
        ).flatten()

        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])

        if best_score >= self.similarity_threshold:
            return self.answers_raw[best_index], round(best_score, 2)

        return "", round(best_score, 2)

    def _query_groq_ai(self, user_query: str) -> str:
        """Fallback function querying Groq Llama 3 model when local FAQ matching fails."""
        if not self.groq_client:
            return "I am currently unable to search online AI resources because the Groq API key is missing. Please check back later!"

        try:
            system_prompt = (
                "You are an expert AI & Computer Science Assistant representing CodeAlpha. "
                "Provide a clear, concise, accurate, and beginner-friendly response (maximum 3 paragraphs). "
                "Format code snippets using markdown code blocks if applicable."
            )

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=500,
            )

            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Groq API call error: {e}")
            return "I'm having trouble connecting to my external AI brain right now. Please try asking another Computer Science or AI question!"

    def get_response(self, user_query: str) -> Dict[str, Any]:
        """
        Main interface method. Tries local FAQ lookup first,
        and falls back to Groq AI if match confidence is below threshold.
        """
        if not user_query or not user_query.strip():
            return {
                "answer": "Please enter a valid question.",
                "source": "System Error",
            }

        faq_answer, confidence = self._search_faq(user_query)

        if faq_answer:
            return {
                "answer": faq_answer,
                "confidence": confidence,
                "source": "FAQ",
            }

        # Query AI Fallback
        ai_answer = self._query_groq_ai(user_query)
        return {
            "answer": ai_answer,
            "confidence": confidence,
            "source": "Groq AI",
        }