import requests
from datetime import datetime
import os
import threading

class PrismaAPI:
    def __init__(self, auth_token: str, base_url: str = None, timeout: int = 30):
        """
        Initialize the client with an auth token.
        If base_url is not provided, will try PRISMA_API_URL env var.
        """
        self.auth_token = auth_token
        self.base_url = base_url or os.getenv("PRISMA_API_URL")
        if not self.base_url:
            raise ValueError("Base URL must be provided or set in PRISMA_API_URL")

        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})

        # Optional: verify token immediately
        self._verify_token()

    def _verify_token(self):
        """Verify the token with the server once at initialization"""
        try:
            response = self.session.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Token verification failed: {e}")

    def send_model_data(self, question: str, answer: str, model_id: int, url: str = None) -> dict:
        """
        Send model data (question, answer, model_number) to the server.
        If `url` is provided, overrides the base_url for this request.
        """
        endpoint = url or self.base_url
        payload = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "model_id": model_id,
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to send model data: {e}")
    
    def send_model_data_async(self, question: str, answer: str, model_id: int, url: str = None):
            """
            Fire-and-forget version of send_model_data.
            Uses its own requests.Session so it's thread-safe.
            """

            def _worker(q, a, m, u):
                try:
                    session = requests.Session()
                    # copy auth header
                    session.headers.update({"Authorization": f"Bearer {self.auth_token}"})

                    endpoint = u or self.base_url
                    payload = {
                        "timestamp": datetime.now().isoformat(),
                        "question": q,
                        "answer": a,
                        "model_id": m,
                    }

                    resp = session.post(endpoint, json=payload, timeout=self.timeout)
                    resp.raise_for_status()

                    print("✅ Async send success:", resp.status_code)

                except Exception as exc:
                    print("❌ Async send failed:", exc)

            thread = threading.Thread(
                target=_worker,
                args=(question, answer, model_id, url),
                daemon=True
            )
            thread.start()
            return thread

