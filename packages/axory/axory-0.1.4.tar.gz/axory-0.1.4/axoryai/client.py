import requests
from typing import Optional
import mimetypes

# Custom exceptions
class APIError(Exception): pass
class AuthenticationError(Exception): pass
class ConfigurationError(Exception): pass

class AxoryClient:
    def __init__(self, jwt_token: str, base_url: str = "https://axory.tech"):
        """
        jwt_token: JWT obtained from backend (/generate-jwt)
        base_url: Backend API URL
        """
        self.base_url = base_url.rstrip("/")
        self.jwt_token = jwt_token

    def analyze_file(
        self,
        file_path: str,
        content_hash: Optional[str] = None,
        has_text: bool = False
    ):
        """Upload video/image file and get analysis results"""
        url = f"{self.base_url}/analyze"
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # fallback

        if not content_hash:
            import time
            file_type = "video" if mime_type.startswith("video") else "image"
            content_hash = f"{file_type}_{int(time.time())}"

        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, mime_type)}
            data = {
                "content_hash": content_hash,
                "has_text": str(has_text).lower(),
            }
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            resp = requests.post(url, files=files, data=data, headers=headers)

        if resp.status_code == 401:
            raise AuthenticationError(resp.json().get("detail", "Unauthorized"))
        if resp.status_code == 403:
            raise ConfigurationError(resp.json().get("detail", "No active subscription or credits remaining"))
        if not resp.ok:
            raise APIError(resp.text)

        return resp.json()

    def health_check(self) -> bool:
        """Check if backend is reachable"""
        try:
            resp = requests.get(f"{self.base_url}/health")
            return resp.status_code == 200
        except Exception:
            return False
