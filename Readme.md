# 🌊 Ocean AI: Autonomous QA Agent

Ocean AI is an autonomous Quality Assurance agent powered by LLMs (Gemini & GPT-4o), RAG (Retrieval-Augmented Generation), and Pinecone vector database. It helps QA engineers automatically generate test cases from documentation and convert those test cases into executable Selenium Python scripts.

---

## 🚀 Features

* **Knowledge Base Creation**
  Upload PDF, TXT, MD, or JSON files to build a specialized knowledge base.

* **Test Case Generation**
  Automatically generates positive and negative test cases based on user queries and uploaded documents.

* **Selenium Script Generation**
  Converts selected test cases into ready-to-run Python Selenium scripts using provided HTML context.

* **Full-Stack Architecture**

  * **Backend:** FastAPI (handling RAG logic, Pinecone indexing, and LLM calls)
  * **Frontend:** Streamlit (user-friendly interface for uploading docs and interacting with the agent)

---

## 🛠️ Prerequisites

* Python 3.10+
* API Keys (Required):

  * `OPENAI_API_KEY` – Selenium script generation
  * `GOOGLE_API_KEY` – Test case generation via Gemini
  * `PINECONE_API_KEY` – Vector Database storage
  * `HF_TOKEN` – HuggingFace token for embeddings

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Autonomous-QA_Agent-ocean-ai
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory and add your API keys:

```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
PINECONE_API_KEY=your_pinecone_key
HF_TOKEN=your_huggingface_token
```

---

## 🏃‍♂️ How to Run the Application

You need to run the Backend and Frontend in two separate terminals.

### Terminal 1: Start the Backend (FastAPI)

This service handles file uploads, vector storage, and LLM processing:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at:

```
http://localhost:8000
```

### Terminal 2: Start the Frontend (Streamlit)

This launches the web interface:

```bash
streamlit run frontend.py
```

App UI available at:

```
http://localhost:8501
```

---

## 📖 Usage Workflow

### 1. Upload Documents

* Go to the Sidebar in the Streamlit UI
* Upload project documentation such as:

  * `product_specs.md`
  * `ui_ux_guide.txt`
* Click **Upload & Build KB**
* Files will be chunked and stored as embeddings in Pinecone

---

### 2. Generate Test Cases

* Enter a requirement query in the main view
  Example:

  ```
  Generate positive and negative test cases for the discount code feature
  ```
* Click **Generate Test Cases**
* Review structured test cases in the displayed table

---

### 3. Generate Selenium Script

* Select a test case from the dropdown
* Paste the HTML snippet from `checkout.html` into the **HTML Context** box
* Click **Generate Python Selenium Code**
* Download or copy the generated script

---

## 📂 Included Support Documents

This repository includes sample files for immediate testing:

| File Name          | Description                                                           | Usage Context                                         |
| ------------------ | --------------------------------------------------------------------- | ----------------------------------------------------- |
| product_specs.md   | Defines business logic for discounts, shipping costs, and order rules | Upload to KB for functional test cases                |
| ui_ux_guide.txt    | Contains UI design rules like colors and button styles                | Upload for UI/visual test cases                       |
| api_endpoints.json | Describes backend API structure                                       | Upload for API integration test generation            |
| checkout.html      | Sample E-Commerce checkout page                                       | Do NOT upload to KB; use as HTML context for Selenium |

---

## 🧩 Project Structure

```
├── main.py              # FastAPI Backend Entry Point
├── frontend.py          # Streamlit Frontend UI
├── requirements.txt     # Python Dependencies
├── .env                 # API Keys (Not included in repo)
├── checkout.html        # Sample HTML for Selenium testing
└── data/                # Directory where uploaded files are saved
    ├── product_specs.md
    ├── ui_ux_guide.txt
    └── api_endpoints.json
```

---

## ⚠️ Troubleshooting

* **Connection Error**
  If Streamlit says *Cannot connect to Backend*, ensure `main.py` is running on port 8000.

* **Startup Warning**
  If you see `sentence-transformers` warnings, install it explicitly:

  ```bash
  pip install sentence-transformers
  ```

* **Pinecone Error**
  Ensure:

  * Your `PINECONE_API_KEY` is valid
  * Index name in `main.py` matches your Pinecone console

---

backend deployed on google cloud 
front deployed on streamlit cloud 

google collab link for reference https://colab.research.google.com/drive/1TAJISXaLMTrfCOyg9Y9VbmuLpSoA7UUY?usp=sharing


