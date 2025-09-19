# graphon_client.py
import os
import time
import requests

API_BASE_URL = "https://indexer-api-485250924682.us-central1.run.app"
# API_BASE_URL = "https://indexer-api-test-485250924682.us-central1.run.app"

class GraphonClient:
    """A client library for interacting with the Graphon API."""

    def __init__(self, token: str):
        """
        Initializes the client with an API token and the base URL of the service.
        """
        api_base_url = API_BASE_URL
        self.api_base_url = api_base_url.rstrip('/')
        self._headers = {"Authorization": f"Bearer {token}"}

    def upload_video(self, video_file_path: str, show_progress: bool = True) -> str:
        """
        Gets a signed URL and uploads a video directly to Google Cloud Storage.

        Args:
            video_file_path (str): The local path to the video file.
            show_progress (bool): Whether to print progress messages.

        Returns:
            str: The GCS path (e.g., "gs://bucket/filename") of the uploaded file.
        """
        if not os.path.exists(video_file_path):
            raise FileNotFoundError(f"Video file not found at: {video_file_path}")

        file_name = os.path.basename(video_file_path)

        # --- Step 1: Get the Signed URL from our API ---
        if show_progress:
            print("Requesting secure upload URL...")
        
        url_payload = {"filename": file_name}
        get_url_endpoint = f"{self.api_base_url}/generate-upload-url"
        response = requests.post(get_url_endpoint, headers=self._headers, json=url_payload)
        response.raise_for_status()
        
        upload_info = response.json()
        signed_url = upload_info['signed_url']
        gcs_path = upload_info['gcs_path']

        # --- Step 2: Upload the file DIRECTLY to Google Cloud Storage ---
        if show_progress:
            print(f"Uploading {file_name} directly to GCS...")
        
        with open(video_file_path, 'rb') as f:
            upload_headers = {'Content-Type': 'application/octet-stream'}
            upload_response = requests.put(signed_url, headers=upload_headers, data=f)
            upload_response.raise_for_status()

        if show_progress:
            print(f"✅ Video uploaded successfully. GCS path: {gcs_path}")
        
        return gcs_path

    def index_existing_video(self, gcs_path: str, detailed: bool = False) -> str:
        """
        A convenience method that calls start_indexing for a video that
        is already in GCS. This is the primary method for a production
        workflow where uploads are handled separately.

        Args:
            gcs_path (str): The GCS path (e.g., "gs://bucket/filename") of the video.
            detailed (bool): Flag for detailed processing.

        Returns:
            str: The job_id for the newly created job.
        """
        if not gcs_path.startswith("gs://"):
            raise ValueError("gcs_path must be a valid GCS URI (e.g., 'gs://your-bucket/video.mp4')")
            
        return self.start_indexing(gcs_path, detailed=detailed)


    def start_indexing(self, gcs_path: str, detailed: bool = False, show_progress: bool = True) -> str:
        """
        Starts the indexing job for a video that is already in GCS.

        Args:
            gcs_path (str): The GCS path of the video to index.
            detailed (bool): Flag for detailed processing.
            show_progress (bool): Whether to print progress messages.

        Returns:
            str: The job_id for the newly created job.
        """
        if show_progress:
            print(f"Starting indexing job for {gcs_path}...")
            
        start_url = f"{self.api_base_url}/start-indexing"
        print(f"Start URL: {start_url}")
        start_payload = {"gcs_path": gcs_path, "detailed": detailed}
        response = requests.post(start_url, headers=self._headers, json=start_payload)
        response.raise_for_status()

        job_id = response.json()['job_id']
        if show_progress:
            print(f"✅ Job '{job_id}' started.")
            
        return job_id
        
    def get_status(self, job_id: str) -> dict:
        """Fetches the raw status of a job."""
        status_url = f"{self.api_base_url}/job-status/{job_id}"
        response = requests.get(status_url, headers=self._headers)

        if response.status_code == 404:
            return {"status": "NOT_FOUND"}
            
        response.raise_for_status()
        return response.json()

    def query(self, job_id: str, query_text: str) -> dict:
        """Sends a query to a completed index."""
        print(f"\nQuerying job '{job_id}' with: '{query_text}'")
        query_url = f"{self.api_base_url}/query"
        payload = {"job_id": job_id, "query": query_text}
        response = requests.post(query_url, headers=self._headers, json=payload)
        
        response.raise_for_status()
        return response.json()
        
    def wait_for_completion(self, job_id: str, poll_interval: int = 10):
        """Polls the job status until it is COMPLETED or FAILED."""
        print(f"\nWaiting for job '{job_id}' to complete (checking every {poll_interval}s)...")
        while True:
            status_data = self.get_status(job_id)
            current_status = status_data.get("status", "UNKNOWN")
            print(f"  -> Current status: {current_status}")

            if current_status == "COMPLETED":
                print("✅ Job completed!")
                return
            elif current_status == "FAILED":
                error_message = status_data.get('error', 'Unknown error')
                raise Exception(f"Job failed: {error_message}")
            
            time.sleep(poll_interval)