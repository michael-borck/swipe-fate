from pathlib import Path
from typing import Dict, Optional

import aiohttp


class AssetManager:
    def __init__(self, base_path: str, default_assets_path: str):
        self.base_path = Path(base_path)
        self.default_assets_path = Path(default_assets_path)
        # Cache maps a key to the local image path
        self.cache: Dict[str, str] = {}

    async def get_image(
        self, image_path: str, filter_type: Optional[str] = None
    ) -> str:
        """
        Load an image from filesystem or URL, apply filters if specified,
        and return path for Flet to use.

        Args:
            image_path: Path or URL to the image
            filter_type: Optional type of filter to apply (grayscale, cartoon, etc.)

        Returns:
            str: Path to the image file that Flet can use
        """
        cache_key = f"{image_path}_{filter_type if filter_type else 'none'}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Try to load from local path first
            path = Path(image_path)
            if path.is_absolute():
                img_path = path
            else:
                img_path = self.base_path / image_path

            if not img_path.exists():
                # Try to load from URL if it looks like a URL
                if image_path.startswith(("http://", "https://")):
                    temp_path = await self._download_image(image_path)
                    img_path = temp_path
                else:
                    # Fall back to default asset
                    default_img = self._get_default_asset_for_type(image_path)
                    img_path = self.default_assets_path / default_img

            # Apply filters if needed
            if filter_type:
                filtered_path = await self._apply_filter(img_path, filter_type)
                self.cache[cache_key] = str(filtered_path)
                return str(filtered_path)

            self.cache[cache_key] = str(img_path)
            return str(img_path)

        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a default fallback image
            fallback = self.default_assets_path / "card_back.png"
            self.cache[cache_key] = str(fallback)
            return str(fallback)

    async def _download_image(self, url: str) -> Path:
        """
        Download image from URL and save to temp location.

        Args:
            url: URL of the image to download

        Returns:
            Path: Path to the downloaded image file
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    # Create a temp file path
                    temp_dir = Path.home() / ".swipe_verse" / "cache"
                    temp_dir.mkdir(parents=True, exist_ok=True)

                    filename = url.split("/")[-1]
                    temp_path = temp_dir / filename

                    with open(temp_path, "wb") as f:
                        f.write(content)

                    return temp_path
                else:
                    raise Exception(
                        f"Failed to download {url}, status {response.status}"
                    )

    async def _apply_filter(self, img_path: Path, filter_type: str) -> Path:
        """
        Apply a filter to an image and save the result.

        Args:
            img_path: Path to the image file
            filter_type: Type of filter to apply (pixelate, cartoon, posterize, blur, grayscale)

        Returns:
            Path: Path to the filtered image
        """
        # Get image processor from app
        from swipe_verse.services.image_processor import ImageProcessor

        processor = ImageProcessor()

        # Create output directory
        output_dir = Path.home() / ".swipe_verse" / "filtered"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{img_path.stem}_{filter_type}{img_path.suffix}"

        # Check if filtered image already exists
        if output_path.exists():
            return output_path

        # Process the image using ImageProcessor
        try:
            # Use the image processor service
            processed_path = processor.process_image(
                str(img_path), filter_name=filter_type
            )
            return Path(processed_path)
        except Exception as e:
            print(f"Error applying filter {filter_type} to {img_path}: {e}")
            # Return original if filtering fails
            return img_path

    def _get_default_asset_for_type(self, path: str) -> str:
        """
        Return appropriate default asset based on the path/type.

        Args:
            path: Original path that couldn't be found

        Returns:
            str: Path to an appropriate default asset
        """
        if "card_back" in path:
            return "card_back.png"
        elif "resource" in path:
            # Determine which resource based on name or position
            resource_num = 1  # Default
            if "resource" in path:
                try:
                    resource_num = int(path.split("resource")[1][0])
                except (IndexError, ValueError):
                    pass
            return f"resource_icons/resource{resource_num}.png"
        else:
            # Default to a card front
            return "card_fronts/card1.png"
