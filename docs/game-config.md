# Game Configuration Guide

SwipeFate uses JSON configuration files to define game content, mechanics, and themes. This allows creating entirely new games without changing the code.

## Configuration Structure

A complete game configuration file includes these main sections:

```json
{
  "metadata": {
    "name": "Game Name",
    "version": "1.0",
    "author": "Author Name",
    "description": "Game description"
  },
  "resources": {
    "resource1": {
      "initial": 100,
      "min": 0,
      "max": 1000,
      "display_name": "Resource One"
    },
    "resource2": {
      "initial": 50,
      "min": 0,
      "max": 100,
      "display_name": "Resource Two"
    }
  },
  "decisions": [
    {
      "id": "decision1",
      "text": "Decision description text",
      "image": "optional/path/to/image.png",
      "image_url": "https://example.com/images/decision1.jpg",
      "left": {
        "text": "Left option text",
        "effects": {
          "resource1": -10,
          "resource2": +5
        },
        "next": "decision2"
      },
      "right": {
        "text": "Right option text",
        "effects": {
          "resource1": +5,
          "resource2": -10
        },
        "next": "decision3"
      }
    }
  ],
  "events": [
    {
      "id": "event1",
      "trigger": {
        "type": "resource",
        "resource": "resource1",
        "condition": "less_than",
        "value": 20
      },
      "text": "Event description text",
      "effects": {
        "resource2": -10
      },
      "next_decision": "decision_emergency"
    }
  ],
  "rules": [
    {
      "id": "rule1",
      "condition": {
        "resource1": {
          "max": 10
        },
        "resource2": {
          "min": 90
        }
      },
      "effects": {
        "trigger_event": "special_outcome"
      }
    }
  ],
  "themes": {
    "default": {
      "background_color": "#f5f5f5",
      "text_color": "#333333",
      "accent_color": "#4a86e8",
      "background_image": "assets/backgrounds/default.jpg",
      "background_image_url": "https://example.com/backgrounds/default.jpg",
      "card_back_image": "assets/cards/card_back.png",
      "card_back_image_url": "https://example.com/cards/card_back.png"
    }
  },
  "assets": {
    "icons": {
      "money": {
        "path": "assets/icons/money.png",
        "url": "https://example.com/icons/money.png"
      },
      "reputation": {
        "path": "assets/icons/reputation.png",
        "url": "https://example.com/icons/reputation.png"
      }
    },
    "sounds": {
      "swipe": {
        "path": "assets/sounds/swipe.mp3",
        "url": "https://example.com/sounds/swipe.mp3"
      },
      "success": {
        "path": "assets/sounds/success.mp3",
        "url": "https://example.com/sounds/success.mp3"
      }
    }
  }
}
```

## Asset Handling

The game supports both local assets and remote URLs to accommodate different platforms:

### Local vs Remote Assets

- **Local Assets**: Use relative paths from the game directory (`assets/images/card1.png`)
- **Remote Assets**: Use full URLs (`https://example.com/images/card1.png`)

The game will try to load local assets first, then fall back to URLs when:
- Running on platforms without local file access (web browser)
- The local file isn't found

### Asset Types

```json
"assets": {
  "icons": {
    "resource_name": {
      "path": "local/path/to/icon.png",
      "url": "https://example.com/icon.png"
    }
  },
  "sounds": {
    "effect_name": {
      "path": "local/path/to/sound.mp3",
      "url": "https://example.com/sound.mp3"
    }
  }
}
```

### Theme Assets

Themes can include background images and other visual elements:

```json
"themes": {
  "default": {
    "background_color": "#f5f5f5",
    "background_image": "assets/backgrounds/default.jpg",
    "background_image_url": "https://example.com/backgrounds/default.jpg"
  }
}
```

## Required Sections

### Resources

Resources are the variables tracked by the game:

```json
"resources": {
  "money": {
    "initial": 1000,
    "min": 0,
    "max": 10000,
    "display_name": "Company Funds"
  },
  "reputation": {
    "initial": 50,
    "min": 0,
    "max": 100,
    "display_name": "Public Reputation"
  }
}
```

Each resource needs:
- `initial`: Starting value
- `min`: Minimum allowed value
- `max`: Maximum allowed value
- `display_name`: Human-readable name shown in UI

### Decisions

Decisions are the core gameplay element:

```json
"decisions": [
  {
    "id": "hire_developer",
    "text": "You need more programming help. Hire a junior or senior developer?",
    "image": "assets/hiring.png",
    "left": {
      "text": "Junior Developer (cheaper)",
      "effects": {
        "money": -500,
        "reputation": +2,
        "productivity": +5
      },
      "next": "office_space"
    },
    "right": {
      "text": "Senior Developer (experienced)",
      "effects": {
        "money": -2000,
        "reputation": +5,
        "productivity": +15
      },
      "next": "office_space"
    }
  }
]
```

Each decision needs:
- `id`: Unique identifier
- `text`: Description of the decision scenario
- `image`: Optional path to a local image file
- `image_url`: Optional URL to an online image (used on platforms where local files aren't accessible)
- `left` and `right` options, each containing:
  - `text`: Description of the choice
  - `effects`: How resources change when selected
  - `next`: ID of the next decision to show

## Example Starter Configuration

For a business simulator theme:

```json
{
  "metadata": {
    "name": "Startup Tycoon",
    "version": "1.0",
    "author": "SwipeFate Team",
    "description": "Build your tech startup from nothing to industry giant"
  },
  "resources": {
    "money": {
      "initial": 10000,
      "min": 0,
      "max": 1000000,
      "display_name": "Capital"
    },
    "reputation": {
      "initial": 20,
      "min": 0,
      "max": 100,
      "display_name": "Market Reputation"
    },
    "staff_morale": {
      "initial": 70,
      "min": 0,
      "max": 100,
      "display_name": "Team Morale"
    },
    "product_quality": {
      "initial": 50,
      "min": 0,
      "max": 100,
      "display_name": "Product Quality"
    }
  },
  "decisions": [
    {
      "id": "start",
      "text": "You're launching your startup. Focus on which aspect first?",
      "left": {
        "text": "Polished prototype (quality first)",
        "effects": {
          "money": -2000,
          "product_quality": +15
        },
        "next": "first_hire"
      },
      "right": {
        "text": "Quick market release (speed first)",
        "effects": {
          "money": -1000,
          "product_quality": +5,
          "reputation": +10
        },
        "next": "first_hire"
      }
    },
    {
      "id": "first_hire",
      "text": "Time to make your first hire. Who will it be?",
      "left": {
        "text": "Technical co-founder",
        "effects": {
          "money": -1000,
          "product_quality": +10,
          "staff_morale": +5
        },
        "next": "marketing"
      },
      "right": {
        "text": "Sales specialist",
        "effects": {
          "money": +500,
          "reputation": +10
        },
        "next": "marketing"
      }
    }
  ]
}
```

## Validation

The game validates configuration files against a schema to ensure they contain all required fields in the correct format. If validation fails, an error message will indicate what's missing or incorrect.