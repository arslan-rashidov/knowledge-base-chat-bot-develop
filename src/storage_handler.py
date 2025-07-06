import os

import faiss

from uuid import uuid4
from datetime import datetime

import numpy as np


class StorageHandler:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

        self.indexes = {}
        self.indexes_metadata = {}

    def add_to_index(self, index_name, chunks, chunks_metadata):
        if index_name not in self.indexes:
            index = faiss.IndexIDMap(faiss.IndexFlatL2(768))
            self.indexes[index_name] = index

            ids = np.arange(len(chunks))

            self.indexes_metadata[index_name] = {}
        else:
            ids = np.arange(self.indexes[index_name].ntotal, self.indexes[index_name].ntotal + len(chunks))

        ids_metadata = {id: metadata for id, metadata in zip(ids, chunks_metadata)}

        embeddings = self.embedding.get_embedding(chunks)

        self.indexes[index_name].add_with_ids(embeddings, ids)
        self.indexes_metadata[index_name] = self.indexes_metadata[index_name] | ids_metadata



    # Функция для создания индекса для нового пользователя
    def add_user_documents(self, user):
        documents = []

        for file in [el for el in os.listdir('user_files/' + user)]:
            text = FileHandler.read_file(f'user_files/{user}/{file}')
            print(text)
            chunks = Splitter.split_text(text)

            for chunk in chunks:
                document = Document(
                    page_content=chunk,
                    metadata={
                        "user": user,
                        "source": file  # Добавляем имя файла в метаданные
                    }
                )
                documents.append(document)

        print(documents)

        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.db.add_documents(documents=documents, ids=uuids)

    # Поиск ближайших соседей в индексе пользователя
    def query_user_documents(self, user, query, k=3, pre_k=10, use_reranker=True,
                             surrounding_k_up=2, surrounding_k_down=2, max_len=2400):
        start_time = datetime.now()
        top_documents = self.db.similarity_search(query, k=pre_k, filter={"user": user})

        if len(top_documents) == 0:
            return []

        results = []
        index_to_docstore_id = self.db.index_to_docstore_id
        doctore_id_to_index = {v: k for k, v in index_to_docstore_id.items()}

        for document in top_documents:
            document_id = document.id
            document_num_id = doctore_id_to_index[document_id]

            start_idx = max(0, document_num_id - surrounding_k_down)
            end_idx = min(len(doctore_id_to_index), document_num_id + surrounding_k_up + 1)

            relevant_chunks = self.db.get_by_ids(
                [index_to_docstore_id[id] for id in range(start_idx, end_idx)]
            )

            source = document.metadata.get('source', 'unknown')

            full_text = "... " + " ".join([chunk.page_content for chunk in relevant_chunks]) + " ..."

            file_info = {
                'text': full_text,
                'highlight': document.page_content,
                'source': source
            }
            results.append(file_info)

        if use_reranker:
            results = self.reranker.rerank_user_documents(query, results, k=k)
        else:
            results = results[:k]

        return results

