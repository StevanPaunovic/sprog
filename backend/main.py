import os
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

indexer = IndexerHelper()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        indexer.load_existing_index()
        if indexer.retriever:
            print("Index loaded successfully at startup.")
        else:
            print("Error: Index not loaded. Please start indexing manually if needed.")
        yield
    except Exception as e:
        print(f"Startup error: {str(e)}")


app = FastAPI(lifespan=lifespan)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(query: Query):
    try:
        if not indexer.retriever:
            return JSONResponse(content={"error": "Index not loaded"}, status_code=500)

        results = indexer.get_relevant_chunks(query.question)
        context_texts = " ".join([result["text"] for result in results])

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
        indexer.start_index()
        messages.append("Indexierung abgeschlossen.")
    except Exception as e:
        messages.append(f"Fehler bei der Indexierung: {str(e)}")

    return JSONResponse(content={"message": messages})


# lifespan instead: https://fastapi.tiangolo.com/advanced/events/
# @app.on_event("startup")
# async def startup_event():
#     try:
#         indexer.load_existing_index()
#         if indexer.retriever:
#             print("Index loaded successfully at startup.")
#         else:
#             print("Error: Index not loaded. Please start indexing manually if needed.")
#     except Exception as e:
#         print(f"Startup error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Chatbot API"}
