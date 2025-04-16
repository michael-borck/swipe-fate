import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from swipe_verse.services.image_processor import ImageProcessor


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        temp_path = temp.name

    # Create a simple test image
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img.save(temp_path)
    
    yield temp_path
    
    # Clean up
    os.unlink(temp_path)


@pytest.fixture
def image_processor():
    """Create an ImageProcessor instance"""
    processor = ImageProcessor()
    
    # Create a temporary cache directory
    test_cache_dir = Path(tempfile.mkdtemp())
    processor.cache_dir = test_cache_dir
    
    yield processor
    
    # Clean up the test cache directory
    for file in test_cache_dir.glob("*"):
        os.unlink(file)
    os.rmdir(test_cache_dir)


def test_init_creates_cache_dir():
    """Test that initializing the processor creates a cache directory"""
    # Arrange & Act
    processor = ImageProcessor()
    
    # Assert
    assert processor.cache_dir.exists()
    assert processor.cache_dir.is_dir()
    assert ".swipe_fate/image_cache" in str(processor.cache_dir)


def test_process_image_missing_file(image_processor):
    """Test that processing a missing image raises FileNotFoundError"""
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        image_processor.process_image("non_existent_file.png")


def test_process_image_no_filter_no_scale(image_processor, sample_image):
    """Test processing an image with no filter or scaling"""
    # Act
    result = image_processor.process_image(sample_image)
    
    # Assert
    assert Path(result).exists()
    assert "no_filter_no_scale" in result
    
    # Verify the image is unchanged
    original = Image.open(sample_image)
    processed = Image.open(result)
    assert original.size == processed.size


def test_process_image_with_scaling(image_processor, sample_image):
    """Test scaling an image"""
    # Arrange
    scale_factor = 0.5
    
    # Act
    result = image_processor.process_image(sample_image, scale=scale_factor)
    
    # Assert
    assert Path(result).exists()
    assert "no_filter_0.5" in result
    
    # Verify the image is scaled
    original = Image.open(sample_image)
    processed = Image.open(result)
    assert processed.width == int(original.width * scale_factor)
    assert processed.height == int(original.height * scale_factor)


def test_process_image_with_filter(image_processor, sample_image):
    """Test applying a filter to an image"""
    # Arrange
    filter_name = "grayscale"
    
    # Act
    result = image_processor.process_image(sample_image, filter_name=filter_name)
    
    # Assert
    assert Path(result).exists()
    assert "grayscale_no_scale" in result
    
    # Verify the image is grayscale
    processed = Image.open(result)
    # Check if image is grayscale by ensuring all RGB channels are equal
    sample_pixel = processed.getpixel((10, 10))
    if isinstance(sample_pixel, tuple):
        r, g, b = sample_pixel[:3]
        assert r == g == b


def test_process_image_with_filter_and_scale(image_processor, sample_image):
    """Test applying both a filter and scaling to an image"""
    # Arrange
    filter_name = "blur"
    scale_factor = 2.0
    
    # Act
    result = image_processor.process_image(
        sample_image, filter_name=filter_name, scale=scale_factor
    )
    
    # Assert
    assert Path(result).exists()
    assert "blur_2.0" in result
    
    # Verify the image is scaled
    original = Image.open(sample_image)
    processed = Image.open(result)
    assert processed.width == int(original.width * scale_factor)
    assert processed.height == int(original.height * scale_factor)


def test_process_image_invalid_filter(image_processor, sample_image):
    """Test that an invalid filter name doesn't apply any filter"""
    # Arrange
    filter_name = "invalid_filter"
    
    # Act
    result = image_processor.process_image(sample_image, filter_name=filter_name)
    
    # Assert
    assert Path(result).exists()
    assert "invalid_filter_no_scale" in result
    
    # Verify the image is unchanged (except for format conversion)
    original = Image.open(sample_image)
    processed = Image.open(result)
    assert original.size == processed.size


def test_cache_reuse(image_processor, sample_image):
    """Test that processed images are cached and reused"""
    # Act
    result1 = image_processor.process_image(sample_image, filter_name="sepia")
    result2 = image_processor.process_image(sample_image, filter_name="sepia")
    
    # Assert
    assert result1 == result2


@pytest.mark.parametrize(
    "filter_name, expected_change",
    [
        ("grayscale", "grayscale"),
        ("cartoon", "edges_enhanced"),
        ("oil_painting", "smoothed_edges"),
        ("sepia", "sepia_tone"),
        ("blur", "blurred"),
        ("sharpen", "sharpened"),
    ],
)
def test_filter_methods(image_processor, sample_image, filter_name, expected_change):
    """Test all filter methods"""
    # Act
    result = image_processor.process_image(sample_image, filter_name=filter_name)
    
    # Assert
    assert Path(result).exists()
    assert f"{filter_name}_no_scale" in result