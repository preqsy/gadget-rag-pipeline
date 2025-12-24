from pprint import pprint
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import MetadataMode


## TESTING THIS SHIT!
documents = SimpleDirectoryReader("./data").load_data()

llm = Ollama(
    model="llama3.2:3b",
    request_timeout=900,
    additional_kwargs={"num_ctx": 8192, "num_predict": 400},
)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)


query_engine = query_engine = index.as_query_engine(
    llm=llm,
    similarity_top_k=2,
    response_mode="compact",
)

prompt = """
You are a CV reviewer. Give:
1) Overall score /10
2) 5 strongest points
3) 8 actionable improvements (bullets)
4) Rewrite my summary in 3 lines
Keep total under 50 words.
"""
response = query_engine.query(prompt)

pprint(response)
pprint(response.__dict__)
