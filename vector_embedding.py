import chromadb

chorma_client=chromadb.Client()

collection=chorma_client.create_collection("my_collection")

collection.add(
    documents=["Hello, what's up","My name is manoj"],
    metadatas=[{"source":"asking"},{"source":"statement"}],
    ids=["1","2"]
)

results=collection.query(
    query_texts=["what is your name"],
    n_results=0
)
print(results)