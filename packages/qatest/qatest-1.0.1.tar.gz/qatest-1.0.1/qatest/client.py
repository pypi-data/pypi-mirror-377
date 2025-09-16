"""API client for QATest service."""

from typing import Any, Dict, List

import requests
from rich.console import Console

from .models import TestCase

console = Console()


class QATestClient:
    """Client for interacting with QATest API."""

    def __init__(self, api_endpoint: str, project_key: str):
        """
        Initialize the QATest client.
        
        Args:
            api_endpoint: API endpoint URL from configuration
            project_key: Project API key from configuration
        """
        if not api_endpoint:
            raise ValueError(
                "API endpoint not configured. Please configure it in qatest-config.yml"
            )
        if not project_key:
            raise ValueError(
                "Project key not configured. Please configure it in qatest-config.yml"
            )
        self.api_endpoint = api_endpoint.rstrip('/')
        self.project_key = project_key

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "qatest-cli/0.1.0",
            "X-API-Key": self.project_key
        })

    def bulk_upload(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Upload multiple test cases to the API.
        
        Args:
            test_cases: List of TestCase objects to upload
        
        Returns:
            Response from the API
        
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.api_endpoint}/api/import/"

        # Convert test cases to dictionaries and include project_key only
        payload = {
            "project_key": self.project_key,
            "test_cases": [
                test_case.model_dump(exclude_none=True)
                for test_case in test_cases
            ]
        }

        try:
            # Disable auto-redirect to handle it manually and preserve POST method
            response = self.session.post(url, json=payload, timeout=30, allow_redirects=False)
            
            # Handle redirect manually to ensure POST is preserved
            if response.status_code in [301, 302, 307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    # If the server redirects from HTTPS to HTTP, force HTTPS
                    # This is a workaround for a server misconfiguration
                    if url.startswith('https://') and redirect_url.startswith('http://'):
                        redirect_url = redirect_url.replace('http://', 'https://', 1)
                    # Follow the redirect with POST
                    response = self.session.post(redirect_url, json=payload, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as err:
            raise ConnectionError(
                f"Failed to connect to API endpoint: {self.api_endpoint}\n"
                "Please check your internet connection and API endpoint configuration."
            ) from err
        except requests.exceptions.Timeout as err:
            raise TimeoutError(
                "Request to API timed out. Please try again later."
            ) from err
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise ValueError(f"Bad request: {e.response.text}") from e
            elif e.response.status_code == 401:
                raise PermissionError("Authentication failed. Please check your credentials.") from e
            elif e.response.status_code == 403:
                raise PermissionError("Access forbidden. You don't have permission to upload test cases.") from e
            elif e.response.status_code == 404:
                raise ValueError(f"API endpoint not found: {url}") from e
            elif e.response.status_code >= 500:
                raise RuntimeError(f"Server error ({e.response.status_code}): {e.response.text}") from e
            else:
                raise RuntimeError(f"HTTP error ({e.response.status_code}): {e.response.text}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}") from e

    def clear_test_cases(self) -> Dict[str, Any]:
        """
        Clear existing test cases for the project.
        
        Returns:
            Response from the API
        
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.api_endpoint}/api/import/clear/"
        
        # Include project_key for authentication
        payload = {
            "project_key": self.project_key
        }
        
        try:
            # Disable auto-redirect to handle it manually and preserve POST method
            response = self.session.post(url, json=payload, timeout=30, allow_redirects=False)
            
            # Handle redirect manually to ensure POST is preserved
            if response.status_code in [301, 302, 307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    # If the server redirects from HTTPS to HTTP, force HTTPS
                    # This is a workaround for a server misconfiguration
                    if url.startswith('https://') and redirect_url.startswith('http://'):
                        redirect_url = redirect_url.replace('http://', 'https://', 1)
                    # Follow the redirect with POST
                    response = self.session.post(redirect_url, json=payload, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as err:
            raise ConnectionError(
                f"Failed to connect to API endpoint: {self.api_endpoint}\n"
                "Please check your internet connection and API endpoint configuration."
            ) from err
        except requests.exceptions.Timeout as err:
            raise TimeoutError(
                "Request to API timed out. Please try again later."
            ) from err
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise ValueError(f"Bad request: {e.response.text}") from e
            elif e.response.status_code == 401:
                raise PermissionError("Authentication failed. Please check your credentials.") from e
            elif e.response.status_code == 403:
                raise PermissionError("Access forbidden. You don't have permission to clear test cases.") from e
            elif e.response.status_code == 404:
                raise ValueError(f"API endpoint not found: {url}") from e
            elif e.response.status_code >= 500:
                raise RuntimeError(f"Server error ({e.response.status_code}): {e.response.text}") from e
            else:
                raise RuntimeError(f"HTTP error ({e.response.status_code}): {e.response.text}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}") from e
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            url = f"{self.api_endpoint}/health"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def upload_single(self, test_case: TestCase) -> Dict[str, Any]:
        """
        Upload a single test case to the API.
        
        Args:
            test_case: TestCase object to upload
        
        Returns:
            Response from the API
        """
        return self.bulk_upload([test_case])

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the session."""
        self.session.close()
