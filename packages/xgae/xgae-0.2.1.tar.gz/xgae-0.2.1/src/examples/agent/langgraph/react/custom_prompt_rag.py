import logging
import os
from typing import List, Optional

os.environ['HF_ENDPOINT']="https://hf-mirror.com"
os.environ['TOKENIZERS_PARALLELISM']="False"

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

class CustomPromptRag:
    PROMPT_SIMILAR_SCORE = 0.8

    def __init__(self, emb_model_name: Optional[str] = "BAAI/bge-small-zh-v1.5"):
        self.emb_model_name = emb_model_name
        prompt_docs = []
        # should read from DB, load all custom prompt or COT
        prompt_docs.append(self._create_prompt_doc(
            prompt_summary="Fault location and analysis of fault causes",
            prompt_path="templates/example/fault_user_prompt.txt"
        ))
        self.vector_store = self._init_vector_store(prompt_docs)


    def _create_prompt_doc(self, prompt_summary: str, prompt_path: str)-> Document:
        return Document(
            page_content=prompt_summary,
            metadata={
                "source": prompt_path,
            }
        )


    def _init_vector_store(self, docs: List[Document]) -> Chroma:
        # FastEmbedEmbeddings first time will download BAAI/bge-small-zh-v1.5 embedding model from HF
        embeddings = FastEmbedEmbeddings(model_name=self.emb_model_name)
        return Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=None)


    def search_prompt(self, query:str)-> str | None:
        prompt_path = None
        results = self.vector_store.similarity_search_with_score(query=query, k=1)
        if results and len(results) > 0:
            doc, score = results[0]
            if score > self.PROMPT_SIMILAR_SCORE:
                logging.info(f"CustomPromptRag search: SIMILAR_SCORE: {score} > {self.PROMPT_SIMILAR_SCORE}, "
                             f"\nquery: '{query}' \nprompt_summary: '{doc.page_content}'\n")
            else:
                prompt_path = doc.metadata['source']
                logging.info(f"CustomPromptRag search: SIMILAR_SCORE: {score}, prompt_path: '{prompt_path}'")

        return prompt_path

if __name__ == "__main__":
    from xgae.utils.setup_env import setup_logging

    setup_logging()

    custom_prompt_rag = CustomPromptRag()

    querys = ["locate 10.2.3.4 fault and solution",
             "5+7"]

    for query in querys:
        logging.info("*"*50)
        logging.info(f"query: '{query}'")
        custom_prompt_rag.search_prompt(query)
