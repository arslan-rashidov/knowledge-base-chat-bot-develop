from src import llm_handler
from src.embeddings_handler import EmbeddingModel
from src.splitters.semantic_chunking import semantic_chunking

class ChunkHandler:
    def __init__(self, documents, llm_handler=None):
        self.embedding_model = EmbeddingModel()
        self.documents = documents

        self.llm_handler = llm_handler

    def get_chunks(self, document):
        chunks = []

        chunk_texts = self.split_document(document)

        for text in chunk_texts:
            chunk = {'text': text}

            if len(text) > 100:
                questions_chunk = self.llm_handler.get_text_questions(text)
                chunk['questions'] = questions_chunk
            else:
                chunk['questions'] = []

            chunks.append(chunk)

        return chunks

    def split_document(self, document):
        semantic_chunks = semantic_chunking(document.get_text(), self.embedding_model)
        return semantic_chunks

    def preprocess_documents(self):
        all_chunks = []

        for document in self.documents:
            document_chunks = self.get_chunks(document)
            all_chunks.extend(document_chunks)

        return all_chunks

