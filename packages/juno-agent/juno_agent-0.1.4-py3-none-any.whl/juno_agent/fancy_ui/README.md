# Fancy UI - Textual TUI Implementation

This module provides a modern Terminal User Interface (TUI) implementation for py-wizard-cli using the Textual framework.

## Welcome Screen Implementation

The welcome screen has been implemented as requested, displaying comprehensive system information in an elegant, organized way.

### Features

#### System Information Display
- **Working Directory**: Shows current working directory path
- **Git Status**: Displays git repository status with visual indicators
- **API Key Status**: Shows whether API key is configured 
- **Editor Status**: Displays selected editor or "Not selected"
- **Agent Configuration**: Shows agent/model configuration status

#### Visual Design
- **JUNO ASCII Art**: Branded header with JUNO AI CLI logo
- **Status Indicators**: Uses ✓, ✗, and ⚠️ symbols with color coding
- **Color Scheme**: 
  - Green (✓) for good status
  - Red (✗) for error status  
  - Yellow (⚠️) for warning status
- **Responsive Layout**: Adapts to different terminal sizes
- **Rich Styling**: Uses Rich markup for enhanced formatting

#### Setup Status
- Shows setup completion status
- Provides helpful guidance for next steps
- Visually distinct messaging for complete vs incomplete setup

### Architecture

#### Core Components

1. **WelcomeScreen Widget** (`widgets/welcome_screen.py`)
   - Main welcome screen widget
   - Integrates with ConfigManager and SystemStatus
   - Displays all system information

2. **PyWizardTUIApp** (`app.py`)
   - Main TUI application with screen management
   - Supports both welcome screen and chat interface
   - Handles navigation between screens

3. **Screen Management**
   - `WelcomeScreenView`: Welcome screen with key bindings
   - `ChatScreenView`: Chat interface screen
   - Seamless navigation between screens

#### Integration Points

- **ConfigManager**: Configuration management and persistence
- **SystemStatus**: System health and capability checking
- **TinyCodeAgentChat**: AI agent communication (in chat mode)

### Usage

#### Running with Welcome Screen
```python
from py_wizard_cli.config import ConfigManager
from py_wizard_cli.fancy_ui import PyWizardTUIApp

config_manager = ConfigManager(workdir)
app = PyWizardTUIApp(config_manager, show_welcome=True)
app.run()
```

#### Direct Chat Mode
```python
app = PyWizardTUIApp(config_manager, show_welcome=False)
app.run()
```

#### CLI Integration
The welcome screen is automatically shown when using fancy UI mode:
```bash
py-wizard-cli --ui-mode fancy
```

### Key Bindings

#### Welcome Screen
- **Enter/C**: Start chat interface
- **S**: Run setup wizard (planned)
- **Q/Escape**: Quit application

#### Chat Screen
- **Ctrl+W**: Return to welcome screen
- **Ctrl+C**: Clear chat
- **Ctrl+Q/Escape**: Quit application

### Styling

The welcome screen uses the same CSS framework as the rest of the TUI:
- Consistent color scheme with other components
- Responsive design that works on various terminal sizes
- Rich text formatting with proper contrast
- Professional appearance with clean borders and spacing

### Status Information

The welcome screen displays comprehensive status information:

1. **Working Directory**: Current project directory
2. **Git Status**: Repository status and location
3. **API Key**: Configuration status for AI features
4. **Editor**: Selected editor for integration
5. **Agent Configuration**: AI model and setup status

Each status item includes:
- Clear labeling
- Visual status indicators
- Color-coded feedback
- Helpful context information

### Integration with Existing Codebase

The welcome screen implementation:
- Maintains full compatibility with existing CLI commands
- Uses existing ConfigManager and SystemStatus classes
- Follows the modular architecture outlined in the product document
- Integrates seamlessly with the TinyAgent system
- Preserves all existing functionality while adding enhanced UI

### Testing

To test the welcome screen:

1. **Demo Script**: Run `demo_welcome_screen.py` for standalone testing
2. **Full Integration**: Use `--ui-mode fancy` with the main CLI
3. **Direct Import**: Import and test individual components

### Debugging Tool Usage Display

#### Log File Location and Purpose

The TUI automatically creates `app_run.log` in the current working directory containing:
- Complete tool usage flow traces from TinyAgent to UI display
- TextualToolCallback event processing
- UI update pipeline debugging information
- Message formatting and display operations

#### Quick Debugging Commands

```bash
# Monitor tool usage in real-time
tail -f app_run.log | grep -E "(TOOL_|ui_callback|MESSAGE_)"

# Check callback system health
grep -E "(textual_callback_initialized|callback.*added)" app_run.log

# Debug missing tool display
grep -A5 -B5 "no_ui_callback_available" app_run.log

# Find formatting issues
grep -E "(applying_tool_format|tool_pattern_applied)" app_run.log
```

#### Tool Usage Display Integration

The fancy UI integrates with the tool usage display system through:

1. **TextualToolCallback** (`callbacks/textual_tool_callback.py`): Captures tool events from TinyAgent
2. **UI Callback Pipeline**: Routes tool events to chat widgets
3. **Message Formatting**: Applies inline tool usage format `🔧 ToolName(args) ⏵`
4. **Chat Area Display**: Renders formatted tool usage within messages

**Expected Log Flow for Successful Tool Display:**
```
EVENT: textual_callback_initialized
TOOL_START: ToolName
EVENT: calling_ui_callback | message_type=tool_start
EVENT: ui_callback_completed
UI_UPDATE: ChatArea.add_tool_usage
UI_UPDATE: MessageWidget.update_content
EVENT: applying_tool_format
```

#### Common Debugging Scenarios

**Tool Usage Not Appearing:**
- Check: `grep "textual_callback_initialized" app_run.log` (callback creation)
- Check: `grep "TOOL_" app_run.log` (tool events)
- Check: `grep "no_ui_callback_available" app_run.log` (callback connection)

**Tool Events Processing But Not Displayed:**
- Check: `grep "ui_callback_failed" app_run.log` (callback errors)
- Check: `grep "MessageWidget" app_run.log` (widget updates)

For comprehensive debugging information, see the main TUI documentation: `product_manager/ui_tui.md#debugging-tool-usage-display`

### Future Enhancements

The welcome screen provides a foundation for:
- Setup wizard integration
- Real-time status updates
- Configuration management interface
- Help and documentation access
- Plugin and extension management

## Files

- `widgets/welcome_screen.py`: Main welcome screen implementation
- `app.py`: Enhanced TUI application with screen management
- `styles/chat.tcss`: Updated CSS with welcome screen styling
- `demo_welcome_screen.py`: Standalone demo application
- `README.md`: This documentation

The implementation follows the technical requirements and design specifications outlined in the product requirements document, providing a modern, intuitive interface that enhances the user experience while maintaining full feature parity with the existing CLI.