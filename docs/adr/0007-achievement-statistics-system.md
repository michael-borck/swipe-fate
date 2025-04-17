# ADR 0007: Achievement and Statistics System

## Status

Accepted

## Context

To enhance player engagement and provide a sense of progression, we needed to implement a system to track player achievements and game statistics. This required decisions about:

1. What data to track and store
2. How to persist this data across game sessions
3. How to present achievements and statistics to players
4. When and how to notify players of achievements

## Decision

We implemented a comprehensive achievement and statistics tracking system with the following components:

1. **GameHistory Service**:
   - Tracks and persists game outcomes, resource statistics, and achievement progress
   - Uses local file storage in the user's home directory
   - Maintains separate records for each game theme/universe

2. **Achievement System**:
   - Predefined set of achievements with unlock conditions
   - Categories including game completion, resource management, and special outcomes
   - Achievement metadata including name, description, and unlock requirements

3. **Statistics Tracking**:
   - General stats: games played, wins, losses, win rate
   - Resource high/low records for each resource type
   - Theme-specific statistics

4. **UI Integration**:
   - Dedicated achievements screen accessible from title and game-over screens
   - Notification system for newly unlocked achievements
   - Visual indicators for locked vs unlocked achievements

## Rationale

- **Engagement**: Achievements provide additional goals beyond simply winning the game
- **Replayability**: Varied achievement conditions encourage players to try different strategies
- **Sense of Progress**: Statistics tracking gives players a sense of their improvement over time
- **Low Technical Overhead**: Local file storage provides persistence without requiring server infrastructure
- **Privacy-Friendly**: All data remains on the user's device
- **Theme Relevance**: Separating statistics by theme/universe maintains the narrative distinction

## Alternatives Considered

### Server-Based Achievement System

A cloud-based approach would have allowed:
- Cross-device synchronization of achievements
- Global leaderboards and community statistics
- More secure storage of achievement data

This was rejected because:
- It would introduce unnecessary infrastructure dependencies
- Privacy concerns with tracking user activity
- Added complexity without significant user benefit for a primarily single-player experience

### In-Memory Only Stats

Simply tracking statistics during a session without persistence was considered for simplicity, but rejected because:
- Would lose all progress when the application closes
- Undermines the sense of long-term progression

### Achievement Tiers/Levels

A more complex system with tiered/leveled achievements (bronze/silver/gold) was considered but postponed because:
- Current achievement set is sufficient for initial release
- Can be implemented as an enhancement in future updates

## Consequences

### Positive

- Increased player engagement and replayability
- Additional goals beyond basic game completion
- Sense of progression across multiple play sessions
- Foundation for potential future social features

### Negative

- Potential for achievement-hunting to overshadow core gameplay
- Local storage limitations (doesn't sync across devices)
- Additional testing and maintenance requirements

## Implementation Notes

The achievement system is implemented through:

- `GameHistory` class in `services/game_history.py` that handles persistence
- Integration with `GameLogic` to track game events and check achievement conditions
- UI components in the game over dialog and dedicated achievements screen
- JSON serialization for persistent storage
- Directory structure in `~/.swipe_verse/history/` to store user data

Achievement definitions are stored in game configuration files, allowing for theme-specific achievements alongside universal ones.

## Related Decisions

- ADR 0002: Configuration Structure and Game Data Model
- ADR 0005: User Interface Navigation Patterns

## Notes

Future enhancements being considered:
- Achievement tiers/levels (bronze, silver, gold)
- Daily/weekly challenges
- Achievement-based unlockable content
- Optional cloud sync for multi-device users