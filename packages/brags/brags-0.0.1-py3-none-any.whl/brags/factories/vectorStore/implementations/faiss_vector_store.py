import os
import logging

from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

from ....config_parser.data_types import VectorStoreConfig
from ...baseclasses.basevectorstore import BaseVectorStore


class FaissVectorStore(BaseVectorStore):
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.logger = logging.getLogger("Adora")

    def create(self, embedder, documents=None, save_if_not_local=False):
        if documents:
            try:
                # Try to load existing store
                store = FAISS.load_local(
                    self.config.persist_path,
                    embedder,
                    allow_dangerous_deserialization=self.config.allow_dangerous_deserialization,
                )
                self.logger.info("FaissVectorStore: Loaded existing vector store from disk")
            except Exception as e:
                dummy_doc = Document(page_content="dummy", metadata={"source": "dummy"})
                store = FAISS.from_documents([dummy_doc], embedder, )
                self.logger.info(f"FaissVectorStore: No existing store found, creating new one. Reason: {e}")

            for d in documents:
                if "source" not in d.metadata:
                    d.metadata["source"] = "unknown"
                    
            # Add new docs
            store.add_documents(documents)
            self.logger.info("FaissVectorStore: Added new documents to existing store")

            # Save if configured
            if save_if_not_local and self.config.persist_path:
                os.makedirs(self.config.persist_path, exist_ok=True)
                store.save_local(self.config.persist_path)
                self.logger.info("FaissVectorStore: Saving updated store to disk complete")

            return store

        else:
            self.logger.info("FaissVectorStore: Documents not provided, reading from disk")
            return FAISS.load_local(
                self.config.persist_path,
                embedder,
                allow_dangerous_deserialization=self.config.allow_dangerous_deserialization,
            )
        
    def remove_by_path(self, embedder, path: str):
        """Remove all documents with metadata['source'] == path from the FAISS store."""
        self.logger.info(f"FaissVectorStore: Removing documents from path={path}")

        store = FAISS.load_local(
            self.config.persist_path,
            embedder,
            allow_dangerous_deserialization=self.config.allow_dangerous_deserialization,
        )

        # Extract all documents
        docs = store.docstore._dict  # internal dict: {id: Document}
        filtered_docs = [doc for doc in docs.values() if doc.metadata.get("source") != path]

        # Rebuild FAISS index
        if filtered_docs:
            new_store = FAISS.from_documents(filtered_docs, store.embedding_function)
        else:
            dummy_doc = Document(page_content="dummy", metadata={"source": "dummy"})
            new_store = FAISS.from_documents([dummy_doc], store.embedding_function)

        # Save back
        if self.config.persist_path:
            os.makedirs(self.config.persist_path, exist_ok=True)
            new_store.save_local(self.config.persist_path)
            self.logger.info("FaissVectorStore: Updated store saved after deletion")

        return new_store