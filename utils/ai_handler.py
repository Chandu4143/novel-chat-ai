# utils/ai_handler.py

import google.generativeai as genai

# --- Constants ---
PROMPT_TEMPLATE = """
You are a helpful assistant. Analyze the following document and answer the user's question based ONLY on the content provided.

DOCUMENT CONTENT:
---
{document_text}
---

USER'S QUESTION:
{user_query}

ANSWER:
"""

class AIHandler:
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("Google API Key cannot be empty.")
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self._configure()

    def _configure(self):
        """Configures the Gemini API and initializes the model."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name=self.model_name)
            print("Gemini AI Handler configured successfully.")
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            raise

    async def get_response(self, document_text: str, user_query: str, max_text_length: int) -> str:
        """
        Generates a response from the Gemini API based on the document and query.
        This is an async function that runs the blocking API call in an executor.
        """
        if not self.model:
            return "The AI model is not initialized. Please check the API key and configuration."

        if not document_text:
            return "I don't have any document context. Please upload a file first."

        prompt = PROMPT_TEMPLATE.format(
            document_text=document_text[:max_text_length],
            user_query=user_query
        )

        try:
            # The generate_content call is synchronous (blocking), so we run it
            # in an executor to avoid blocking the bot's event loop.
            response = await genai.GenerativeModel.generate_content_async(self.model, prompt)

            if response.parts:
                return response.text
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                return f"My response was blocked. Reason: {response.prompt_feedback.block_reason}. This can happen if the query or document content triggers a safety filter."
            else:
                return "I received an empty response from the AI. Please try rephrasing your question."

        except Exception as e:
            print(f"Error interacting with Gemini API: {e}")
            return f"Sorry, an error occurred while contacting the AI service: {e}"