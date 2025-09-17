import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader

def load_documents(files, urls=None, logger=print):
    """
    Load documents from a list of files (txt, md, pdf, docx).
    URLs are not implemented yet.
    """
    docs = []

    for f in files:
        if not os.path.exists(f):
            logger(f"File not found: {f}")
            continue

        ext = os.path.splitext(f)[-1].lower()
        try:
            if ext in [".txt", ".md"]:
                loader = TextLoader(f, encoding="utf-8")
            elif ext == ".pdf":
                loader = PyPDFLoader(f)
            elif ext == ".docx":
                loader = UnstructuredWordDocumentLoader(f)
            else:
                logger(f"Unsupported file type: {f}")
                continue

            file_docs = loader.load()
            docs.extend(file_docs)

        except Exception as e:
            logger(f"Failed to load {f}: {e}")

    if urls:
        logger("URL ingestion not implemented yet.")

    return docs
