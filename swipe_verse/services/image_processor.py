from pathlib import Path
from typing import Callable, Dict, Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ImageProcessor:
    """
    Handles various image processing operations for game assets.
    """

    def __init__(self) -> None:
        # Map filter names to processing functions
        self.filters: Dict[str, Callable[[Image.Image], Image.Image]] = {
            "grayscale": self._apply_grayscale,
            "cartoon": self._apply_cartoon,
            "posterize": self._apply_posterize,
            "blur": self._apply_blur,
            "pixelate": self._apply_pixelate,
        }

        # Create a cache directory
        self.cache_dir = Path.home() / ".swipe_verse" / "image_cache"
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
        img: Image.Image = Image.open(path)

        # Apply scaling if requested
        if scale is not None:
            width, height = img.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

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
        """Apply a cartoon-like effect using edge detection and color quantization"""
        # Convert to RGB mode if not already
        img_rgb = img.convert("RGB")

        # Edge detection for outlines
        edges = img_rgb.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Contrast(edges).enhance(2.0)

        # Simplify colors (quantize to fewer colors)
        quantized = img_rgb.quantize(colors=32).convert("RGB")

        # Combine edges with the quantized image
        result = Image.blend(quantized, edges, 0.3)
        return result

    def _apply_posterize(self, img: Image.Image) -> Image.Image:
        """Apply posterize effect (reduced color palette)"""
        # Convert to RGB mode if not already
        img_rgb = img.convert("RGB")

        # Posterize to reduce number of bits per channel (2 bits = 4 values per channel)
        return ImageOps.posterize(img_rgb, 2)

    def _apply_pixelate(self, img: Image.Image) -> Image.Image:
        """Apply pixelation effect"""
        # Determine pixelation factor based on image size
        width, height = img.size
        factor = max(
            1, min(width, height) // 50
        )  # Dynamic pixelation based on image size

        # Downsample and then upsample without interpolation
        small = img.resize(
            (width // factor, height // factor), Image.Resampling.NEAREST
        )
        return small.resize(img.size, Image.Resampling.NEAREST)

    def _apply_blur(self, img: Image.Image) -> Image.Image:
        """Apply a blur effect to an image"""
        return img.filter(ImageFilter.GaussianBlur(radius=2))
