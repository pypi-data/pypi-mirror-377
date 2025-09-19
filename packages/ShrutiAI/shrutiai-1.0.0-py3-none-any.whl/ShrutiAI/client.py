"""
Main client class for shrutiAI SDK
"""
import requests
import json
import os
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import mimetypes

from .exceptions import (
    ShrutiAIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
    NetworkError
)

class ShrutiAIClient:
    """
    Client for interacting with shrutiAI API

    Usage:
        client = ShrutiAIClient(api_key="your-api-key")
        response = client.chat(message="Hello, how are you?")
    """

    def _decode_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Decode and validate an API key to extract tool permissions

        Args:
            api_key: The encrypted API key

        Returns:
            Dict containing decoded information or error
        """
        try:
            # Decode from base64
            decoded_bytes = base64.urlsafe_b64decode(api_key.encode())
            decoded_json = decoded_bytes.decode()

            # Parse JSON
            data = json.loads(decoded_json)

            # Verify integrity
            payload = data["payload"]
            integrity_hash = data["integrity"]

            payload_json = json.dumps(payload, sort_keys=True)
            expected_hash = hashlib.sha256(payload_json.encode()).hexdigest()[:16]

            if integrity_hash != expected_hash:
                return {
                    "valid": False,
                    "error": "API key integrity check failed"
                }

            # Validate date format (but no expiry check)
            try:
                created_at_str = payload["created_at"]
                datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except (ValueError, KeyError) as e:
                return {
                    "valid": False,
                    "error": f"Invalid date format in API key: {str(e)}"
                }

            return {
                "valid": True,
                "user_id": payload["user_id"],
                "allowed_tools": payload["allowed_tools"],
                "created_at": payload["created_at"],
                "version": payload["version"]
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid API key format: {str(e)}"
            }

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://app-shruti-ai-prod-api.azurewebsites.net/api",
        timeout: int = 120
    ):
        """
        Initialize the API client

        Args:
            api_key: Your API key for authentication
            base_url: Base URL for the API (default: https://app-shruti-ai-prod-api.azurewebsites.net/api)
            timeout: Request timeout in seconds (default: 120)
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        # Decode API key to extract tool permissions
        decoded_key = self._decode_api_key(api_key)
        if not decoded_key["valid"]:
            raise AuthenticationError(f"Invalid API key: {decoded_key['error']}")

        self.api_key = api_key
        self.decoded_key = decoded_key  # Store decoded key info
        self.allowed_tools = decoded_key["allowed_tools"]
        self.user_id = decoded_key["user_id"]

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

        # Set default headers with API key and tool permissions
        self.session.headers.update({
            'User-Agent': 'shrutiAI-SDK/1.0.0',
            'X-API-Key': api_key,
            'X-User-ID': self.user_id,
            'X-Allowed-Tools': json.dumps(self.allowed_tools)
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Dict containing the JSON response

        Raises:
            ShrutiAIError: For various API errors
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))

        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            response = self.session.request(method, url, **kwargs)

            # Handle different error status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key", response.status_code, response)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", response.status_code, response)
            elif response.status_code == 404:
                raise NotFoundError("Resource not found", response.status_code, response)
            elif response.status_code == 422:
                raise ValidationError("Invalid request data", response.status_code, response)
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.text}", response.status_code, response)
            elif not response.ok:
                raise ShrutiAIError(f"API request failed: {response.text}", response.status_code, response)

            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"message": response.text, "status_code": response.status_code}

        except requests.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    def _prepare_file_data(self, file_path: Optional[str] = None) -> Optional[tuple]:
        """
        Prepare file data for upload

        Args:
            file_path: Path to the file to upload

        Returns:
            Tuple of (file_object, filename) or None
        """
        if not file_path:
            return None

        if not os.path.exists(file_path):
            raise ValidationError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            from io import BytesIO
            file_obj = BytesIO(file_data)
            file_obj.name = filename
            file_obj.mode = 'rb'

            return file_obj, filename

        except Exception as e:
            raise ValidationError(f"Error reading file {file_path}: {str(e)}")

    # Chat and AI Methods
    def chat(
        self,
        message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        language: str = "english",
        image_path: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to the AI assistant

        Args:
            message: The message to send
            user_id: Optional user identifier
            conversation_id: Optional conversation identifier
            latitude: Optional latitude for location-based queries
            longitude: Optional longitude for location-based queries
            language: Language for response (default: "english")
            image_path: Optional path to image file for analysis
            file_path: Optional path to document file for analysis

        Returns:
            Dict containing AI response and metadata
        """
        # Prepare form data
        data = {
            'message': message,
            'language': language,
            'allowed_tools': json.dumps(self.allowed_tools),  # Send allowed_tools as separate parameter
            'api_key_info': json.dumps({
                'user_id': self.user_id,
                'allowed_tools': self.allowed_tools,
                'created_at': self.decoded_key['created_at'],
                'version': self.decoded_key['version']
            })
        }

        if user_id:
            data['user_id'] = user_id
        if conversation_id:
            data['conversation_id'] = conversation_id
        if latitude:
            data['latitude'] = latitude
        if longitude:
            data['longitude'] = longitude

        # Prepare files
        files = {}
        if image_path:
            file_obj, filename = self._prepare_file_data(image_path)
            files['image'] = (filename, file_obj, 'image/jpeg')
        if file_path:
            file_obj, filename = self._prepare_file_data(file_path)
            files['file'] = (filename, file_obj, 'application/pdf')

        response = self._make_request('POST', '/api/chat-tool', data=data, files=files if files else None)
        return response

    def get_allowed_tools(self) -> List[str]:
        """
        Get the list of tools allowed for this API key

        Returns:
            List of allowed tool names
        """
        return self.allowed_tools.copy()

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the current API key user

        Returns:
            Dict containing user information and permissions
        """
        return {
            'user_id': self.user_id,
            'allowed_tools': self.allowed_tools,
            'created_at': self.decoded_key['created_at'],
            'version': self.decoded_key['version']
        }

    def validate_tool_access(self, tool_name: str) -> bool:
        """
        Check if a specific tool is allowed for this API key

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is allowed, False otherwise
        """
        return tool_name in self.allowed_tools