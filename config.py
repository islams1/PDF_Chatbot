import os
import urllib.parse

GOOGLE_API_KEY = "AIzaSyBL3RIsGWMn62uI1yf6OEfPHoIykpHBfb8"  

DB_USER = "islamsherif243_db_user"
DB_PASS = "4DMNEy60zKE7pfXw"
DB_NAME = "pdf_index"
COLLECTION_NAME = "chunkss"

escaped_username = urllib.parse.quote_plus(DB_USER)
escaped_password = urllib.parse.quote_plus(DB_PASS)
MONGO_URI = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.gi3uu1s.mongodb.net/?appName=Cluster0&retryWrites=true&w=majority"

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)