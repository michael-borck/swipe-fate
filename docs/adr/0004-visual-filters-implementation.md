# Visual Filters Implementation

## Status

Accepted

## Context

To enhance the visual variety and customization options in Swipe Verse, we wanted to add various visual filters that could be applied to game assets. This required:

1. A way to process and transform images at runtime
2. Efficient caching to avoid reprocessing the same images
3. A variety of filter types to offer meaningful visual alternatives
4. User controls to select and apply filters
5. Persistence of filter preferences

## Decision

We implemented a visual filter system with the following components:

1. **ImageProcessor Service**:
   - Processes images with various filters
   - Supports multiple filter types:
     - Grayscale: Converts images to black and white
     - Pixelate: Creates a pixelated, retro look
     - Cartoon: Applies edge detection and color quantization
     - Posterize: Reduces color palette for a poster-like effect
     - Blur: Applies a gaussian blur effect
   - Implements caching to avoid reprocessing
   - Uses PIL/Pillow for image manipulation

2. **Filter Configuration**:
   - Game themes specify available filters
   - Filter selection stored in game state
   - UI controls for filter selection

3. **Asset Integration**:
   - AssetManager applies filters via ImageProcessor
   - Filtered images cached separately from originals
   - Filter applied consistently across all assets

## Rationale

- **Runtime Filtering**: Allows players to customize the visual experience without requiring multiple asset sets.
- **Filter Variety**: Different filter types provide meaningful visual changes rather than subtle adjustments.
- **Caching Strategy**: Prevents performance issues by avoiding repeated processing of the same assets.
- **PIL/Pillow Library**: Industry-standard Python imaging library with extensive capabilities.
- **Filter Configurability**: Themes can specify which filters make sense for their visual style.

Alternative approaches considered:
- Pre-generated filtered assets (rejected due to storage requirements)
- CSS filters (rejected due to inconsistent support across platforms)
- Simpler filter options (rejected as less visually impactful)

## Consequences

### Positive
- Players can customize the visual style to their preference
- Same assets can be presented in multiple ways, increasing visual variety
- Caching system ensures good performance even with many assets
- Filters work across all asset types (card images, resource icons, etc.)
- New filters can be added without changing the underlying architecture

### Negative
- Initial filter application can cause a slight delay
- Filter quality depends on the original image resolution
- Cache storage grows with each filter and asset combination

## Related Decisions

- [ADR-0003: Theming System & Asset Management](0003-theming-system-asset-management.md)
- [ADR-0009: Virtual Card Display Design](0009-virtual-card-display-design.md)

## Notes

Filter implementation examples:

```python
def _apply_pixelate(self, img: Image.Image) -> Image.Image:
    """Apply pixelation effect"""
    width, height = img.size
    factor = max(1, min(width, height) // 50)  # Dynamic pixelation based on image size
    small = img.resize((width // factor, height // factor), Image.NEAREST)
    return small.resize(img.size, Image.NEAREST)

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
```

The filter system is particularly useful for creating visual distinction between different game runs, or for adapting the visuals to match player preferences or accessibility needs.