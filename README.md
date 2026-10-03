# 📚 AI DocStudy & Research Platform

An end-to-end, high-performance academic research and grounded document analysis platform. Built with a decoupled architecture featuring a **FastAPI** backend powering strict Retrieval-Augmented Generation (RAG) and ultra-fast structured notes generation, paired with a modern **React/Vite** frontend.

---

## 🌐 Live Deployments

- **Live Application:** [ai-docstudy-research.vercel.app](https://ai-docstudy-research.vercel.app)
- **Interactive API Documentation (Swagger):** [ai-docstudy-research.onrender.com/docs](https://ai-docstudy-research.onrender.com/docs)
- **Backend Health Check:** [ai-docstudy-research.onrender.com/api/health](https://ai-docstudy-research.onrender.com/api/health)

---

## ✨ Key Features

### 1. Document Research Engine (Strict Grounded RAG)
- Multi-format ingestion supporting **PDF, DOCX, PPTX, TXT, and MD** files.
- Vectorized chunk retrieval via local high-speed vector embeddings.
- Zero-hallucination policy: answers are strictly grounded within selected documents, providing transparent citations and fallback notifications when evidence is missing.

### 2. AI Study Notes Engine
- High-throughput structured academic notes generation.
- Formats outputs into an exam-oriented 9-part breakdown including:
  - Executive Overview
  - Deep-dive Core Concepts
  - Mathematical Formulations & Syntax Examples
  - Comparative Analysis
  - Real-World Industry Applications
  - Edge Cases & Common Pitfalls
  - Summary & Quick Reference

### 3. Session & Query Persistence
- Real-time research history tracking.
- Contextual deletion and granular history management.

---

## 🛠️ Architecture & Tech Stack
┌─────────────────────────────────┐
│     React + Vite Frontend       │  <── Deployed on Vercel
│   (Tailwind CSS, TypeScript)    │
└────────────────┬────────────────┘
│ REST API (JSON)
┌────────────────▼────────────────┐
│        FastAPI Backend          │  <── Deployed on Render
│  (Uvicorn, Pydantic, Python)    │
└───────┬─────────────────┬───────┘
│                 │
┌───────▼───────┐ ┌───────▼───────────┐
│ Vector Store  │ │ LLM Engine        │
│  (FastEmbed)  │ │ (Groq / NVIDIA)   │
└───────────────┘ └───────────────────┘


- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI, Python 3.11+, Uvicorn, Pydantic v2
- **Embeddings & Vector Search:** FastEmbed (ONNX Runtime-based for ultra-low memory footprint), Qdrant Client
- **Document Extractors:** `pypdf`, `python-docx`, `python-pptx`
- **Hosting & Infrastructure:** Vercel (Edge CDN Frontend), Render (Dockerized Web Service)

---

## ⚡ Engineering Highlight: Memory Optimization on Low-Resource Runtimes

During initial staging, standard HuggingFace/PyTorch dependencies (`torch`, `sentence-transformers`) resulted in container memory exhaustion on 512MB RAM free instances. 

The inference engine was refactored to use **FastEmbed (ONNX Runtime)**:
- **RAM Footprint:** Reduced from **1.2 GB+ down to < 200 MB**.
- **Cold-Start Time:** Decreased by over **65%**.
- **Embedding Throughput:** Near-instant vector operations without requiring GPU compute.

---
