# VectorX - Encrypted Vector Database

VectorX is an encrypted vector database designed for maximum security and speed. Utilizing client-side encryption with private keys, VectorX ensures data confidentiality while enabling rapid Approximate Nearest Neighbor (ANN) searches within encrypted datasets. Leveraging a proprietary algorithm, VectorX provides unparalleled performance and security for applications requiring robust vector search capabilities in an encrypted environment.

## Key Features

- **Client-side Encryption**: Vectors are encrypted using private keys before being sent to the server
- **Fast ANN Searches**: Efficient similarity searches on encrypted vector data
- **Multiple Distance Metrics**: Support for cosine, L2, and inner product distance metrics
- **Metadata Support**: Attach and search with metadata and filters
- **High Performance**: Optimized for speed and efficiency with encrypted data

## Installation

```bash
pip install vecx
```

## Quick Start

```python
from vecx.vectorx import VectorX

# Initialize client with your API token
vx = VectorX(token="your_user_id:your_api_token:region")

# Generate a secure encryption key
encryption_key = vx.generate_key()

# Create a new index
vx.create_index(
    name="my_vectors",
    dimension=1536,  # Your vector dimension
    key=encryption_key,  # Encryption key
    space_type="cosine"  # Distance metric (cosine, l2, ip)
)

# Get index reference
index = vx.get_index(name="my_vectors", key=encryption_key)

# Insert vectors
index.upsert([
    {
        "id": "doc1",
        "vector": [0.1, 0.2, 0.3, ...],  # Your vector data
        "meta": {"text": "Example document", "category": "reference"}
    }
])

# Query similar vectors
results = index.query(
    vector=[0.2, 0.3, 0.4, ...],  # Query vector
    top_k=10,
    filter={"category": "reference"}  # Optional filter
)

# Process results
for item in results:
    print(f"ID: {item['id']}, Similarity: {item['similarity']}")
    print(f"Metadata: {item['meta']}")
```

## Basic Usage

### Initializing the Client

```python
from vecx.vectorx import VectorX

# Production with specific region
vx = VectorX(token="user_id:api_token:region")
```

### Managing Indexes

```python
# List all indexes
indexes = vx.list_indexes()

# Create an index with custom parameters
vx.create_index(
    name="my_custom_index",
    dimension=384,
    key=encryption_key,
    space_type="l2",
    M=32,             # Graph connectivity parameter
    ef_con=200,       # Construction-time parameter
    use_fp16=True     # Use half-precision for storage optimization
)

# Delete an index
vx.delete_index("my_index")
```

### Working with Vectors

```python
# Get index reference
index = vx.get_index(name="my_index", key=encryption_key)

# Insert multiple vectors in a batch
index.upsert([
    {
        "id": "vec1",
        "vector": [...],  # Your vector
        "meta": {"title": "First document", "tags": ["important"]}
    },
    {
        "id": "vec2",
        "vector": [...],  # Another vector
        "filter": {"visibility": "public"}  # Optional filter values
    }
])

# Query with custom parameters
results = index.query(
    vector=[...],      # Query vector
    top_k=5,           # Number of results to return
    filter={"tags": "important"},  # Filter for matching
    ef=128,            # Runtime parameter for search quality
    include_vectors=True  # Include vector data in results
)

# Delete vectors
index.delete_vector("vec1")
index.delete_with_filter({"visibility": "public"})

# Get a specific vector
vector = index.get_vector("vec1")
```

## API Reference

### VectorX Class
- `__init__(token=None)`: Initialize with optional API token
- `set_token(token)`: Set API token
- `set_base_url(base_url)`: Set custom API endpoint
- `generate_key()`: Generate a secure encryption key
- `create_index(name, dimension, key, space_type, ...)`: Create a new index
- `list_indexes()`: List all indexes
- `delete_index(name)`: Delete an index
- `get_index(name, key)`: Get reference to an index

### Index Class
- `upsert(input_array)`: Insert or update vectors
- `query(vector, top_k, filter, ef, include_vectors)`: Search for similar vectors
- `delete_vector(id)`: Delete a vector by ID
- `delete_with_filter(filter)`: Delete vectors matching a filter
- `get_vector(id)`: Get a specific vector
- `describe()`: Get index statistics and info

## Security Considerations

- **Key Management**: Store your encryption key securely. Loss of the key will result in permanent data loss.
- **Client-Side Encryption**: All sensitive data is encrypted before transmission.
