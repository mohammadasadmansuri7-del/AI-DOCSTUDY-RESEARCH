import os
import uuid
import re
from typing import List, Dict, Any, Generator
import pypdf
import docx
import pptx

class ParsedPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

class DocumentParser:
    @staticmethod
    def parse_file(file_path: str, file_type: str) -> Generator[ParsedPage, None, None]:
        ext = file_type.lower()
        if not ext.startswith("."):
            ext = "." + ext

        if ext == ".pdf":
            yield from DocumentParser._parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            yield from DocumentParser._parse_docx(file_path)
        elif ext in [".pptx", ".ppt"]:
            yield from DocumentParser._parse_pptx(file_path)
        elif ext in [".txt", ".md", ".markdown"]:
            yield from DocumentParser._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def _parse_pdf(file_path: str) -> Generator[ParsedPage, None, None]:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    yield ParsedPage(page_number=page_num, text=text.strip())

    @staticmethod
    def _parse_docx(file_path: str) -> Generator[ParsedPage, None, None]:
        doc = docx.Document(file_path)
        current_page = 1
        page_text_acc = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            # Check for page breaks or synthetic page split every ~ 500 words
            page_text_acc.append(text)
            full_text = "\n".join(page_text_acc)
            if len(full_text.split()) >= 400:
                yield ParsedPage(page_number=current_page, text=full_text)
                current_page += 1
                page_text_acc = []
        
        if page_text_acc:
            yield ParsedPage(page_number=current_page, text="\n".join(page_text_acc))

    @staticmethod
    def _parse_pptx(file_path: str) -> Generator[ParsedPage, None, None]:
        prs = pptx.Presentation(file_path)
        for slide_num, slide in enumerate(prs.slides, start=1):
            text_runs = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    text_runs.append(shape.text.strip())
            slide_text = "\n".join(text_runs).strip()
            if slide_text:
                yield ParsedPage(page_number=slide_num, text=slide_text)

    @staticmethod
    def _parse_text(file_path: str) -> Generator[ParsedPage, None, None]:
        # For large txt/md files, read line by line / chunk per 50 lines to avoid high memory usage
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = []
            page_num = 1
            for line in f:
                lines.append(line)
                if len(lines) >= 60:
                    text = "".join(lines).strip()
                    if text:
                        yield ParsedPage(page_number=page_num, text=text)
                        page_num += 1
                    lines = []
            if lines:
                text = "".join(lines).strip()
                if text:
                    yield ParsedPage(page_number=page_num, text=text)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits text into overlapping chunks using word boundaries."""
    words = text.split()
    if not words:
        return []
    
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_str = " ".join(chunk_words)
        if chunk_str.strip():
            chunks.append(chunk_str.strip())
        i += (chunk_size - overlap)
        if i <= 0:
            break
    return chunks
