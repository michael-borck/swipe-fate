# Theming System & Asset Management

## Status

Accepted

## Context

To support multiple game themes (Kingdom, Business, etc.) while maintaining consistency in the game mechanics, we needed a flexible system for:

1. Managing theme-specific visual assets (card images, resource icons)
2. Handling fallback assets when theme-specific ones are missing
3. Organizing assets in a manner that makes it easy to add new themes
4. Loading and caching assets efficiently
5. Applying visual filters and transformations to assets

## Decision

We implemented a comprehensive theming and asset management system with the following components:

1. **Directory Structure**:
   - `/assets/default/`: Common fallback assets
   - `/assets/themes/{theme_name}/`: Theme-specific assets
   - Within each theme: `card_fronts/`, `resource_icons/`, and `card_back.png`

2. **Asset Naming Convention**:
   - Generic, descriptive names for default assets (e.g., `resource.png`, `people.png`)
   - Theme-specific, functional names for themed assets (e.g., `treasury.png`, `population.png`)

3. **AssetManager Service**:
   - Handles loading assets from filesystem or URLs
   - Implements fallback logic: specific theme → default assets
   - Manages caching for performance
   - Applies visual filters when requested

4. **Theme Configuration**:
   - Each game config includes a `theme` section
   - Maps resource types to their icon paths
   - Specifies card back and other theme-specific visuals
   - Defines color schemes for UI elements

## Rationale

- **Layered Fallback System**: Ensures the game never breaks due to missing assets.
- **Semantic Asset Naming**: Makes it clear what each asset represents.
- **Theme-Specific Directories**: Allow clean separation between different visual themes.
- **Default Asset Collection**: Provides a complete set of generic assets that can work with any theme.
- **Asset Manager Service**: Centralizes asset loading logic and implements caching for better performance.

Alternative approaches considered:
- Single directory with prefixed asset names (rejected as less organized)
- Database storage for assets (rejected as overly complex)
- Runtime asset generation (rejected due to performance concerns)

## Consequences

### Positive
- Easy to add new themes by creating a new theme directory and assets
- Consistent fallback behavior ensures the game always looks complete
- Clear organization makes it evident which assets belong to which theme
- Efficient caching reduces unnecessary asset loading
- Generic default assets work across all game themes

### Negative
- More complex initial setup compared to a simple asset directory
- Requires maintaining both specific and fallback assets
- Adding new types of assets requires updating the fallback collection

## Related Decisions

- [ADR-0002: Configuration Structure & Game Data Model](0002-configuration-structure-game-data-model.md)
- [ADR-0004: Visual Filters Implementation](0004-visual-filters-implementation.md)
- [ADR-0009: Virtual Card Display Design](0009-virtual-card-display-design.md)

## Notes

The decision to use descriptive, semantic names for default assets (resource, people, power, harmony) instead of generic names (resource1, resource2, etc.) makes the assets more intuitive and increases the likelihood they'll work well as fallbacks for various themes.

Default asset types include:
- Card backs
- Resource icons (4 types)
- Card fronts for different scenarios (choice, event, challenge, opportunity)

This structure allows game designers to mix and match assets or create entirely new themes while maintaining a consistent gameplay experience.