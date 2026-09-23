from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def index_search(query, index_path="faiss_index", k=5):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    vectorstore = FAISS.load_local(
        folder_path=index_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

    results = vectorstore.similarity_search(query, k=k)

    print(f"Query: '{query}'\n")
    for i, doc in enumerate(results):
        print(f"{i+1}. {doc.page_content[:200]}...")
        print(f"   Metadata: {doc.metadata}\n")

    print(f"-----------------")

    return results

if __name__ == "__main__":

    results = index_search("Mickael Norswell", k=3)

    queries = ["Jessica Firral", "Main cafe"]
    for query in queries:
        index_search(query, k=2)
