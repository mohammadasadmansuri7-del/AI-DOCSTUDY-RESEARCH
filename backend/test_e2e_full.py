import os
import sys
import time
import httpx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_full_user_journey():
    client = httpx.Client(timeout=45.0)

    print("[1] Checking Backend Health...")
    r = client.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(" -> Health check passed:", r.json())

    # Create sample study document
    sample_path = "sample_os_study.txt"
    sample_content = (
        "Operating System Overview & Memory Management\n"
        "Page 1: Definition of Operating System\n"
        "An Operating System (OS) is software that acts as an interface between computer hardware and the user.\n"
        "Key functions include Process Management, Memory Management, File System Management, and Device Management.\n\n"
        "Page 2: Deadlock and CPU Scheduling\n"
        "Deadlock is a set of blocked processes each holding a resource and waiting for another resource held by another process.\n"
        "Four necessary conditions for Deadlock: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.\n"
        "CPU scheduling algorithms include FCFS, Shortest Job First (SJF), Round Robin (RR), and Priority Scheduling.\n"
    )
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(sample_content)

    print("\n[2] Testing Document Upload...")
    with open(sample_path, "rb") as f:
        files = {"file": ("sample_os_study.txt", f, "text/plain")}
        r = client.post(f"{BASE_URL}/api/documents/upload", files=files)
    assert r.status_code == 200, f"Upload failed: {r.text}"
    doc_data = r.json()
    doc_id = doc_data["id"]
    print(" -> Document uploaded successfully. ID:", doc_id)

    # Wait for ingestion to complete
    print("\n[3] Waiting for Document Ingestion & Qdrant Indexing...")
    status = "processing"
    for _ in range(15):
        time.sleep(1)
        r = client.get(f"{BASE_URL}/api/documents/{doc_id}")
        if r.status_code == 200:
            status = r.json()["status"]
            print(f"    Status: {status} (Chunks: {r.json().get('chunk_count', 0)})")
            if status == "indexed":
                break
    assert status == "indexed", "Document failed to reach 'indexed' status."

    print("\n[4] Testing Document Research (Multi-Question + Strict Grounding)...")
    multi_prompt = (
        "1. What is an Operating System?\n"
        "2. What are the 4 conditions for Deadlock?\n"
        "3. What is Quantum Physics Superposition?"
    )
    r = client.post(f"{BASE_URL}/api/research/query", json={
        "question": multi_prompt,
        "document_ids": [doc_id]
    })
    assert r.status_code == 200, f"Research query failed: {r.text}"
    research_res = r.json()["results"]
    print(f" -> Received {len(research_res)} research answers:")

    for idx, ans in enumerate(research_res, start=1):
        print(f"\n   Q{idx}: {ans['question']}")
        print(f"   A: {ans['answer'][:120]}...")
        print(f"   Found in Document: {ans['found_in_document']}")
        print(f"   Sources: {len(ans['sources'])}")

    # Invariant Verification: Question 3 MUST return "Not found in document."
    q3_result = research_res[2]
    assert q3_result["found_in_document"] is False or "Not found in document" in q3_result["answer"], \
        f"Strict grounding invariant broken for Q3! Expected 'Not found in document.', got: {q3_result['answer']}"
    print(" -> Strict Grounding Invariant Verified: Missing info properly yields 'Not found in document.'")

    print("\n[5] Testing AI Study Notes (9-Part Structured Notes with Complex Question)...")
    complex_prompt = "Explain normalization and compare 2NF with 3NF with examples"
    r = client.post(f"{BASE_URL}/api/notes/ai", json={
        "topic": complex_prompt
    })
    assert r.status_code == 200, f"AI notes failed: {r.text}"
    ai_notes = r.json()
    print(" -> AI Study Notes generated:", ai_notes["title"])
    sections = ai_notes["sections"]
    print("    Sections generated:", list(sections.keys()))

    expected_sections = [
        "📌 Topic & Overview",
        "📖 Definition & Core Principles",
        "⚙️ How It Works / Architectural Breakdown",
        "🔑 Key Concepts & Bullet Points",
        "📝 Important Technical Terms",
        "💡 Real-World Examples / Code Walkthrough / Diagrams",
        "⚖️ Advantages vs. Limitations / Comparison Table",
        "🎯 Exam-Oriented Points & Common Pitfalls",
        "⚡ Quick Revision Summary (Cheatsheet)"
    ]
    for s in expected_sections:
        assert s in sections, f"Missing section '{s}' in AI notes!"
    print(" -> All 9 required sections successfully validated!")

    print("\n[6] Testing History Persistence API...")
    r = client.get(f"{BASE_URL}/api/history")
    assert r.status_code == 200, f"History fetch failed: {r.text}"
    history_data = r.json()
    print(f" -> Found {len(history_data['research'])} research history items and {len(history_data['notes'])} notes history items.")
    assert len(history_data["research"]) > 0, "Research history was not saved!"
    assert len(history_data["notes"]) > 0, "Notes history was not saved!"

    # Verify deleting single research history item
    first_res_id = history_data["research"][0]["id"]
    r_del = client.delete(f"{BASE_URL}/api/history/research/{first_res_id}")
    assert r_del.status_code == 200, f"Failed to delete research history item: {r_del.text}"
    print(" -> Successfully deleted single research history item.")

    # Clean up test file
    if os.path.exists(sample_path):
        os.remove(sample_path)

    print("\n=======================================================")
    print("SUCCESS: ALL TWO-MODE & HISTORY INVARIANTS VERIFIED!")
    print("=======================================================")

if __name__ == "__main__":
    test_full_user_journey()
