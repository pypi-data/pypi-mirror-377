from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

async def query_rag(vector_store, question, cfg, logger=print):
    """
    Query the RAG pipeline using LangChain Expression Language (LCEL).
    """

    if not question or not question.strip():
        logger("[DEBUG] Empty question provided")
        return "No question provided."

    if not vector_store:
        logger("[DEBUG] No vector store available")
        return f"Answer (no knowledge base): {question}"

    try:
        logger("[DEBUG] Initializing ChatOpenAI...")
        llm = ChatOpenAI(
            model=cfg.get("openai", {}).get("chat", {}).get("model", "gpt-4o"),
            temperature=cfg.get("openai", {}).get("chat", {}).get("temperature", 0.3),
            openai_api_key=cfg.get("openai", {}).get("apiKey"),
        )
        logger(f"[DEBUG] LLM initialized with model={llm.model_name}")

        # Retriever
        retriever  = vector_store
        logger("[DEBUG] Retriever created")

        # Test retriever separately
        try:
            retrieved_docs = await retriever.ainvoke(question)
            logger(f"[DEBUG] Retrieved {len(retrieved_docs)} docs")
            for i, doc in enumerate(retrieved_docs[:2]):
                logger(f"[DEBUG] Doc {i+1} preview: {doc.page_content[:200]}...")
        except Exception as re:
            logger(f"[DEBUG] Retriever error: {re}")

        # Prompt
        prompt_template = cfg.get("openai", {}).get("chat", {}).get(
            "promptTemplate",
            (
                "You are a helpful assistant. Use the following context to answer the question.\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Answer:"
            ),
        )
        prompt = PromptTemplate.from_template(prompt_template)
        logger(f"[DEBUG] Prompt template: {prompt_template[:100]}...")

        # RAG chain
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        logger("[DEBUG] RAG chain built successfully")

        # Async invoke
        logger(f"[DEBUG] Invoking RAG chain with question: {question}")
        result = await rag_chain.ainvoke(question)
        logger(f"[DEBUG] Got result: {result[:200]}...")

        return result

    except Exception as e:
        logger(f"[ERROR] Exception in query_rag: {e}")
        return f"Answer (fallback): {question}"
