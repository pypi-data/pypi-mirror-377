# VeDB

This notebook covers how to get started with the VeDB.

## Setup

To access VeDB you'll need to create a/an ByteDance account, get an API key, and install the `langchain-vedb-link` integration package.
```
%pip install -qU "langchain-vedb-link>=MINIMUM_VERSION"
```

## Initialization
import EmbeddingTabs from "@theme/EmbeddingTabs";
``` 
extra_column = {"source": "VARCHAR(255)"}   # Define the field information to be added to metadata

client_config = {"host": 'xxx.xxx.xxx.xxx',  # e.g., '192.168.1.88'
                 "port": 12345,
                 "user": 'vector_user',
                 "password": '123456',  # Leave empty if no password was set during authorization
                 "database": 'vectorStoreTest',  # Use your actual database name
                 "table_name": 'langchain_vector_test',  # Set an existing table name or initialize a new one
                 "charset": 'utf8mb4',
                 "metadata_columns": extra_column}     # Additional metadata columns
vector_store = ByteDanceVectorStore(embeddings, client_config)
```

## Manage vector store
### Add items to vector store
``` 
from langchain_core.documents import Document

document_1 = Document(page_content="foo", metadata={"source": "https://example.com"})

document_2 = Document(page_content="bar", metadata={"source": "https://example.com"})

document_3 = Document(page_content="baz", metadata={"source": "https://example.com"})

documents = [document_1, document_2, document_3]

vector_store.add_documents(documents=documents, ids=["1", "2", "3"])
```

You can also use the from_text function to directly instantiate a vector store from a document.
```
docs = ["foo","bar","bar"]

metadatas = [{"source": "https://example.com"},{"source": "https://example.com"},{"source": "https://example.com"}]

vector_store = ByteDanceVectorStore.from_texts(texts=docs, embedding=embeddings, metadatas=metadatas, client_config=client_config)
```

### Delete items from vector store
```
vector_store.delete(ids=["3"])
```

### Update items in vector store
```
updated_document_1 = Document(
    id = "1", page_content="qux", metadata={"source": "https://another-example.com"}
)

vector_store.update_document(document=updated_document_1)
```

### Get documents by ids
You can directly get a specific document by its ID.
```
results = vector_store.get_by_ids(["1", "2", "3"])
for doc in results:
     print(f"* {doc.id} {doc.page_content} [{doc.metadata}]")
```

## Query vector store
Once your vector store has been created and the relevant documents have been added, you will most likely wish to query it during the running of your chain or agent.
### Filtering Support
The vectorstore supports a set of filters that can be applied against the metadata fields of the documents.

| Operator   | Meaning/Category                  |
|------------|------------------------------------|
| `$eq`      | Equality (`==`)                    |
| `$ne`      | Inequality (`!=`)                  |
| `$lt`      | Less than (`<`)                    |
| `$lte`     | Less than or equal (`<=`)          |
| `$gt`      | Greater than (`>`)                 |
| `$gte`     | Greater than or equal (`>=`)       |
| `$in`      | Special Case (`in`)                |
| `$nin`     | Special Case (`not in`)            |
| `$between` | Special Case (`between`)           |
| `$exists`  | Exists (`IS [NOT] NULL`)           |
| `$like`    | Text (`like`)                      |
| `$ilike`   | Text (case-insensitive `like`)     |
| `$and`     | Logical (`and`)                    |
| `$or`      | Logical (`or`)                     |

### Query directly
A simple similarity search can be performed in the following way.
```
results = vector_store.similarity_search(
    query="thud", k=1, filter={"source": "https://example.com"}
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
```

You can run the following to execute a similarity search and get the corresponding scores
```
results = vector_store.similarity_search_with_score(
    query="thud", k=1, filter={"source": "https://example.com"}    
)
for doc, score in results:
    print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")
```
If you provide a dict with multiple fields, but no operators, the top level will be interpreted as a logical AND filter
```
results = vector_store.similarity_search_with_score(
    query="thud", 
    k=10, 
    filter={"year": {"$in": [2004, 2022]}, "topic": {"$eq": "magic"}},
)
```
```
results = vector_store.similarity_search_with_score(
    query="thud", 
    k=10, 
    filter={
         "$and":[
         {"year": {"$in": [2004, 2025]}}, 
         {"topic": {"$eq": "magic"}},
         ]
     },
)
```
## Limitations
After adding documents, the system builds the ANN index asynchronously in the background. Therefore, you need to wait a short period between adding documents and performing similarity searches. 
You can use sleep to pause for a while. To prevent potential crashes, you can run the following between adding documents and performing a similarity search.
```
vector_store.close()
```

---
# ❗️Needs to be modified
## API reference
For detailed documentation of all ByteDanceVectorStore features and configurations head to the API reference: https://api.python.langchain.com/en/latest/vectorstores/langchain_vedb_link.vectorstores.VeDB.html
## Related
- Vector store conceptual guide
- Vector store how-to guides