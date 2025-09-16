from __future__ import annotations
from contextlib import suppress
from typing import Any, Dict, List, Optional
from pathlib import Path


class Engine:
    """Light wrapper around the OpenAI Responses client.

    The OpenAI client is created lazily so importing the CLI module
    (for --help or tests) does not require OPENAI_API_KEY to be set.
    """

    def __init__(self, model_default: str = "gpt-4o-mini"):
        self._client_inst = None
        self.model_default = model_default
        self._load_dotenv()

    def _load_dotenv(self):
        """Load environment variables from .env file if it exists."""
        try:
            from dotenv import load_dotenv
            
            # Look for .env file in current directory and parent directories
            env_path = Path.cwd() / ".env"
            if env_path.exists():
                load_dotenv(env_path)
            else:
                # Check parent directories up to project root
                current = Path.cwd()
                for parent in current.parents:
                    env_path = parent / ".env"
                    if env_path.exists():
                        load_dotenv(env_path)
                        break
                    # Stop at git root or when we find pyproject.toml
                    if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                        break
        except ImportError:
            # python-dotenv not installed, skip silently
            pass

    def _get_client(self):
        if self._client_inst is None:
            # import here to avoid raising on module import if OPENAI_API_KEY is missing
            from openai import OpenAI

            self._client_inst = OpenAI()
        return self._client_inst

    def send(
        self,
        input: Any,
        *,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        previous_response_id: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ):
        kwargs: Dict[str, Any] = {
            "model": model or self.model_default,
            "input": input,
        }
        if instructions:     kwargs["instructions"] = instructions
        if tools:            kwargs["tools"] = tools
        if attachments:      kwargs["attachments"] = attachments
        if previous_response_id: kwargs["previous_response_id"] = previous_response_id
        if response_format:  kwargs["response_format"] = response_format

        if stream:
            text_chunks: List[str] = []
            with self._get_client().responses.stream(**kwargs) as s:
                for event in s:
                    if event.type == "response.output_text.delta":
                        print(event.delta, end="", flush=True)
                        text_chunks.append(event.delta)
                    elif event.type == "response.error":
                        raise RuntimeError(event.error)
            print()
            with suppress(Exception):
                final = s.get_final_response()
                return final
            # Fallback: create pseudo response-like object
            class R:
                def __init__(self):
                    self.output_text = ""
                    self.id = None
                    self.output = []
            
            r = R()
            r.output_text = "".join(text_chunks)
            return r

        return self._handle_responses_api_call(**kwargs)

    # Convenience
    def upload_for_kb(self, path) -> str:
        with open(path, "rb") as f:
            file = self._get_client().files.create(file=f, purpose="assistants")
        return file.id

    def create_vector_store(self, name: str) -> str:
        """Create a vector store and return its ID."""
        vector_store = self._get_client().vector_stores.create(name=name)
        return vector_store.id

    def add_files_to_vector_store(self, vector_store_id: str, file_ids: List[str]) -> None:
        """Add files to an existing vector store."""
        for file_id in file_ids:
            self._get_client().vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )

    def _handle_responses_api_call(self, **kwargs):
        """Centralized Responses API call with error handling."""
        try:
            return self._get_client().responses.create(**kwargs)
        except Exception as e:
            # Log error details for debugging
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'kwargs_model': kwargs.get('model'),
                'input_type': type(kwargs.get('input')).__name__ if 'input' in kwargs else None
            }
            raise RuntimeError(f"Responses API call failed: {error_details}")

    def _extract_response_text(self, response) -> str:
        """Extract text content from Responses API response."""
        if hasattr(response, 'output_text') and response.output_text:
            return response.output_text
        elif hasattr(response, 'output') and response.output:
            # Handle structured output format
            try:
                return response.output[0].content[0].text
            except (IndexError, AttributeError):
                pass
        return str(response)

    def _get_image_mime_type(self, file_path: str) -> str:
        """Get MIME type for image file based on extension."""
        from pathlib import Path

        extension = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')  # default fallback

    def analyze_image(self, image_path: str, user_prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None):
        """Analyze an image with optional system and user prompts using Responses API."""
        import base64
        from pathlib import Path

        # Read and encode image
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Get MIME type using helper method
        mime_type = self._get_image_mime_type(image_path)

        # Build input for Responses API
        input_content = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{base64_image}"
                    },
                    {
                        "type": "input_text",
                        "text": user_prompt
                    }
                ]
            }
        ]

        # Build API call parameters
        kwargs = {
            "model": model or "gpt-4o",
            "input": input_content,
            "max_output_tokens": 1000
        }

        if system_prompt:
            kwargs["instructions"] = system_prompt

        # Use Responses API consistently with error handling
        response = self._handle_responses_api_call(**kwargs)
        return self._extract_response_text(response)

    def analyze_multimodal_content(self, content_path: Optional[str] = None, user_prompt: str = "", 
                                  system_prompt: Optional[str] = None, model: Optional[str] = None, 
                                  previous_response_id: Optional[str] = None, content_type: str = "auto"):
        """
        Unified method for analyzing any content type (images, audio, video, files, or text-only).
        Uses Responses API for proper threading across all modalities.
        
        Args:
            content_path: Path to content file (None for text-only)
            user_prompt: User's prompt/question
            system_prompt: Optional system prompt for context
            model: Model to use (auto-selected based on content type)
            previous_response_id: Previous response ID for threading
            content_type: Content type ("auto", "image", "audio", "video", "file", "text")
        """
        import base64
        from pathlib import Path
        
        # Auto-detect content type if not specified
        if content_type == "auto" and content_path:
            content_type = self._detect_content_type(content_path)
        elif not content_path:
            content_type = "text"
        
        # Build input based on content type
        if content_type == "text":
            # Text-only input
            input_content = user_prompt
            model = model or self.model_default
            
        elif content_type == "image":
            # Image analysis
            if not content_path:
                raise ValueError("content_path is required for image analysis")
            img_path = Path(content_path)
            if not img_path.exists():
                raise FileNotFoundError(f"Image file not found: {content_path}")

            with open(img_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Get MIME type using helper method
            mime_type = self._get_image_mime_type(content_path)

            # Build multimodal input for Responses API
            input_content = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{base64_image}"
                        }
                    ]
                }
            ]

            # Add text if provided
            if user_prompt:
                input_content[0]["content"].append({
                    "type": "input_text",
                    "text": user_prompt
                })

            model = model or "gpt-4o"  # Vision-capable model
            
        elif content_type == "audio":
            # Future: Audio analysis (when supported by Responses API)
            raise NotImplementedError("Audio analysis will be supported when OpenAI releases audio capabilities in Responses API")
            
        elif content_type == "video":
            # Future: Video analysis (when supported by Responses API)
            raise NotImplementedError("Video analysis will be supported when OpenAI releases video capabilities in Responses API")
            
        elif content_type == "file":
            # File analysis by reading content directly
            if not content_path:
                raise ValueError("content_path is required for file analysis")
            file_path = Path(content_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {content_path}")

            # Read file content directly for text-based files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                # For binary files, fall back to basic info
                file_content = f"Binary file: {file_path.name} ({file_path.stat().st_size} bytes)"

            # Combine user prompt with file content
            combined_prompt = f"{user_prompt}\n\n--- File: {file_path.name} ---\n{file_content}"
            input_content = combined_prompt
            model = model or "gpt-4o"
        
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Standard Responses API call for all other content types
        kwargs = {
            "model": model,
            "input": input_content,
            "max_output_tokens": 4000
        }
        
        if system_prompt:
            kwargs["instructions"] = system_prompt
        if previous_response_id:
            kwargs["previous_response_id"] = previous_response_id

        response = self._handle_responses_api_call(**kwargs)
        return response
    
    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type based on file extension."""
        from pathlib import Path
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Image formats
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return "image"
        
        # Audio formats (for future)
        elif extension in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
            return "audio"
        
        # Video formats (for future)
        elif extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return "video"
        
        # Document/file formats
        elif extension in ['.pdf', '.txt', '.md', '.py', '.js', '.json', '.csv', '.xml', '.html']:
            return "file"
        
        else:
            return "file"  # Default to file analysis
