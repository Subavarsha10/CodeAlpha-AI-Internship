import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from chatbot import FAQChatbot

# Load environment variables
load_dotenv()

# Setup Flask Application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskServer")

# Initialize Chatbot Core Engine
try:
    chatbot = FAQChatbot(faq_file_path="faq.json", similarity_threshold=0.35)
    logger.info("FAQ Chatbot Engine initialized successfully.")
except Exception as err:
    logger.critical(f"Critical error initializing Chatbot Engine: {err}")
    chatbot = None


@app.route("/")
def index():
    """Renders main chatbot UI application page."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint indicating server and engine status."""
    return (
        jsonify({
            "status": "online",
            "faq_engine_ready": chatbot is not None,
            "groq_api_configured": bool(os.getenv("GROQ_API_KEY")),
        }),
        200,
    )


@app.route("/chat", methods=["POST"])
def chat():
    """Primary chat endpoint accepting JSON payload with user message."""
    if not chatbot:
        return (
            jsonify({
                "error": "Chatbot engine is unavailable.",
                "answer": (
                    "Internal Server Error: FAQ engine failed to initialize."
                ),
            }),
            500,
        )

    try:
        data = request.get_json(silent=True)
        if not data:
            return (
                jsonify({"error": "Invalid request. JSON payload expected."}),
                400,
            )

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "User message cannot be empty."}), 400

        # Retrieve structured response from backend engine
        result = chatbot.get_response(user_message)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error handling /chat request: {e}")
        return (
            jsonify({
                "error": (
                    "An internal server error occurred while processing your"
                    " request."
                ),
                "answer": (
                    "Sorry, something went wrong on our server. Please try"
                    " again."
                ),
            }),
            500,
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)