# 🧠 GraphRAG: Hybrid Retrieval-Augmented Generation System

A production-grade RAG system designed for **University Prospectus Analysis** (UET Lahore). This project uses a **Hybrid Retrieval Engine** combining **Knowledge Graphs (NetworkX)** for structural relationships and **Vector Search (FAISS)** for semantic understanding, orchestrated by an adaptive logic layer.

## 🚀 Key Features

- **Hybrid Retrieval:** Merges structured data (graph) with unstructured text (vector) to reduce hallucinations.
- **Dual-Search Strategy:**
    - *Precision Mode:* Extracts specific degrees (e.g., "M.Sc. AI") and filters contexts aggressively.
    - *Recall Mode:* Cleans conversational noise (e.g., "I live near UET") for broad queries.
- **Smart Sanitization:** Removes user bias (e.g., "Is AI in CS?") from search queries to prevent false-positive retrievals.
- **Chain-of-Thought Reasoning:** Encourages the LLM to follow academic logic (e.g., differentiating *Eligibility* from *Offered Programs*).
- **Tech Stack:** Python, FastAPI, Streamlit, NetworkX, FAISS, SentenceTransformers, Qwen 2.5-3B (via vLLM/OpenAI API).

---

## 🏗️ System Architecture & Logic

The system follows a modular architecture separating the Presentation, Logic, and Data layers. Below are architectural diagrams illustrating the design.

### 1. High-Level System Architecture

This diagram illustrates the Orchestration, Retrieval, and Generation layers and how the hybrid engine combines vector and graph data.

![System Architecture](docs/images/LLM%20Guided%20Query%20Pipeline-2026-01-26-080121.png)

### 2. Logic Flow (Activity Diagram)

Visualizes the system's decision-making ("The Brain") and how it selects between **High Precision** and **High Recall** strategies.

![Logic Flow](docs/images/Untitled%20diagram-2026-01-26-075952.png)

### 3. Component Architecture

Details logical components and layer separation (Presentation, Services, Business Logic, Data Access).

![Component Diagram](docs/images/LLM%20Guided%20Query%20Pipeline-2026-01-26-080329.png)

### 4. Query Execution Sequence

Shows the timeline of a request and interactions between the Orchestrator, Vector Service, and Inference Engine.

![Sequence Diagram](docs/images/LLM%20Guided%20Query%20Pipeline-2026-01-26-081051.png)

### 5. Code Structure (Class Design)

Technical view of core classes (`FrontendInterface`, `APIGateway`, `OrchestrationService`) and dependencies.

![Class Diagram](docs/images/LLM%20Guided%20Query%20Pipeline-2026-01-26-080222.png)

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YourUsername/GraphRAG-Project.git
cd GraphRAG-Project
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file in the project root with example values:

```ini
LLM_API_URL="http://localhost:8000/v1"
LLM_API_KEY="EMPTY"
```

## Usage

1. Start the backend (FastAPI):

```bash
uvicorn app.main:app --reload
```

2. Start the frontend (Streamlit):

```bash
streamlit run frontend/ui.py
```

3. Open the UI at http://localhost:8501 and use the "Ingest PDF" button to build the Graph and Vector index.

---

## Project Structure

```
GraphRAG-Project/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── services/
│   │   ├── rag_orchestrator.py # Core logic (orchestrator)
│   │   ├── vector_service.py   # FAISS wrapper
│   │   └── graph_service.py    # NetworkX wrapper
├── frontend/
│   └── ui.py                  # Streamlit interface
├── docs/
│   └── images/                # Architecture diagrams
├── notebooks/
│   └── qwen_inference.ipynb   # Research / experiments
├── data/                      # PDF storage and indexes
├── .gitignore                 # Files to exclude from Git
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

---

## Project Members and Their Roles

```
1. Ishaque Rafique [2025(S)-MS-AI-05] (Project Manager + Did Documentation)
2. M. Ali Hassan [2024-MSAIE-13] (Frontend, Make Sreamlit Web Page)
3. Kamran Wahab [2025(S)-MS-AI-03] (Project Design, Backend, API Integration)
4. M. Haroon [2025(S)-MS-AI-04] (Tester, Write Test Cases)
