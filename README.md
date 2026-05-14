# 📘 Scalable RAG Pipeline with OpenSearch & Ray

This repository implements a **scalable Retrieval-Augmented Generation (RAG) pipeline** using:

- **LangChain** for document loading, text splitting, and embeddings  
- **Ray** for distributed parallel processing  
- **OpenSearch** for vector storage and retrieval  
- **HuggingFace Sentence Transformers** for embeddings  
- **PyMuPDF (fitz)** for PDF text and image extraction  

The pipeline extracts text from PDFs, chunks it, generates embeddings, and stores them in OpenSearch for efficient semantic search.

---

## 🚀 Features

- **Extraction Layer**  
  - Extracts text, tables, and images from PDFs inside a ZIP archive.  
  - Supports parallel extraction with `ThreadPoolExecutor`.  
  - Handles table parsing and text normalization.  

- **Chunking & Preprocessing Layer**  
  - Cleans text (removes unwanted line breaks, hyphenation issues).  
  - Splits text into overlapping chunks using `RecursiveCharacterTextSplitter`.  
  - Adds metadata (document name, page number, chunk number, version).  

- **Embedding Layer**  
  - Generates embeddings using HuggingFace (`all-mpnet-base-v2`) or OpenAI (`text-embedding-3-small`).  
  - Parallel embedding with Ray workers.  

- **Indexing Layer (OpenSearch)**  
  - Creates k‑NN enabled index with FAISS HNSW engine.  
  - Inserts documents individually or in bulk.  
  - Stores text, metadata, and vector embeddings.  

- **Pipeline Orchestration**  
  - Runs end‑to‑end: extraction → chunking → embedding → indexing.  
  - Parallelized with Ray for scalability.  
  - Batch processing for large datasets.  

---

## 🛠️ Project Structure

```
├── main_pipeline.py        # Full RAG pipeline (extraction → chunking → embedding → indexing)
├── opensearch_interface.py # OpenSearch client, index management, and insert functions
├── data/
│   ├── latest_dataset.zip  # Input ZIP containing PDFs
│   └── unzipped/           # Extracted PDFs
```

---

## ⚙️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages:**
- `langchain-community`
- `langchain-huggingface`
- `opensearch-py`
- `ray`
- `PyMuPDF`
- `loguru`
- `dotenv`

### 2. Configure Environment
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
LOG_LEVEL=INFO
```

### 3. OpenSearch Setup
Run OpenSearch locally (example with Docker):
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
```

Default credentials:
- **User:** `admin`  
- **Password:** `xxxxxxx`  

---

## ▶️ Usage

Run the pipeline:
```bash
python main_pipeline.py
```

Steps executed:
1. Extract PDFs from `latest_dataset.zip`.
2. Process text, tables, and images.
3. Chunk text into overlapping segments.
4. Generate embeddings in parallel.
5. Insert into OpenSearch index (`scalable-rag-index3`).

---

## 🔍 OpenSearch Index Schema

The index stores:
- **vector_field** → `knn_vector` (dimension 768, FAISS HNSW)  
- **text** → raw chunk text  
- **metadata** → version, document name, page number, chunk number  

---

## 📊 Example Workflow

1. Place your PDFs inside `data/latest_dataset.zip`.  
2. Run the pipeline.  
3. Query OpenSearch for semantic search:  

```python
from opensearchpy import OpenSearch

client = OpenSearch(hosts=[{"host":"localhost","port":9200}], http_auth=("admin","xxxxxxx"))
response = client.search(
    index="scalable-rag-index3",
    body={
        "query": {
            "knn": {
                "vector_field": {
                    "vector": [0.1, 0.2, ...],  # your query embedding
                    "k": 5
                }
            }
        }
    }
)
print(response)
```

---

## 📌 Notes

- Image summarization is scaffolded but disabled (`MULTIMODAL_SUPPORT=False`).  
- Ray workers handle embedding and chunking in parallel.  
- Bulk insert is supported but currently uses single insert for simplicity.  
- Extendable for multimodal RAG (text + image embeddings).  

---

## 🧩 Future Enhancements

- Enable multimodal support (image embeddings + summaries).  
- Add RAPTOR reranking for hierarchical retrieval.  
- Integrate feedback loop for embedding refresh.  
- Build analytics dashboard for query insights.  
