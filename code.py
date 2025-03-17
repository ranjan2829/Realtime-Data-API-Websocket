import os
from groq import Groq
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import numpy as np
from langchain.embeddings.base import Embeddings

# Custom embeddings class compatible with LangChain
class SimpleEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._simple_embedding(text) for text in texts]
    
    def embed_query(self, text: str) -> list[float]:
        return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> list[float]:
        words = text.lower().split()
        embedding = np.zeros(100, dtype=np.float32)  # FAISS expects float32
        for i, word in enumerate(words[:100]):
            embedding[i] = hash(word) % 100
        return embedding.tolist()

# Set up Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def create_vector_store(documents_path: str):
    try:
        if not os.path.exists(documents_path):
            raise FileNotFoundError(f"File {documents_path} not found")
            
        loader = TextLoader(documents_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        
        vectorstore = FAISS.from_documents(texts, SimpleEmbeddings())
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

def retrieve_relevant_context(query: str, vectorstore):
    try:
        docs = vectorstore.similarity_search(query, k=2)
        context = "\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"Error retrieving context: {str(e)}")
        return ""

def generate_response(query: str, context: str):
    try:
        prompt = f"""As Grok, created by xAI, I'll help you with this query using the provided context.
Context: {context}
Query: {query}
Answer: """
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Sorry, I encountered an error while processing your request."

def main():
    documents_path = "knowledge_base.txt"
    if not os.path.exists(documents_path):
        with open(documents_path, "w") as f:
            f.write("Retrieval-Augmented Generation (RAG) is a technique that combines retrieval of relevant information with generation of responses. It uses a vector store to find relevant context and then generates answers based on that context.")

    vectorstore = create_vector_store(documents_path)
    if vectorstore is None:
        return

    query = "Explain me all this text ?"
    context = retrieve_relevant_context(query, vectorstore)
    response = generate_response(query, context)
    print("Response:", response)

if __name__ == "__main__":
    main()