import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

class VectorService:
    def __init__(self, persist_directory="data/chroma"):
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = persist_directory
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def add_document(self, text, metadata, collection_name):
        """
        Chunks text, embeds it, and stores it in ChromaDB.
        """
        docs = [Document(page_content=text, metadata=metadata)]
        split_docs = self.text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        return vectorstore

    def query(self, query_text, collection_name, k=3):
        """
        Retrieves the most relevant chunks for a query.
        """
        if not os.path.exists(self.persist_directory):
            return []
            
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        results = vectorstore.similarity_search(query_text, k=k)
        return [doc.page_content for doc in results]
