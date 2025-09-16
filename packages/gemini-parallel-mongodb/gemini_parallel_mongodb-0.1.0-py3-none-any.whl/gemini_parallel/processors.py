"""
Content processors for different input types (text, images, structured).
"""

from typing import List, Union, Any
from google.genai import types
from PIL import Image
import mimetypes
import os


class ContentBuilder:
    """Builder for creating content objects for different modes."""

    @staticmethod
    def with_image(image_path: str, prompt: str) -> List[Any]:
        """
        Create multimodal content with single image from file path.

        Args:
            image_path: Path to image file
            prompt: Text prompt to accompany the image

        Returns:
            List containing PIL Image and prompt
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        image = Image.open(image_path)
        return [image, prompt]

    @staticmethod
    def with_images(image_paths: List[str], prompt: str) -> List[Any]:
        """
        Create multimodal content with multiple images from file paths.

        Args:
            image_paths: List of paths to image files
            prompt: Text prompt to accompany the images

        Returns:
            List containing PIL Images and prompt
        """
        images = []
        for path in image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            images.append(Image.open(path))

        return images + [prompt]

    @staticmethod
    def with_pil_image(image: Image.Image, prompt: str) -> List[Any]:
        """
        Create multimodal content with PIL Image object.

        Args:
            image: PIL Image object
            prompt: Text prompt to accompany the image

        Returns:
            List containing PIL Image and prompt
        """
        return [image, prompt]

    @staticmethod
    def with_pil_images(images: List[Image.Image], prompt: str) -> List[Any]:
        """
        Create multimodal content with multiple PIL Image objects.

        Args:
            images: List of PIL Image objects
            prompt: Text prompt to accompany the images

        Returns:
            List containing PIL Images and prompt
        """
        return images + [prompt]

    @staticmethod
    def from_bytes(image_bytes: bytes, mime_type: str, prompt: str) -> List[Any]:
        """
        Create multimodal content from image bytes.

        Args:
            image_bytes: Image data as bytes
            mime_type: MIME type of the image (e.g., 'image/jpeg')
            prompt: Text prompt to accompany the image

        Returns:
            List containing Part.from_bytes and prompt
        """
        return [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt
        ]

    @staticmethod
    def from_uri(file_uri: str, mime_type: str, prompt: str) -> List[Any]:
        """
        Create multimodal content from URI (e.g., Google Cloud Storage).

        Args:
            file_uri: URI to the image file
            mime_type: MIME type of the image
            prompt: Text prompt to accompany the image

        Returns:
            List containing Part.from_uri and prompt
        """
        return [
            types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
            prompt
        ]

    @staticmethod
    def guess_mime_type(file_path: str) -> str:
        """
        Guess MIME type from file extension.

        Args:
            file_path: Path to file

        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"

    @staticmethod
    def auto_image_content(image_input: Union[str, bytes, Image.Image], prompt: str) -> List[Any]:
        """
        Automatically create image content based on input type.

        Args:
            image_input: String path, bytes data, or PIL Image
            prompt: Text prompt

        Returns:
            Appropriate content list
        """
        if isinstance(image_input, str):
            # File path
            return ContentBuilder.with_image(image_input, prompt)
        elif isinstance(image_input, bytes):
            # Bytes data - try to guess type
            return ContentBuilder.from_bytes(
                image_input,
                "image/jpeg",  # Default assumption
                prompt
            )
        elif isinstance(image_input, Image.Image):
            # PIL Image
            return ContentBuilder.with_pil_image(image_input, prompt)
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")


class TextProcessor:
    """Simple text processing utilities."""

    @staticmethod
    def create_batch_prompts(
        base_prompt: str,
        items: List[str],
        template: str = "{base_prompt}\n\nItem: {item}"
    ) -> List[str]:
        """
        Create batch of prompts from a base prompt and list of items.

        Args:
            base_prompt: Base prompt template
            items: List of items to process
            template: Template string with {base_prompt} and {item} placeholders

        Returns:
            List of formatted prompts
        """
        return [
            template.format(base_prompt=base_prompt, item=item)
            for item in items
        ]

    @staticmethod
    def create_numbered_prompts(prompts: List[str]) -> List[str]:
        """
        Add numbers to prompts for tracking.

        Args:
            prompts: List of prompts

        Returns:
            List of numbered prompts
        """
        return [
            f"[{i+1}/{len(prompts)}] {prompt}"
            for i, prompt in enumerate(prompts)
        ]