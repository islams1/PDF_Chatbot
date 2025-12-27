import pymongo
import traceback
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, GOOGLE_API_KEY
import json

print("start ")

try:
    print("Loading Embedding ")
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Loading Gemini ")
    Settings.llm = GoogleGenAI(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

    print("Models setup done.")
except Exception as e:
    print(f"Error setting up models: {e}")


class RAGEngine:
    
    def __init__(self):
        print("Initializing RAG Engine...")
        
        self.client = None
        self.vector_store = None
        self.index = None
        
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.client.admin.command('ping')
            print("Success Connected")
            
            self.vector_store = MongoDBAtlasVectorSearch(
                mongodb_client=self.client,
                db_name=DB_NAME,
                collection_name=COLLECTION_NAME,
                vector_index_name="vector_index"
            )
        except Exception as e:
            print(f"MongoDB Connection Error: {e}")
            return

        try:
            self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
            self.query_engine = self.index.as_query_engine()
            print("RAG Engine ready.")
        except Exception as e:
            print(f"Index might be empty or new: {e}")
            self.index = None 

    def add_pdf(self, file_path: str):
        print(f"Processing PDF: {file_path}")
        
        try:
            print("Deleting old data")
            db = self.client[DB_NAME]
            collection = db[COLLECTION_NAME]
            delete_result = collection.delete_many({}) # يمسح كل المستندات
            print(f"Deleted {delete_result.deleted_count} old chunks.")
            
            self.index = None
            self.query_engine = None
            
        except Exception as e:
            print(f"Warning during cleanup: {e}")

        try:
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            print(f"Loaded {len(documents)} ...")

            print("Creating New Index ")
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            self.index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                show_progress=True
            )
            
            self.query_engine = self.index.as_query_engine()
            print(f"Successfully added {file_path} to Mongodb.")

        except Exception as e:
            print(f"CRITICAL ERROR inside add_pdf:")
            print(f"Error Message: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Failed to process PDF: {str(e)}")

    def query(self, question: str):
        if self.index is None:
            return "Database is empty. Please upload a PDF first."
        
        try:
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            print(f" Query Error: {e}")
            return "Sorry, I cannot answer right now."
        
    def generate_flashcards(self):
        if self.index is None:
            return json.dumps({"error": "Database is empty. Upload PDF first."})

        prompt = """
        You are a strict JSON generator. Based on the uploaded document, generate 5 study flashcards.
        
        RULES:
        1. Output MUST be a valid JSON list.
        2. Do NOT write any introduction or conclusion.
        3. Do NOT use markdown code blocks (like ```json).
        4. Format: [{"front": "Concept", "back": "Definition"}, ...]
        """
        
        response = self.query_engine.query(prompt)
        text = str(response).strip()

        try:
            start_index = text.find('[')
            end_index = text.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                text = text[start_index:end_index]
            
            json.loads(text) 
            return text
            
        except Exception as e:
            print(f"JSON Parsing Error: {text}")
            return json.dumps({"error": "Failed to parse Gemini response", "raw": text})
        
    def generate_quiz(self):
        if self.index is None:
            return json.dumps({"error": "Database is empty."})

        prompt = """
        Generate a strictly valid JSON list of 3 Multiple Choice Questions based on the document.
        
        RULES:
        1. No markdown, no intro.
        2. Format: 
        [
            {
                "question": "Question text?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            },
            ...
        ]
        """
        try:
            response = self.query_engine.query(prompt)
            text = str(response).strip()
            
            if "```json" in text: text = text.replace("```json", "").replace("```", "")
            start, end = text.find('['), text.rfind(']') + 1
            return text[start:end] if start != -1 else text
            
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    def generate_interactive_map(self):
        if self.index is None:
            return json.dumps({"error": "Database is empty."})

        prompt = """
        Analyze the document and create a detailed hierarchical structure.
        Output MUST be strictly a JSON object with this structure:
        {
          "filename": "Name of PDF",
          "topics": [
            {
              "title": "Main Topic 1",
              "points": [
                {
                  "sub_title": "Point 1.1",
                  "description": "Detailed explanation of Point 1.1"
                }
              ]
            }
          ]
        }
        Do not include any markdown formatting (```json).
        """
        try:
            response = self.query_engine.query(prompt)
            text = str(response).strip()
            start = text.find('{')
            end = text.rfind('}') + 1
            return text[start:end]
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    def generate_summary(self):
        if self.index is None:
            return "Database is empty."

        prompt = """
        Generate a comprehensive professional summary of the document.
        The summary should be formatted in Markdown and include:
        1. **Executive Summary**: A brief overview.
        2. **Key Takeaways**: Bullet points of the most important facts.
        3. **Detailed Analysis**: Important sections explained.
        4. **Conclusion**.
        
        Keep it clear, concise, and structured.
        """
        try:
            response = self.query_engine.query(prompt)
            return str(response)
        except Exception as e:
            return f"Error generating summary: {str(e)}"
        
    def generate_slide_content(self):
        if self.index is None:
            return json.dumps({"error": "Database is empty."})

        prompt = """
        Create content for a 5-slide presentation based on the document.
        Output MUST be a strictly valid JSON list.
        
        Format:
        [
            {
                "title": "Slide 1 Title (Main Topic)",
                "points": ["Subtitle or Brief Intro"]
            },
            {
                "title": "Slide 2 Title",
                "points": ["Bullet point 1", "Bullet point 2", "Bullet point 3"]
            },
            ...
        ]
        
        RULES:
        1. No markdown formatting (no ```json).
        2. Keep points concise (max 10 words per point).
        """
        try:
            response = self.query_engine.query(prompt)
            text = str(response).strip()
            
            if "```json" in text: text = text.replace("```json", "").replace("```", "")
            start, end = text.find('['), text.rfind(']') + 1
            return text[start:end] if start != -1 else text
            
        except Exception as e:
            return json.dumps({"error": str(e)})

rag_system = RAGEngine()