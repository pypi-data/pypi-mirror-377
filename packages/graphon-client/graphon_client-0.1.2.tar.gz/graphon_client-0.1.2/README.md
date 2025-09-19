# Graphon Client

A Python client library for interacting with the Graphon API for video indexing and querying.

## Installation

```bash
pip install graphon-client
```

## Usage

```python
from graphon_client import GraphonClient

# Initialize the client
client = GraphonClient(token="your-api-token")

# Index a video file
job_id = client.index("path/to/your/video.mp4")

# Wait for indexing to complete
client.wait_for_completion(job_id)

# Query the indexed video
result = client.query(job_id, "What topics are discussed in this video?")
print(result)
```

## API Reference

### GraphonClient

#### `__init__(token: str)`
Initialize the client with your API token.

#### `index(video_file_path: str, show_progress: bool = True) -> str`
Upload and index a video file. Returns a job ID.

#### `get_status(job_id: str) -> dict`
Get the current status of an indexing job.

#### `query(job_id: str, query_text: str) -> dict`
Query a completed index with a text question.

#### `wait_for_completion(job_id: str, poll_interval: int = 10)`
Wait for an indexing job to complete, polling at regular intervals.

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License
