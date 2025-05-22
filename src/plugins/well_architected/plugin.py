import logging
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from semantic_kernel.functions import kernel_function
from PyPDF2 import PdfReader

class WellArchitectedPlugin:
    def __init__(self):
        self.storage_path = os.path.join("/workspaces/adr-agent/","src","plugins","well_architected")
        self.pdf_path = os.path.join(self.storage_path, "azure-well-architected.pdf")
        self.index_path = os.path.join(self.storage_path, "well_architected.index")
        self.texts_path = os.path.join(self.storage_path, "well_architected_texts.npy")

        if os.path.exists(self.index_path) and os.path.exists(self.texts_path):
            logging.info("Loading existing FAISS index and texts...")
            self.index = faiss.read_index(self.index_path)
            self.texts = np.load(self.texts_path, allow_pickle=True).tolist()
        else:
            logging.info("Initializing FAISS index and SentenceTransformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = None
            self.texts = []
    
    def vectorize_pdf(self):
        if self.index is not None and self.texts:
            logging.info("FAISS index and texts already loaded. Skipping vectorization.")
            return

        if not os.path.exists(self.pdf_path):
            logging.error(f"PDF file not found at {self.pdf_path}")
            return
        
        logging.info("Loading PDF...")
        reader = PdfReader(self.pdf_path)

        logging.info("Extracting text from PDF...")
        all_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
        # Chunk text for vectorization (simple split by paragraphs)
        logging.info("Chunking text...")
        chunks = []
        for text in all_text:
            chunks.extend([p for p in text.split("\n\n") if p.strip()])
        if not chunks:
            return "No text found in PDF."
        
        logging.info("Vectorizing text...")
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.texts = chunks

        logging.info("Storing index and texts...")
        
        faiss.write_index(self.index, self.index_path)
        np.save(self.texts_path, np.array(self.texts, dtype=object))

        logging.info(f"Vectorized and stored {len(chunks)} chunks in FAISS index.")
