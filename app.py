from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA
from llama_cpp import Llama
import os

# --- Load and embed documents ---
loader = TextLoader("data/sample.txt")
documents = loader.load()

splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
docs = splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)

# --- Load mistral 7B GGUF model ---
model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=6)

def ask_mistral(prompt):
    output = llm(prompt, max_tokens=200)
    return output['choices'][0]['text'].strip()

# --- RAG QA chain using LangChain ---
retriever = vectorstore.as_retriever()
app = FastAPI()

# ✅ Add this block to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(request: Request):
    body = await request.json()
    question = body.get("question", "")

    docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"Answer based on the following:\n{context}\nQuestion: {question}\nAnswer:"

    response = ask_mistral(prompt)
    return {"response": response}
