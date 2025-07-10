# Novel Chat AI Discord Bot

This Discord bot allows users to upload documents (PDF, EPUB, or TXT) and ask questions about their content. The bot uses the Gemini AI to understand the document and provide answers based solely on the text provided.

## Features

- **Document Analysis:** Upload a document directly to the bot in a DM.
- **Supported Formats:** PDF (.pdf), EPUB (.epub), and Text (.txt).
- **Q&A:** Ask questions in natural language about the uploaded document.
- **Context-Aware:** The bot remembers the context of the last uploaded file for follow-up questions.
- **Simple Commands:** Easy-to-use commands to manage the bot.

## How It Works

1.  **Upload:** The user sends a direct message to the bot with an attached document.
2.  **Extraction:** The bot extracts the text from the document.
3.  **Context:** The extracted text is stored as the current context for that user.
4.  **Query:** The user asks a question.
5.  **Response:** The bot sends the document text and the user's question to the Gemini API and returns the answer.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Chandu4143/novel-chat-ai.git
    cd novel-chat-ai
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file:**
    -   Copy the `.env.example` file to `.env`.
    -   Add your Discord bot token and Google API key to the `.env` file.
    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token
    GOOGLE_API_KEY=your_google_api_key
    ```

4.  **Run the bot:**
    ```bash
    python bot.py
    ```

## Usage

-   **Upload a document:** Send a DM to the bot with a `.pdf`, `.epub`, or `.txt` file attached.
-   **Ask a question:** Once the bot confirms the document has been processed, simply type your question in the DM.
-   `!reset`: Clears the current document, allowing you to upload a new one.
-   `!status`: Shows the currently loaded document.
-   `!help`: Shows a list of available commands.

## Project Structure

```
.
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
├── cogs/
│   └── document_cog.py # Cog for handling document processing and commands
└── utils/
    ├── ai_handler.py   # Handles interaction with the Gemini API
    └── file_processor.py # Handles text extraction from files
```
