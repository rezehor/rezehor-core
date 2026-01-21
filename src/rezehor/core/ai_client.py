"""Claude API client for Rezehor."""

from typing import AsyncIterator, Optional
import base64
from pathlib import Path

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message, TextBlock
from loguru import logger

from rezehor.utils.config import get_config


class AIClient:
    """Client for interacting with Claude API."""

    def __init__(self) -> None:
        """Initialize AI client."""
        self.config = get_config()

        # Synchronous client
        self.client = Anthropic(api_key=self.config.settings.anthropic_api_key)

        # Async client for streaming
        self.async_client = AsyncAnthropic(
            api_key=self.config.settings.anthropic_api_key
        )

        logger.info(f"AI Client initialized with model: {self.config.ai.model}")

    def send_message(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        image_path: Optional[Path] = None,
    ) -> str:
        """
        Send a message to Claude and get response.

        Args:
            message: User message
            system_prompt: Optional system instructions
            image_path: Optional image to include (for screen analysis)

        Returns:
            Claude's response text
        """
        # Build message content
        content: list[Any] = []

        # Add image if provided
        if image_path:
            logger.debug(f"Including image: {image_path}")
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                }
            )

        # Add text message
        content.append(
            {
                "type": "text",
                "text": message,
            }
        )

        # Make API call
        try:
            response: Message = self.client.messages.create(
                model=self.config.ai.model,
                max_tokens=self.config.ai.max_tokens,
                temperature=self.config.ai.temperature,
                system=(
                    system_prompt
                    if system_prompt
                    else "You are Rezehor, a helpful AI assistant."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )

            # Extract text from response - handle different content types
            result = ""
            for block in response.content:
                if isinstance(block, TextBlock):
                    result += block.text

            logger.info(f"Received response ({len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    async def stream_message(
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream Claude's response token by token.

        Args:
            message: User message
            system_prompt: Optional system instructions

        Yields:
            Response text chunks
        """
        try:
            async with self.async_client.messages.stream(
                model=self.config.ai.model,
                max_tokens=self.config.ai.max_tokens,
                temperature=self.config.ai.temperature,
                system=(
                    system_prompt
                    if system_prompt
                    else "You are Rezehor, a helpful AI assistant."
                ),
                messages=[{"role": "user", "content": message}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise


# Example usage
if __name__ == "__main__":
    from typing import Any  # Add this import at top

    client = AIClient()
    response = client.send_message("Hello! What can you help me with?")
    print(response)
