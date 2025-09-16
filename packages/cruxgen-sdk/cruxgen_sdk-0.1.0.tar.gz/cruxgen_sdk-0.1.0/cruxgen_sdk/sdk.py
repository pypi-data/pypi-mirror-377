import httpx
import orjson
from typing import Optional, Dict, Any, Union
from pathlib import Path

class CruxGenSDK:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 300.0):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return orjson.loads(response.content)

    # Document Management
    def create_bucket(self, bucket_name: str) -> Dict[str, Any]:
        return self._request("POST", "/document/create-bucket", 
                           json={"bucket_name": bucket_name})

    # def upload_file(self, file_path: str, bucket_name: str = "default-bucket") -> Dict[str, Any]:
    #     with open(file_path, "rb") as f:
    #         files = {"file": (Path(file_path).name, f, "application/octet-stream")}
    #         data = {"bucket_name": bucket_name}
    #         return self._request("POST", "/document/upload-file", files=files, data=data)
        
    def upload_file(self, file_path: str, bucket_name: str = "default-bucket") -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/octet-stream")}
            params = {"bucket_name": bucket_name}
            return self._request("POST", "/document/upload-file", files=files, params=params)

    def delete_object(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        return self._request("DELETE", "/document/delete-object",
                           json={"bucket_name": bucket_name, "object_name": object_name})

    def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        return self._request("DELETE", "/document/delete-bucket",
                           json={"bucket_name": bucket_name})

    def list_objects(self, bucket_name: Optional[str] = None, 
                    prefix: Optional[str] = None, recursive: bool = False) -> Dict[str, Any]:
        params = {"recursive": recursive}
        if bucket_name:
            params["bucket_name"] = bucket_name
        if prefix:
            params["prefix"] = prefix
        return self._request("GET", "/document/list-objects", params=params)

    def list_buckets(self) -> Dict[str, Any]:
        return self._request("POST", "/document/list-buckets")

    def get_object_info(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        params = {"bucket_name": bucket_name, "object_name": object_name}
        return self._request("GET", "/document/get-object-info", params=params)

    def get_file_id_by_name(self, file_name: str) -> Dict[str, Any]:
        params = {"file_name": file_name}
        return self._request("GET", "/document/get_file_id_from_name", params=params)

    # Chunk Management
    def create_chunks(self, file_id: str, bucket_name: str) -> Dict[str, Any]:
        return self._request("POST", "/chunks/create-chunks",
                           json={"file_id": file_id, "bucket_name": bucket_name})

    def delete_chunks(self, file_id: str) -> Dict[str, Any]:
        return self._request("DELETE", "/chunks/delete-chunks",
                           json={"file_id": file_id})

    def get_chunks(self, file_id: str) -> Dict[str, Any]:
        params = {"file_id": file_id}
        return self._request("GET", "/chunks/get-chunks", params=params)

    # QA Management
    def create_qa_pairs(self, file_id: str, chunk_id: Optional[str] = None) -> Dict[str, Any]:
        data = {"file_id": file_id}
        if chunk_id:
            data["chunk_id"] = chunk_id
        return self._request("POST", "/qa/process-chunks-to-qa", json=data)

    def delete_qa_pairs(self, file_id: str) -> Dict[str, Any]:
        return self._request("DELETE", "/qa/delete-qa-pairs",
                           json={"file_id": file_id})

    # def get_qa_pairs(self, file_id: str, generate_jsonl: bool = False) -> Dict[str, Any]:
    #     params = {"generate_jsonl": generate_jsonl}
    #     return self._request("GET", f"/qa/get-qa-pairs/{file_id}", params=params)
    
    def get_qa_pairs(self, file_id: str, generate_jsonl: bool = False) -> Union[Dict[str, Any], bytes]:
        params = {"generate_jsonl": generate_jsonl}
        response = self.client.get(f"{self.base_url}/qa/get-qa-pairs/{file_id}", params=params)
        response.raise_for_status()
        
        if generate_jsonl and response.headers.get("content-type") == "application/jsonl":
            return response.content
        
        return response.json()

    # Health Check
    def health_check(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()