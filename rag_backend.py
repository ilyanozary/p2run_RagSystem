from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
import os

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2")
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def load_documents_from_dir(dir_path):
    all_docs = []
    for filename in os.listdir(dir_path):
        if filename.endswith(".docx"):
            loader = Docx2txtLoader(os.path.join(dir_path, filename))
            all_docs.extend(loader.load())
    return all_docs

def create_vectorstore(docs):
    texts = text_splitter.split_documents(docs)
    return FAISS.from_documents(texts, embedding_model)

def load_llama_model():
    return LlamaCpp(
        model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
        n_ctx=2048,
        temperature=0.1,
        top_p=0.95,
        n_threads=8,
        verbose=False
    )

def build_qa_chain(vectorstore):
    llm = load_llama_model()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        verbose=True
    )
