# rag.py
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_mistralai import MistralAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY
os.environ["USER_AGENT"] = "Mozilla/5.0"

def get_vectorstore():
    embedding_dir = "Embedding"
    enhanced_dir = "enhanced_texts"

    # Use existing Embedding folder if present
    if os.path.exists(embedding_dir):
        print("Using existing Embedding folder...")
        vectorstore = FAISS.load_local(
            embedding_dir,
            MistralAIEmbeddings(),
            allow_dangerous_deserialization=True
        )
        return vectorstore

    # Otherwise, create Embedding from enhanced/*.txt
    print("Creating new Embedding from enhanced folder...")
    docs = []
    for file in os.listdir(enhanced_dir):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(enhanced_dir, file), encoding="utf-8")
            docs.extend(loader.load())

    # Split text
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    splits = text_splitter.split_documents(docs)

    # Create embeddings (using Mistral for now)
    embeddings = MistralAIEmbeddings(model="mistral-embed")

    vectorstore = FAISS.from_documents(splits, embeddings)

    # Save locally as Embedding
    vectorstore.save_local(embedding_dir)

    return vectorstore