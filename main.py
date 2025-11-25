import os
import uuid
import json
import shutil
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# --- APP SETUP ---
app = FastAPI(title="Ocean AI QA Agent", version="1.1")

# --- CONFIGURATION ---
# Create the 'data' folder if it doesn't exist
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

llm_gemini = None
llm_openai = None
embeddings = None
KB_REGISTRY = {}
INDEX_NAME = None

# Initialize Models (Ensure env vars are set)
try:
    llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    llm_openai = ChatOpenAI(model="gpt-4o", temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    INDEX_NAME = "qa-agent-index"

    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Store KBs in memory for this session
    KB_REGISTRY: Dict[str, PineconeVectorStore] = {}

except Exception as e:
    print(f"Startup Warning: {e}")


# --- PYDANTIC MODELS ---
class QueryRequest(BaseModel):
    kb_id: str
    query: str


class SeleniumRequest(BaseModel):
    test_case: Dict[str, Any]
    html_content: str


# --- HELPER FUNCTIONS ---

def save_and_load_file(file: UploadFile) -> List[Document]:
    """
    1. Saves the uploaded file to the 'data/' directory.
    2. Detects the file type.
    3. Loads it using the appropriate LangChain loader.
    """

    # Define the permanent path in the data folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Write the uploaded bytes to the data folder
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Now load from that saved file
    ext = os.path.splitext(file.filename)[1].lower()

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            return loader.load()
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path, encoding="utf-8")
            return loader.load()
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Convert JSON object to string for processing
            text = json.dumps(data, indent=2)
            return [Document(page_content=text, metadata={"source": file.filename})]
        else:
            # Fallback for other types (docx, etc)
            loader = UnstructuredFileLoader(file_path)
            return loader.load()
    except Exception as e:
        print(f"Error loading {file.filename}: {e}")
        return []


def clean_python_script(script: str) -> str:
    # (Same helper as before to clean LLM output)
    import re
    code_block = re.search(r"```(?:python)?(.*?)```", script, re.DOTALL)
    if code_block:
        script = code_block.group(1).strip()

    lines = [line for line in script.splitlines() if
             not (line.strip().startswith("Explanation") or line.strip().startswith("Here"))]
    return "\n".join(lines)


# --- ENDPOINTS ---

@app.post("/upload-docs")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts files from ANY client directory.
    Saves them to server's 'data/' folder.
    Processes them into Pinecone.
    """
    # print(INDEX_NAME)
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    all_docs = []
    saved_files = []

    for file in files:
        # Save to 'data/' and load docs
        docs = save_and_load_file(file)
        if docs:
            all_docs.extend(docs)
            saved_files.append(file.filename)

    if not all_docs:
        raise HTTPException(status_code=400, detail="Could not extract text from uploaded files.")

    # Split text
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(all_docs)

    # Create Knowledge Base
    kb_id = f"kb_{uuid.uuid4().hex}"

    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
        namespace=kb_id
    )

    KB_REGISTRY[kb_id] = vector_store

    return {
        "message": "Files saved to 'data/' and processed successfully.",
        "kb_id": kb_id,
        "saved_files": saved_files,
        "chunks_created": len(chunks)
    }


@app.post("/generate-test-cases")
async def generate_test_cases(request: QueryRequest):
    if request.kb_id not in KB_REGISTRY:
        raise HTTPException(status_code=404, detail="KB not found.")

    vector_store = KB_REGISTRY[request.kb_id]
    results = vector_store.similarity_search(request.query, k=5)
    context = "\n\n".join([d.page_content for d in results])

    prompt = f"""
    Role: QA Lead.
    Context: {context}
    Task: Generate structured test cases for: {request.query}.
    Format: JSON list with keys: Test_ID, Feature, Test_Scenario, Expected_Result, Grounded_In.
    """

    response = llm_gemini.invoke([HumanMessage(content=prompt)])

    # Basic cleanup
    content = response.content.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(content)
        # Handle cases where LLM wraps list in a dict key like {"cases": [...]}
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    data = data[key]
                    break
        return {"test_cases": data}
    except:
        raise HTTPException(status_code=500, detail="Failed to parse LLM JSON")


@app.post("/generate-selenium")
async def generate_selenium(request: SeleniumRequest):
    test_case_str = json.dumps(request.test_case)
    prompt = f"""
    Write a Python Selenium script for this test case:
    {test_case_str}

    HTML Context:
    {request.html_content}

    Return ONLY code.
    """
    resp = llm_openai.invoke([HumanMessage(content=prompt)])
    return {"script": clean_python_script(resp.content)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)