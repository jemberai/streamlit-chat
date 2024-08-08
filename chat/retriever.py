import logging
from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from data_intake import DataIntakeService

class DataIntakeRetriever(BaseRetriever):
    client: DataIntakeService
    k: int
    similarityThreshold: int

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Sync implementations for retriever."""
        docs = self.client.request_query_topk(query, self.k, self.similarityThreshold)
        logging.info("Got TopK documents")
        matching_documents = []
        for doc in docs:
            logging.info(docs)
            document = Document(
                page_content=doc['content'],
                metadata={"source": "https://example.jember.ai"}
            )
            matching_documents.append(document)
        logging.info("==================")

        return matching_documents