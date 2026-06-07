import argparse
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

import fitz


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_into_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    return paragraphs if paragraphs else [text.strip()]


def chunk_text(text: str, max_words: int = 400) -> list[str]:
    words = text.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(current) >= max_words:
            chunks.append(" ".join(current).strip())
            current = []
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def build_chunk_metadata(source_name: str, domain: str, page_number: int, chunk_index: int, text: str) -> dict:
    chunk_hash = hashlib.sha256(f"{source_name}|{domain}|{page_number}|{chunk_index}|{text}".encode("utf-8")).hexdigest()
    return {
        "id": chunk_hash,
        "source_name": source_name,
        "source_type": "pdf",
        "source_url": None,
        "domain": domain,
        "source_page": page_number,
        "title": source_name,
        "chunk_text": text,
        "chunk_hash": chunk_hash,
        "metadata": {
            "page": page_number,
            "chunk_index": chunk_index,
            "domain": domain,
        },
    }


def ingest_pdf_file(pdf_path: Path, domain: str, output_dir: Path) -> list[dict]:
    doc = fitz.open(pdf_path)
    chunks = []
    source_name = pdf_path.stem
    for page_index, page in enumerate(doc, start=1):
        raw_text = page.get_text("text")
        text = normalize_text(raw_text)
        if not text:
            continue
        paragraphs = split_into_paragraphs(text)
        for paragraph_index, paragraph in enumerate(paragraphs):
            for chunk_index, chunk_text in enumerate(chunk_text(paragraph, max_words=250), start=1):
                data = build_chunk_metadata(source_name, domain, page_index, f"{paragraph_index + 1}.{chunk_index}", chunk_text)
                chunks.append(data)
    if chunks:
        output_path = output_dir / f"{source_name}.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
    return chunks


def ingest_directory(input_dir: Path, domain: str, output_root: Path) -> int:
    output_dir = output_root / domain
    total = 0
    for pdf_file in sorted(input_dir.glob("*.pdf")):
        print(f"Processing {pdf_file.name}")
        chunks = ingest_pdf_file(pdf_file, domain, output_dir)
        total += len(chunks)
        print(f"  => {len(chunks)} chunks")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and chunk PDF files for TuVi/BatTu ingestion.")
    parser.add_argument("--input-dir", default="data", help="Root directory containing tuvi/ and battu/")
    parser.add_argument("--output-dir", default="data/ingested", help="Directory to write chunk JSON files")
    args = parser.parse_args()

    root_path = Path(args.input_dir)
    output_root = Path(args.output_dir)
    total_chunks = 0

    for domain_folder, domain_tag in [("tuvi", "TUVI"), ("battu", "BATU")]:
        source_dir = root_path / domain_folder
        if not source_dir.exists():
            continue
        print(f"Ingesting domain={domain_tag} from {source_dir}")
        total_chunks += ingest_directory(source_dir, domain_tag, output_root)

    print(f"Total chunks written: {total_chunks}")


if __name__ == "__main__":
    main()
