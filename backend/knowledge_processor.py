import os
import pandas as pd
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, CSVLoader
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb


class KnowledgeProcessor:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the knowledge processor with vector database."""
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing ChromaDB vectorstore."""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("Loaded existing vectorstore")
        except Exception as e:
            print(f"Creating new vectorstore: {e}")
            # Create new vectorstore
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def load_text_file(self, file_path: str) -> List[Document]:
        """Load and split text file into documents."""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)
            print(f"Loaded {len(splits)} chunks from {file_path}")
            return splits
        except Exception as e:
            print(f"Error loading text file {file_path}: {e}")
            return []
    
    def load_csv_file(self, file_path: str, source_column: Optional[str] = None) -> List[Document]:
        """Load and process CSV file into documents."""
        try:
            df = pd.read_csv(file_path)
            documents = []
            
            for index, row in df.iterrows():
                # Convert row to text
                content = ""
                for col, value in row.items():
                    content += f"{col}: {value}\n"
                
                # Create document
                metadata = {
                    "source": file_path,
                    "row": index,
                }
                if source_column and source_column in df.columns:
                    metadata["title"] = str(row[source_column])
                
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            
            # Split documents if they're too long
            splits = self.text_splitter.split_documents(documents)
            print(f"Loaded {len(splits)} chunks from CSV {file_path}")
            return splits
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def add_documents_to_vectorstore(self, documents: List[Document]):
        """Add documents to the vector database."""
        if documents:
            try:
                self.vectorstore.add_documents(documents)
                self.vectorstore.persist()
                print(f"Added {len(documents)} documents to vectorstore")
            except Exception as e:
                print(f"Error adding documents to vectorstore: {e}")
    
    def process_knowledge_base(self, file_paths: List[str]):
        """Process multiple knowledge base files."""
        all_documents = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.txt':
                documents = self.load_text_file(file_path)
            elif file_extension == '.csv':
                documents = self.load_csv_file(file_path)
            else:
                print(f"Unsupported file type: {file_extension}")
                continue
            
            all_documents.extend(documents)
        
        if all_documents:
            self.add_documents_to_vectorstore(all_documents)
            return True
        return False
    
    def get_vectorstore(self):
        """Return the vectorstore for use in retrieval."""
        return self.vectorstore
    
    def search_similar_documents(self, query: str, k: int = 3) -> List[Document]:
        """Search for similar documents in the vectorstore."""
        try:
            if self.vectorstore:
                docs = self.vectorstore.similarity_search(query, k=k)
                return docs
            return []
        except Exception as e:
            print(f"Error searching documents: {e}")
            return [] 