from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
from tempfile import NamedTemporaryFile
import os

llm = LlamaCpp(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    temperature=0.1,
    top_p=0.95,
    n_threads=8,
    verbose=False
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2")


def load_docx_and_build_chain(docx_path: str):
    loader = Docx2txtLoader(docx_path)
    documents = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(texts, embedding_model)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )

    return qa_chain


def get_answer(docx_path: str, question: str) -> str:
    chain = load_docx_and_build_chain(docx_path)
    return chain.run(question)
