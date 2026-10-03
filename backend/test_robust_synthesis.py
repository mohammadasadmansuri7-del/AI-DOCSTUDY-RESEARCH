import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend root in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.models import DocumentDB, DocumentChunkDB
from app.database import SessionLocal
from app.vector_store import vector_store

class TestRobustAnswerSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Seed sample documents
        cls.linux_doc_id = "test-doc-sublime-linux-001"
        cls.os_doc_id = "test-doc-os-theory-002"

        # 1. Procedural Document (Sublime Text on Linux)
        doc1 = DocumentDB(
            id=cls.linux_doc_id,
            filename="linux_tools_guide.pdf",
            file_path="/mock/storage/linux_tools_guide.pdf",
            file_type=".pdf",
            file_size_bytes=1048576,
            status="indexed",
            page_count=550,
            chunk_count=2
        )
        cls.db.merge(doc1)

        doc1_chunks = [
            {
                "chunk_id": "p527_c1_sublime",
                "page_number": 527,
                "content": (
                    "Installing Sublime Text on Linux\n"
                    "On most Linux systems, it is easiest to install Sublime Text from the terminal.\n"
                    "Open your terminal and execute the following commands to install the GPG key and repository:\n"
                    "wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null\n"
                    "echo 'deb https://download.sublimetext.com/apt/stable/' | sudo tee /etc/apt/sources.list.d/sublime-text.list\n"
                    "sudo apt update\n"
                    "sudo apt install sublime-text\n"
                    "This downloads and installs the official Sublime Text package on Ubuntu and Debian distributions."
                )
            }
        ]

        vector_store.upsert_chunks(
            document_id=cls.linux_doc_id,
            filename="linux_tools_guide.pdf",
            chunks_data=doc1_chunks
        )

        for item in doc1_chunks:
            db_chunk = DocumentChunkDB(
                id=f"chunk-{item['chunk_id']}",
                document_id=cls.linux_doc_id,
                chunk_id=item["chunk_id"],
                page_number=item["page_number"],
                content=item["content"]
            )
            cls.db.merge(db_chunk)

        # 2. Theoretical Document (Operating System Concepts)
        doc2 = DocumentDB(
            id=cls.os_doc_id,
            filename="os_concepts.pdf",
            file_path="/mock/storage/os_concepts.pdf",
            file_type=".pdf",
            file_size_bytes=2097152,
            status="indexed",
            page_count=100,
            chunk_count=2
        )
        cls.db.merge(doc2)

        doc2_chunks = [
            {
                "chunk_id": "p1_c1_os_def",
                "page_number": 1,
                "content": (
                    "An Operating System (OS) is core system software that manages computer hardware, software resources, "
                    "and provides common services for computer programs. It acts as an intermediary between the computer hardware and users."
                )
            }
        ]

        vector_store.upsert_chunks(
            document_id=cls.os_doc_id,
            filename="os_concepts.pdf",
            chunks_data=doc2_chunks
        )

        for item in doc2_chunks:
            db_chunk = DocumentChunkDB(
                id=f"chunk-{item['chunk_id']}",
                document_id=cls.os_doc_id,
                chunk_id=item["chunk_id"],
                page_number=item["page_number"],
                content=item["content"]
            )
            cls.db.merge(db_chunk)

        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        # Cleanup seeded records
        vector_store.delete_document_chunks(cls.linux_doc_id)
        vector_store.delete_document_chunks(cls.os_doc_id)
        cls.db.query(DocumentChunkDB).filter(DocumentChunkDB.document_id.in_([cls.linux_doc_id, cls.os_doc_id])).delete(synchronize_session=False)
        cls.db.query(DocumentDB).filter(DocumentDB.id.in_([cls.linux_doc_id, cls.os_doc_id])).delete(synchronize_session=False)
        cls.db.commit()
        cls.db.close()

    def test_procedural_question_synthesis(self):
        """Test procedural question: How to install Sublime Text on Linux."""
        question_text = "How to install Sublime Text on Linux"
        response = self.client.post("/api/research/query", json={
            "question": question_text,
            "document_ids": [self.linux_doc_id]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)

        result = data["results"][0]
        # 1. Question Title strictly reflects user prompt
        self.assertEqual(result["question"], question_text)
        # 2. Must be found in document
        self.assertTrue(result["found_in_document"])
        # 3. Answer contains cohesive context and instructions / commands
        answer = result["answer"]
        self.assertTrue(
            "Sublime Text" in answer or "terminal" in answer or "apt" in answer,
            f"Answer missing expected terms: {answer}"
        )
        # 4. Sources attached with Page 527
        self.assertGreater(len(result["sources"]), 0)
        source = result["sources"][0]
        self.assertEqual(source["page_number"], 527)
        self.assertEqual(source["filename"], "linux_tools_guide.pdf")

    def test_theoretical_question_synthesis(self):
        """Test theoretical question: What is an Operating System?"""
        question_text = "What is an Operating System?"
        response = self.client.post("/api/research/query", json={
            "question": question_text,
            "document_ids": [self.os_doc_id]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        result = data["results"][0]
        self.assertEqual(result["question"], question_text)
        self.assertTrue(result["found_in_document"])
        self.assertIn("software", result["answer"].lower())
        self.assertEqual(result["sources"][0]["page_number"], 1)

    def test_absent_question_strict_grounding(self):
        """Test absent question: Who founded Apple? -> Strict Not found in document."""
        question_text = "Who founded Apple?"
        response = self.client.post("/api/research/query", json={
            "question": question_text,
            "document_ids": [self.linux_doc_id, self.os_doc_id]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        result = data["results"][0]
        self.assertEqual(result["question"], question_text)
        self.assertFalse(result["found_in_document"])
        self.assertEqual(result["answer"], "Not found in document.")
        self.assertEqual(len(result["sources"]), 0)

if __name__ == "__main__":
    unittest.main()
