from pathlib import Path
from typing import Any, Callable, Dict, Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ImageProcessor:
    """
    Handles various image processing operations for game assets.
    """

    def __init__(self):
        self.filters: Dict[str, Callable[[Image.Image, Any], Image.Image]] = {
            "grayscale": self._apply_grayscale,
            "cartoon": self._apply_cartoon,
            "oil_painting": self._apply_oil_painting,
            "sepia": self._apply_sepia,
            "blur": self._apply_blur,
            "sharpen": self._apply_sharpen,
        }

        # Create a cache directory
        self.cache_dir = Path.home() / ".swipe_fate" / "image_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def process_image(
        self,
        image_path: str,
        filter_name: Optional[str] = None,
        scale: Optional[float] = None,
    ) -> str:
        """
        Process an image with the specified filter and/or scaling.

        Args:
            image_path: Path to the image file
            filter_name: Name of the filter to apply
            scale: Scale factor to resize the image

        Returns:
            str: Path to the processed image
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Create a cache key based on the parameters
        filter_part = filter_name or "no_filter"
        scale_part = scale or "no_scale"
        cache_key = f"{path.stem}_{filter_part}_{scale_part}{path.suffix}"
        cache_path = self.cache_dir / cache_key

        # Return cached version if available
        if cache_path.exists():
            return str(cache_path)

        # Process the image
        img = Image.open(path)

        # Apply scaling if requested
        if scale is not None:
            width, height = img.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Apply filter if requested
        if filter_name and filter_name in self.filters:
            img = self.filters[filter_name](img)

        # Save the processed image
        img.save(cache_path)
        return str(cache_path)

    def _apply_grayscale(self, img: Image.Image) -> Image.Image:
        """Convert an image to grayscale"""
        return ImageOps.grayscale(img)

    def _apply_cartoon(self, img: Image.Image) -> Image.Image:
        """Apply a cartoon-like effect to an image"""
        # Edge detection and enhancement
        edges = img.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Contrast(edges).enhance(2.0)

        # Color simplification
        color = img.filter(ImageFilter.SMOOTH_MORE)
        color = ImageEnhance.Color(color).enhance(1.5)

        # Combine edges and colors
        result = Image.blend(color, edges, 0.3)
        return result

    def _apply_oil_painting(self, img: Image.Image) -> Image.Image:
        """Apply an oil painting effect to an image"""
        # Smooth and then enhance edges
        result = img.filter(ImageFilter.SMOOTH_MORE)
        result = result.filter(ImageFilter.EDGE_ENHANCE)
        result = ImageEnhance.Contrast(result).enhance(1.2)
        return result

    def _apply_sepia(self, img: Image.Image) -> Image.Image:
        """Apply a sepia tone to an image"""
        # First convert to grayscale
        gray = ImageOps.grayscale(img)

        # Apply sepia tone
        sepia = Image.new("RGB", gray.size, (255, 240, 192))
        return Image.blend(gray.convert("RGB"), sepia, 0.5)

    def _apply_blur(self, img: Image.Image) -> Image.Image:
        """Apply a blur effect to an image"""
        return img.filter(ImageFilter.GaussianBlur(radius=2))

    def _apply_sharpen(self, img: Image.Image) -> Image.Image:
        """Sharpen an image"""
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(2.0)
