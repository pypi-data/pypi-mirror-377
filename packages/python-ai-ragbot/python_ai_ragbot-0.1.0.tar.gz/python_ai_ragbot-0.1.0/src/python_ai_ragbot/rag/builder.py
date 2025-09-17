from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from .loaders import load_documents


async def build_vector_store(cfg, logger=print):
    """
    Build a LangChain FAISS vector store from given sources.
    """
    files = cfg.get("sources", {}).get("files", [])
    urls = cfg.get("sources", {}).get("urls", [])

    docs = load_documents(files, urls, logger=logger)

    if not docs:
        logger("No documents loaded, vector store will be empty.")
        return None

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.get("rag", {}).get("textSplit", {}).get("chunkSize", 1000),
        chunk_overlap=cfg.get("rag", {}).get("textSplit", {}).get("chunkOverlap", 200),
    )
    split_docs = splitter.split_documents(docs)

    # Embeddings
    embeddings = OpenAIEmbeddings(
        model=cfg["openai"].get("embeddings", {}).get("model", "text-embedding-3-small")
    )

    # Vector store
    vector_store = FAISS.from_documents(split_docs, embeddings)
    logger(f"Built vector store with {len(split_docs)} chunks.")

    return vector_store.as_retriever(
        search_kwargs={"k": cfg.get("rag", {}).get("topK", 3)}
    )
