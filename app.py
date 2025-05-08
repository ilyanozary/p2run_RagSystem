import streamlit as st
import os
import shutil
from rag_backend import load_documents_from_dir, create_vectorstore, build_qa_chain

st.set_page_config(page_title="📄 Multi-Doc RAG", layout="centered")
st.title("📚 Multi-Document Q&A System")

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Upload section
st.subheader("📤 Upload .docx Files")
uploaded_files = st.file_uploader("Select multiple files:", type="docx", accept_multiple_files=True)

# Save files
if uploaded_files:
    for file in uploaded_files:
        with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
            f.write(file.getbuffer())
    st.success(f"{len(uploaded_files)} files uploaded.")

# Process and prepare FAISS
if st.button("📚 Process and Build Knowledge Base"):
    with st.spinner("Processing files..."):
        docs = load_documents_from_dir(UPLOAD_DIR)
        vs = create_vectorstore(docs)
        chain = build_qa_chain(vs)
        st.session_state["qa_chain"] = chain
        st.success("✅ Knowledge base is ready.")

# Ask a question
if "qa_chain" in st.session_state:
    st.subheader("❓ Ask a Question")
    question = st.text_input("Write your question:")
    if st.button("📨 Get Answer") and question.strip():
        with st.spinner("Model is generating an answer..."):
            answer = st.session_state["qa_chain"].run(question)
            st.success("Answer:")
            st.write(answer)
