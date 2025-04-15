# SwipeFate Design Document

## Game Concept

SwipeFate is a card-based decision game where players make binary choices (swipe left or right) on cards to progress through scenarios. Each decision affects various resources and can trigger events based on the game state.

## Core Mechanics

### Decision Cards
- Players are presented with decision cards one at a time
- Each card presents a scenario with two choices
- Swiping left or right (or tapping corresponding buttons) makes a choice
- Decisions affect resources immediately and may trigger events

### Resources
- Numerical values tracked by the game
- Can include concrete resources (money, materials, crew) or abstract values (reputation, morale)
- Updated based on decision outcomes
- Can trigger events when reaching certain thresholds

### Events
- Triggered by decisions or resource values
- Can introduce new scenarios, modify resources, or change game state
- Add narrative depth and consequences to decisions

### Game Progression
- Games follow a semi-linear progression with branching paths
- Some decisions unlock or lock future scenarios
- Resource management creates strategy depth
- Multiple endings based on cumulative decisions and resource management

## UI Design Principles

### Simplicity
- Clean, minimal interface focusing on the current decision
- Resources displayed clearly but unobtrusively
- Animations provide feedback but don't distract from core gameplay

### Accessibility
- High contrast text options
- Configurable text size
- Alternative input methods (tap buttons in addition to swipe)
- Screen reader compatibility

### Responsive Design
- Adapts to different screen sizes and orientations
- Maintains usability across desktop, web, and mobile

## Themes and Variations

SwipeFate can host multiple game themes through its configuration system:

1. **Business Management**
   - Resources: Money, Reputation, Staff Morale, Market Share
   - Goal: Build a successful business empire

2. **Space Exploration**
   - Resources: Oxygen, Fuel, Crew Morale, Scientific Data
   - Goal: Successfully complete the mission and return safely

3. **Political Simulator**
   - Resources: Public Support, Party Loyalty, Treasury, Foreign Relations
   - Goal: Stay in power and implement your agenda

Each theme utilizes the same core mechanics but presents distinct narrative contexts and resource systems.