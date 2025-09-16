# CruxGen SDK

Python SDK for CruxGen API - Create LLM-ready datasets from documents.

## Installation

```bash
pip install cruxgen-sdk
```

## Requirements

- Python 3.13+
- httpx 0.28.1+
- orjson 3.11.3+

## Quick Start

```python
from cruxgen_sdk import CruxGenSDK

# Initialize SDK
with CruxGenSDK("http://localhost:8000") as sdk:
    # Health check
    health = sdk.health_check()
    print(health)
```

## Initialization

```python
sdk = CruxGenSDK(
    base_url="http://localhost:8000",  # API base URL
    timeout=300.0                      # Request timeout in seconds
)
```

## Document Management

### Create Bucket
```python
result = sdk.create_bucket("my-bucket")
```

### Upload File
```python
result = sdk.upload_file("path/to/file.pdf", bucket_name="my-bucket")
file_id = result["response"]  # Extract file ID for further operations
```

### Delete Object
```python
result = sdk.delete_object("my-bucket", "file.pdf")
```

### Delete Bucket
```python
result = sdk.delete_bucket("my-bucket")
```

### List Objects
```python
# List all objects
objects = sdk.list_objects()

# List objects in specific bucket
objects = sdk.list_objects("my-bucket")

# List with prefix filter
objects = sdk.list_objects("my-bucket", prefix="docs/", recursive=True)
```

### List Buckets
```python
buckets = sdk.list_buckets()
```

### Get Object Info
```python
info = sdk.get_object_info("my-bucket", "file.pdf")
```

### Get File ID by Name
```python
file_info = sdk.get_file_id_by_name("file.pdf")
file_id = file_info["response"]
```

## Chunk Management

### Create Chunks
```python
result = sdk.create_chunks(file_id, "my-bucket")
```

### Get Chunks
```python
chunks = sdk.get_chunks(file_id)
chunk_texts = chunks["response"]  # List of chunk texts
```

### Delete Chunks
```python
result = sdk.delete_chunks(file_id)
```

## QA Management

### Create QA Pairs
```python
# Process all chunks
result = sdk.create_qa_pairs(file_id)

# Process specific chunk
result = sdk.create_qa_pairs(file_id, chunk_id="chunk-123")
```

### Get QA Pairs
```python
# Get as JSON
qa_pairs = sdk.get_qa_pairs(file_id)

# Download as JSONL file
qa_jsonl = sdk.get_qa_pairs(file_id, generate_jsonl=True)
if isinstance(qa_jsonl, bytes):
    with open(f"qa_pairs_{file_id}.jsonl", "wb") as f:
        f.write(qa_jsonl)
```

### Delete QA Pairs
```python
result = sdk.delete_qa_pairs(file_id)
```

## Health Check

```python
health = sdk.health_check()
status = health["status"]  # "ok" or "error"
```

## Complete Workflow Example

```python
from cruxgen_sdk import CruxGenSDK

def process_document(file_path: str):
    with CruxGenSDK("http://localhost:8000") as sdk:
        # 1. Create bucket
        sdk.create_bucket("documents")
        
        # 2. Upload document
        upload_result = sdk.upload_file(file_path, "documents")
        file_id = upload_result["response"]
        
        # 3. Create chunks
        sdk.create_chunks(file_id, "documents")
        
        # 4. Generate QA pairs
        sdk.create_qa_pairs(file_id)
        
        # 5. Export QA dataset
        qa_jsonl = sdk.get_qa_pairs(file_id, generate_jsonl=True)
        with open(f"dataset_{file_id}.jsonl", "wb") as f:
            f.write(qa_jsonl)
        
        return file_id
```

## Context Manager Usage

The SDK supports context manager protocol for automatic resource cleanup:

```python
# Recommended approach
with CruxGenSDK("http://localhost:8000") as sdk:
    result = sdk.health_check()

# Manual cleanup
sdk = CruxGenSDK("http://localhost:8000")
try:
    result = sdk.health_check()
finally:
    sdk.close()
```

## Error Handling

The SDK raises `httpx.HTTPStatusError` for HTTP errors:

```python
import httpx

try:
    result = sdk.upload_file("nonexistent.pdf")
except httpx.HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")
except FileNotFoundError:
    print("File not found")
```

## Response Format

All methods return dictionaries with standardized structure:

```python
{
    "success": true,
    "message": "Operation completed successfully",
    "status_code": 200,
    "response": {/* operation-specific data */}
}
```