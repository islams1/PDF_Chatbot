from llama_index.core import SimpleDirectoryReader
from rag_engine import index

def index_pdf(pdf_path: str):
    documents = SimpleDirectoryReader(
        input_files=[pdf_path]
    ).load_data()

    index.insert_documents(documents)
