from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os


class IndexerHelper:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.data_path = "./RAG/data/documentation/"
        self.db_path = "./RAG/dbs/documentation/faiss_index"
        self.embeddings = self.load_embeddings()
        self.retriever = None

    def load_embeddings(self):
        try:
            return HuggingFaceEmbeddings(model_name=self.model_name, model_kwargs={'device': 'cpu'})
        except Exception as e:
            print(f"Failed to load embeddings: {e}")
            return None

    def start_index(self):
        if self.embeddings is None:
            print("Embeddings not loaded. Indexing cannot proceed.")
            return

        try:
            # PDF-Loader mit Chunk-Splitting
            loader = PyPDFDirectoryLoader(self.data_path)
            print("Loading and splitting PDF files from directory.")
            pages = loader.load_and_split()

            # Fügt Metadaten zu jedem Chunk hinzu
            for page in pages:
                # Hier werden Metadaten für den Chunk hinzugefügt
                file_name = page.metadata.get("source", "Unknown PDF")
                page_number = page.metadata.get("page", 1)
                chunk_id = f"{file_name}_page_{page_number}"

                # Aktualisiere die Metadaten des Chunks
                page.metadata["file_name"] = file_name
                page.metadata["page_number"] = page_number
                page.metadata["chunk_id"] = chunk_id

                print("Indexing chunk with metadata:", page.metadata)

            if pages:
                # FAISS-Index erstellen und speichern
                db = FAISS.from_documents(documents=pages, embedding=self.embeddings)
                db.save_local(self.db_path)
                self.retriever = db.as_retriever()
                print("Indexing completed successfully and retriever set.")
            else:
                print("No pages to index. Please verify PDF files.")

        except Exception as exc:
            print("Failed to index documents:", str(exc))

    def load_existing_index(self):
        if not os.path.exists(self.db_path):
            print(f"FAISS index not found at {self.db_path}. Run start_index() first.")
            return

        try:
            print("Loading existing FAISS index.")
            db = FAISS.load_local(self.db_path, embeddings=self.embeddings, allow_dangerous_deserialization=True)
            if isinstance(db, FAISS):
                self.retriever = db.as_retriever()
                print("Existing FAISS index and retriever loaded successfully.")
            else:
                print("Error: Loaded object is not a valid FAISS index.")
        except Exception as exc:
            print("Error loading existing index:", str(exc))

    def get_relevant_chunks(self, query):
        if not self.retriever:
            print("Retriever not set. Please run start_index or load_existing_index first.")
            return []

        try:
            results = self.retriever.invoke(query)
            relevant_chunks = []

            for result in results:
                # Extrahiere Text und Metadaten des Chunks
                text = result.page_content
                metadata = result.metadata
                relevant_chunks.append({
                    "text": text,
                    "file_name": metadata.get("file_name"),
                    "page_number": metadata.get("page_number"),
                    "chunk_id": metadata.get("chunk_id")
                })

            return relevant_chunks
        except Exception as e:
            print(f"Error retrieving relevant chunks: {e}")
            return []
