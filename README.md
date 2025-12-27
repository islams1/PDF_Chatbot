# 📄 PDF_Chatbot

An AI-powered document understanding system designed to help users extract knowledge from PDF files quickly and intelligently. This project uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers to your questions based on the content of your uploaded documents.

## 🚀 Features

*   **PDF Upload:** Easily upload one or multiple PDF documents.
*   **Smart Chunking:** Automatically splits long documents into meaningful text chunks (with overlap) to preserve context.
*   **Vector Search:** Uses **FAISS** to store and retrieve relevant information efficiently.
*   **AI Integration:** Powered by **Google Gemini** to generate natural language responses.
*   **Context-Aware:** Answers are based strictly on the provided documents.

## 🛠️ Tech Stack

*   **Language:** Python
*   **AI Model:** Google Gemini (GenAI)
*   **Vector Database:** FAISS
*   **PDF Processing:** PyPDF2 / pdfplumber (depending on your implementation)

## ⚙️ Installation & Setup

Follow these steps to run the project locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/islams1/PDF_Chatbot.git
    cd Chat_With_PDF
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `config.py` file in the root directory and add your API Key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

5.  **Run the application:**
    ```bash
    # Replace 'main.py' with your actual entry file name
    python main.py
    ```


