"""
AIClient - OpenAI-compatible API client with configurable endpoint.

Supports:
- OpenAI API
- LM Studio (local)
- Ollama
- Any OpenAI-compatible endpoint
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Type
import json
import logging

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """
    Configuration for the AI client.
    
    Attributes:
        base_url: The API endpoint URL (e.g., "http://localhost:1234/v1" for LM Studio)
        api_key: API key (use "lm-studio" or "ollama" for local servers)
        model: Model name to use
        temperature: Sampling temperature (0.0 = deterministic)
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
    """
    
    # Endpoint configuration
    base_url: str = "http://localhost:1234/v1"  # LM Studio default
    api_key: str = "lm-studio"  # Placeholder for local servers
    model: str = "local-model"
    
    # Generation parameters
    temperature: float = 0.1  # Low for more deterministic behavior
    max_tokens: int = 500
    top_p: float = 0.9
    
    # Request settings
    timeout: float = 30.0
    retry_attempts: int = 2
    
    # Structured output
    use_json_mode: bool = True
    
    @classmethod
    def for_lm_studio(
        cls,
        model: str = "local-model",
        port: int = 1234,
    ) -> "AIConfig":
        """Create config for LM Studio."""
        return cls(
            base_url=f"http://localhost:{port}/v1",
            api_key="lm-studio",
            model=model,
        )
    
    @classmethod
    def for_ollama(
        cls,
        model: str = "llama2",
        port: int = 11434,
    ) -> "AIConfig":
        """Create config for Ollama."""
        return cls(
            base_url=f"http://localhost:{port}/v1",
            api_key="ollama",
            model=model,
        )
    
    @classmethod
    def for_openai(
        cls,
        api_key: str,
        model: str = "gpt-4o-mini",
    ) -> "AIConfig":
        """Create config for OpenAI."""
        return cls(
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            model=model,
        )


class AIClient:
    """
    OpenAI-compatible API client.
    
    Provides structured output for reliable, parseable responses.
    Works with any OpenAI-compatible endpoint.
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """
        Initialize the AI client.
        
        Args:
            config: AI configuration. Defaults to LM Studio config.
        """
        if not HAS_OPENAI:
            raise ImportError(
                "openai package is required for AI features. "
                "Install with: pip install openai"
            )
        
        self.config = config or AIConfig()
        
        self._client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout,
        )
        
        logger.info(f"AI client initialized: {self.config.base_url}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a text response.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
        )
        
        return response.choices[0].message.content
    
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> BaseModel:
        """
        Generate a structured response using a Pydantic model.
        
        Uses OpenAI's json_schema response format for strict output validation.
        
        Args:
            prompt: The user prompt
            response_model: Pydantic model class defining the output schema
            system_prompt: Optional system prompt
            temperature: Override default temperature
            
        Returns:
            Instance of the response model with parsed data
        """
        # Build the JSON schema from the Pydantic model
        schema = response_model.model_json_schema()
        
        # Clean up the schema for OpenAI compatibility
        # Remove $defs references and flatten if needed
        clean_schema = self._prepare_schema_for_openai(schema)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "timeout": self.config.timeout,
        }
        
        # Use json_schema response format for strict structured output
        if self.config.use_json_mode:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": clean_schema,
                }
            }
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                
                # Parse and validate with Pydantic
                parsed = self._parse_json_response(content)
                return response_model.model_validate(parsed)
                
            except Exception as e:
                error_str = str(e)
                
                # If provider doesn't support json_schema, fall back to json_object
                if "json_schema" in error_str and "response_format" in kwargs:
                    logger.warning("Provider rejected json_schema; trying json_object mode")
                    kwargs["response_format"] = {"type": "json_object"}
                    # Add schema instruction to system prompt
                    schema_str = json.dumps(clean_schema, indent=2)
                    schema_instruction = (
                        f"\n\nYou must respond with a valid JSON object matching this schema:\n"
                        f"```json\n{schema_str}\n```\n"
                        f"Respond ONLY with the JSON object, no additional text."
                    )
                    if messages[0]["role"] == "system":
                        messages[0]["content"] += schema_instruction
                    else:
                        messages.insert(0, {"role": "system", "content": schema_instruction})
                    kwargs["messages"] = messages
                    continue
                
                # If provider rejects json_object too, try without response_format
                if "response_format" in error_str and "response_format" in kwargs:
                    logger.warning("Provider rejected response_format; retrying without it")
                    kwargs.pop("response_format", None)
                    continue
                
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise
        
        raise RuntimeError("Failed to generate structured response")
    
    def _prepare_schema_for_openai(self, schema: Dict) -> Dict:
        """
        Prepare a Pydantic JSON schema for OpenAI's json_schema format.
        
        OpenAI requires:
        - additionalProperties: false on all objects
        - All properties must be required (no optional without default)
        - $defs must be resolved or kept at top level
        """
        # Deep copy to avoid modifying original
        import copy
        clean = copy.deepcopy(schema)
        
        def process_object(obj: Dict) -> Dict:
            """Recursively process schema objects."""
            if not isinstance(obj, dict):
                return obj
            
            # Handle $ref by keeping them (OpenAI supports $defs)
            if "$ref" in obj:
                return obj
            
            # Process object types
            if obj.get("type") == "object":
                obj["additionalProperties"] = False
                
                # Ensure all properties are in required
                if "properties" in obj:
                    if "required" not in obj:
                        obj["required"] = list(obj["properties"].keys())
                    
                    # Process nested properties
                    for prop_name, prop_schema in obj["properties"].items():
                        obj["properties"][prop_name] = process_object(prop_schema)
            
            # Process array items
            if obj.get("type") == "array" and "items" in obj:
                obj["items"] = process_object(obj["items"])
            
            # Process anyOf/oneOf
            for key in ["anyOf", "oneOf", "allOf"]:
                if key in obj:
                    obj[key] = [process_object(item) for item in obj[key]]
            
            return obj
        
        # Process the main schema
        clean = process_object(clean)
        
        # Process $defs if present
        if "$defs" in clean:
            for def_name, def_schema in clean["$defs"].items():
                clean["$defs"][def_name] = process_object(def_schema)
        
        return clean
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON from response, handling common issues."""
        # Clean up common issues
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines (code block markers)
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)
        
        return json.loads(content)
    
    def check_connection(self) -> bool:
        """
        Check if the AI endpoint is reachable.
        
        Returns:
            True if connection successful
        """
        try:
            # Try a minimal request
            self._client.models.list()
            return True
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
