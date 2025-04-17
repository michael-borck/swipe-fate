# Package Renaming & Project Structure

## Status

Accepted

## Context

The project initially started as "Swipe Fate," a card-based decision game focused on a single gameplay experience. As the project evolved, it became clear that the concept could be expanded to include multiple themed "verses" or worlds, creating a multiverse of gaming experiences. This raised questions about:

1. Whether the project name accurately reflected the expanded scope
2. How to structure the codebase to accommodate multiple themes and game variants
3. How to organize assets and configurations for a more flexible system

## Decision

We decided to:

1. Rename the project from "Swipe Fate" to "Swipe Verse" to better reflect the multiverse concept
2. Restructure the package and module organization to support the new name and improved architecture
3. Update all import statements, references, and configurations to use the new naming scheme
4. Create a more modular directory structure for assets, separating themes into distinct directories

The primary change was renaming the main package from `swipe_fate` to `swipe_verse`, updating all import statements throughout the codebase, and modifying package metadata in `pyproject.toml`.

## Rationale

- **Name Change**: "Swipe Verse" better represents the multiverse gameplay concept where players can experience different themed "verses" through the same core mechanics.
- **Comprehensive Approach**: Rather than make incremental changes, we opted for a complete rename to ensure consistency and avoid technical debt.
- **Breaking Change**: While this is a breaking change, it occurred early in development when the impact was minimal.
- **Future-Proofing**: The new structure allows for easier addition of new themes/verses without major architectural changes.

Alternative approaches considered:
- Keeping the original name but expanding the functionality (rejected due to potential confusion)
- Creating a new project rather than renaming (rejected due to the large amount of shared code)

## Consequences

### Positive
- Project name now accurately reflects the expanded game concept
- Directory structure is more intuitive and accommodates multiple themes
- Cleaner separation of concerns between game logic and theme-specific content
- More consistent naming throughout the codebase

### Negative
- One-time breaking change requiring updates to documentation and any existing installations
- Temporary duplication during the transition phase
- Cache directories needed to be updated for the new package name

## Related Decisions

- [ADR-0003: Theming System & Asset Management](0003-theming-system-asset-management.md)
- [ADR-0008: Multi-Verse Concept](0008-multi-verse-concept.md)

## Notes

The renaming process involved:
- Updating package structure
- Modifying pyproject.toml for package metadata
- Changing all import statements
- Updating command-line entry points
- Migrating cache directories to the new name
- Ensuring backward compatibility where possible