import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from indexer_helper import IndexerHelper
import openai
from contextlib import asynccontextmanager
import traceback

load_dotenv(override=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = os.getenv("OPENAI_API_TYPE", "openai")

client = chromadb.HttpClient(host=os.getenv('CHROMA_HOST'), port=os.getenv('CHROMA_PORT'))  # ChromaDB service details

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai.api_key,
                model_name="text-embedding-ada-002")

collection = client.get_or_create_collection(name="my_collection",embedding_function=openai_ef)

indexer = IndexerHelper(collection=collection)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Check if the ChromaDB collection is ready
        if indexer.collection:
            print("ChromaDB collection is ready at startup.")
        else:
            print("Error: ChromaDB collection not initialized. Please check your setup.")
        yield
    except Exception as e:
        print(f"Startup error: {str(e)}")


app = FastAPI(lifespan=lifespan)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(query: Query):
    try:
        results = indexer.get_relevant_chunks(query.question)
        context_texts = " ".join([result["text"] for result in results])

        if not results:
            return JSONResponse(content={"error": "No relevant chunks found."}, status_code=404)

        openai_response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant for answering questions based on provided context."},
                {"role": "user", "content": f"Context: {context_texts}\n\nQuestion: {query.question}"}
            ],
            max_tokens=2000
        )

        answer_text = openai_response.choices[0].message.content.strip()

        return JSONResponse(content={
            "answer": answer_text,
            "used_chunks": results
        })
    except Exception as e:
        print("Error in /ask endpoint:", str(e))
        traceback.print_exc()  # Print the full traceback
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/upload-pdf")
async def upload_pdf(files: list[UploadFile] = File(...)):
    messages = []
    for file in files:
        file_location = f"./RAG/data/documentation/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

        with open(file_location, "wb") as f:
            f.write(await file.read())

        messages.append(f"{file.filename} erfolgreich hochgeladen")

    try:
        indexed_data = indexer.start_index()
        for chunk in indexed_data:
            collection.add(
                ids=[chunk["id"]],
                documents=[chunk["text"]],
                metadatas=[chunk["metadata"]]
            )
        messages.append("Indexierung abgeschlossen und in ChromaDB gespeichert.")
    except Exception as e:
        messages.append(f"Fehler bei der Indexierung: {str(e)}")

    return JSONResponse(content={"message": messages})


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Chatbot API"}


@app.get("/list-documents")
async def list_documents():
    try:
        # Fetch all documents (or a sample) from ChromaDB
        response = collection.query(query_texts=["what is stock prediction"],where_document={"$contains":"stock"}, n_results=10)

        return JSONResponse(content=response)
    except Exception as e:
        error_details = {"error": str(e)}
        if hasattr(e, 'response'):
            error_details["response"] = e.response
        if hasattr(e, 'body'):
            error_details["body"] = e.body
        return JSONResponse(content=error_details, status_code=500)
