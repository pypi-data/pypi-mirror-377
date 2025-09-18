# Welcome Message System

## Overview

This directory contains utilities for the TUI (Terminal User Interface), including the centralized welcome message builder system.

## WelcomeMessageBuilder

The `WelcomeMessageBuilder` class (`welcome_message_builder.py`) centralizes all welcome message construction for consistent UI across all components. This refactoring eliminates code duplication and makes future improvements easier and more developer-friendly.

### Features

- **Centralized Status Building**: Single place to manage all status indicators (Git, API, Editor, Agent, Model, AGENTS.md)
- **Rich Formatting Support**: Supports both plain text and Rich markup formatting
- **Consistent Branding**: Unified title, separators, and completion messages
- **Modular Design**: Individual methods for different components (title, status, completion message)

### Usage

```python
from ..utils.welcome_message_builder import WelcomeMessageBuilder

# Initialize with config and system status
welcome_builder = WelcomeMessageBuilder(config_manager, system_status)

# For TUI widgets (no Rich formatting)
title = welcome_builder.get_title_text()
status_line = welcome_builder.build_status_line(use_rich_formatting=False)
completion_msg = welcome_builder.build_completion_message(use_rich_formatting=False)

# For Rich-formatted text areas (with color markup)
welcome_text = welcome_builder.build_welcome_text(use_rich_formatting=True)
```

### Available Methods

#### Core Components
- `get_title_text()` - Plain title: "🧙‍♂️ JUNO AI CLI"
- `get_title_with_rich_formatting()` - Rich formatted title
- `get_separator_line()` - Consistent separator line
- `build_status_line(use_rich_formatting)` - Complete status line with all indicators

#### Status Components
- `build_status_parts()` - Individual status parts (plain text)
- `build_status_parts_with_rich_formatting()` - Individual status parts (Rich markup)
- `build_completion_message(use_rich_formatting)` - Setup completion message

#### Complete Messages
- `build_complete_welcome_parts(use_rich_formatting)` - All parts as list
- `build_welcome_text(use_rich_formatting)` - Complete message as string

### Status Indicators

The system displays these status indicators:

1. **📁 Working Directory** - Last two path parts (e.g., `...parent/current`)
2. **🔀 Git Status** - Git repository status (✓/✗)
3. **🔑 API Key** - API key configuration (✓/✗) 
4. **📝 Editor** - Selected editor (name + ✓/⚠)
5. **🤖 Agent** - Agent configuration status (✓/⚠)
6. **🧠 Model** - Configured model (name + ✓/✗)
7. **📋 AGENTS.md** - AGENTS.md file existence (✓/✗)

### Completion Messages

Based on setup state:
- **Setup Complete**: "✅ Ready to code! Type your questions below."
- **API Key Available**: "🚀 Ready to chat! Setup optional with /setup"
- **No API Key**: "🔧 Set API key with /apikey to start"

### Refactored Components

The following components now use the centralized builder:

1. **`app.py`** - `_create_welcome_message()` method
2. **`welcome_screen.py`** - `compose()` method

### Benefits

- **Single Source of Truth**: All welcome messages built from one place
- **Consistent Updates**: Changes automatically apply to all UI components
- **Easy Maintenance**: Add new status indicators in one location
- **Developer Friendly**: Clear API for different formatting needs
- **No Duplication**: Eliminates duplicate status building logic

### Future Enhancements

To add new status indicators:

1. Add the indicator logic to `build_status_parts()` and `build_status_parts_with_rich_formatting()`
2. The change automatically applies to both the main app and welcome screen widget
3. No need to update multiple files

### Migration Notes

This refactoring consolidated status building logic from:
- `app.py:_create_welcome_message()` - 70+ lines → 3 lines
- `welcome_screen.py:compose()` - 50+ lines → 20 lines
- Removed duplicate `_get_agent_status()` methods

The refactoring maintains 100% functional compatibility while significantly improving maintainability.