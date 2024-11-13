import os
import uuid

from langchain_community.document_loaders import PyPDFLoader


class IndexerHelper:
    def __init__(self, collection):
        self.data_path = "./RAG/data/documentation/"
        self.collection = collection

    def start_index(self, file_path):
        """
        Indexes a single PDF document by splitting it into chunks, creating embeddings, and storing them in ChromaDB.
        """
        try:
            # Load and split a single PDF file into chunks
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()

            indexed_chunks = []  # List to store indexed chunks for response

            # Process and add each page chunk to the ChromaDB collection
            for page in pages:
                file_name = page.metadata.get("source", os.path.basename(file_path))
                page_number = page.metadata.get("page", 1)
                chunk_id = f"{file_name}_page_{page_number}"

                # Update the metadata for the chunk
                metadata = {
                    "file_name": file_name,
                    "page_number": page_number,
                    "chunk_id": chunk_id
                }

                # Generate a unique ID for the document
                unique_id = str(uuid.uuid4())

                print("Indexing chunk with metadata:", page.metadata)

                # Add the document text and metadata to ChromaDB
                self.collection.add(
                    ids=[unique_id],
                    documents=[page.page_content],  # Use page.page_content to pass the text content
                    metadatas=[metadata]  # Pass metadata explicitly
                )

                # Store indexed chunk information for feedback
                indexed_chunks.append({
                    "id": unique_id,
                    "text": page.page_content,
                    "metadata": metadata
                })

                print("Indexed chunk with metadata:", metadata)

            print("Indexing completed and documents stored in ChromaDB.")
            return indexed_chunks

        except Exception as exc:
            print("Failed to index documents:", str(exc))
            return []

    def get_relevant_chunks(self, query_text):
        if not self.collection:
            print("ChromaDB collection not set. Please ensure it is initialized.")
            return []

        try:
            # Query ChromaDB for the top relevant chunks based on similarity to the query embedding
            results = self.collection.query(
                query_texts=[query_text],
                n_results=5  # Specify how many similar chunks you want to retrieve
            )
            print(f"results: {results}")

            documents = results["documents"][0]  # Access the first query's document list
            metadatas = results["metadatas"][0]  # Access the first query's metadata list

            relevant_chunks = [
                {
                    "text": text,
                    "file_name": metadata.get("file_name"),
                    "page_number": metadata.get("page_number"),
                    "chunk_id": metadata.get("chunk_id")
                }
                for text, metadata in zip(documents, metadatas)
            ]

            return relevant_chunks
        except Exception as e:
            print(f"Error retrieving relevant chunks: {e}")
            return []

    def load_existing_index(self):
        """
        Loops through all files in the data_path and indexes each one.
        """
        indexed_files = []
        for filename in os.listdir(self.data_path):
            file_path = os.path.join(self.data_path, filename)
            if os.path.isfile(file_path) and filename.endswith(".pdf"):
                print(f"Indexing file: {filename}")
                indexed_chunks = self.start_index(file_path)
                indexed_files.extend(indexed_chunks)
        return indexed_files
