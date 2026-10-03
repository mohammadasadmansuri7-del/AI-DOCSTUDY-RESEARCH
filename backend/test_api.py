import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend root in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.parsers import DocumentParser, chunk_text

class TestDocStudyBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_parser_and_chunker(self):
        test_text = "This is a sample document for testing chunking. " * 50
        chunks = chunk_text(test_text, chunk_size=100, overlap=20)
        self.assertGreater(len(chunks), 0)

    def test_document_research_not_found(self):
        response = self.client.post("/api/research/query", json={
            "question": "What is the secret code of Mars?",
            "document_ids": ["non_existent_doc_id"]
        })
        self.assertEqual(response.status_code, 404)

    def test_ai_study_notes_9_sections(self):
        response = self.client.post("/api/notes/ai", json={
            "topic": "Explain normalization and compare 2NF with 3NF with examples"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("sections", data)
        sections = data["sections"]
        # Verify 9 sections are present
        expected_keys = [
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
        for key in expected_keys:
            self.assertIn(key, sections, f"Section {key} missing from AI Study Notes!")

    def test_history_endpoints(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("research", data)
        self.assertIn("notes", data)

if __name__ == "__main__":
    unittest.main()
