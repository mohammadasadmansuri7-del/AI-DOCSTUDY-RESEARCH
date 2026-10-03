# 📚 AI DocStudy & Research Platform

🔗 **Live Website:** [https://ai-docstudy-research.vercel.app](https://ai-docstudy-research.vercel.app)  
🔗 **API Docs:** [https://ai-docstudy-research.onrender.com/docs](https://ai-docstudy-research.onrender.com/docs)

---

### 🌟 Key Features
- **Strict Grounded Document Research (Zero Hallucination RAG):** PDF, DOCX, PPTX, TXT aur MD files ko ingest karke exact context-based answers deta hai. Agar document me proof nahi milta, toh galat jawab dene ke bajaye saaf bata deta hai ki context missing hai.
- **Automated 9-Part AI Study Notes Engine:** Kisi bhi complex topic par exam-ready structured study notes generate karta hai (Overview, Core Concepts, Formulas/Syntax, Comparison Matrix, Industry Applications, Edge Cases, Glossary, Practice Problems, aur Quick Revision).
- **Multi-Format Document Parsing:** Badi books, technical manuals aur slides ko split karke semantic chunks me convert karta hai.
- **Query & Document History Management:** Search history aur uploaded files ka real-time tracking aur instant delete control.

---

### 💼 Real-World Applications
- **EdTech & Exam Preparation:** Students badi textbooks upload karke fast revision aur structured notes bana sakte hain.
- **Legal & Compliance Analysis:** Contracts aur legal agreements se exact clauses aur penalties bina hallucination ke verify karne ke liye.
- **Tech Documentation Search:** Developers ke liye heavy API manuals aur technical specs se syntax aur logic dhoondhne ke liye.
- **Medical & Clinical Research:** Clinical trial papers se exact findings extract karne ke liye jahan accuracy 100% zaroori hoti hai.

---

### 💎 Business & Technical Value
- **Zero Hallucination:** Normal AI chatbots ki tarah fake ya guess kiye hue jawab nahi deta; har answer document proof ke sath hota hai.
- **Time Saving:** Ghanton ka reading work kuch seconds ke automated semantic retrieval me badal deta hai.
- **Resource Efficiency:** ONNX Runtime aur FastEmbed use karne ki wajah se heavy GPU ke bina low-memory servers (512MB RAM) par bhi high speed se run karta hai.

---

### ⚙️ How It Was Created
1. **Document Ingestion & Chunking:** PyPDF, python-docx aur python-pptx se text extract karke overlapping context windows banayi gayi.
2. **Local Vector Embeddings:** FastEmbed (ONNX Runtime) ke through text ko fast mathematical vectors me convert kiya.
3. **Similarity Search:** User ke sawal aur document chunks ke beech semantic cosine similarity match ki gayi.
4. **Strict LLM Orchestration:** High-speed LLM engine (Groq / NVIDIA) ko strict context grounding prompts ke sath connect kiya gaya.
5. **Decoupled Architecture:** Modern React/Vite UI ko FastAPI backend ke sath connect karke Vercel aur Render par deploy kiya gaya.

---

### 🛠️ Tech Stack Used
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI, Python, Uvicorn, Pydantic
- **Vector Search & RAG:** FastEmbed (ONNX Runtime), Vector Indexing
- **Document Processors:** PyPDF, python-docx, python-pptx
- **LLM Inference:** Groq API / NVIDIA Inference Engine
- **Hosting:** Vercel (Frontend) + Render (Backend)
