# Window Management Features

The Windows Agent now includes comprehensive window management capabilities to control application windows.

## New Features

### 1. List Windows
```bash
win windows
```
Lists all visible windows with their PID, state (normal/minimized/maximized), and title.

### 2. Focus Window
```bash
win focus "Steam"
```
Brings the specified window to the foreground. If the window is minimized, it will be restored first.

### 3. Maximize Window
```bash
win maximize "Steam"
```
Maximizes the specified window to fill the screen.

### 4. Minimize Window
```bash
win minimize "Steam"
```
Minimizes the specified window to the taskbar.

### 5. Restore Window
```bash
win restore "Steam"
```
Restores a window to its normal size (not maximized or minimized).

### 6. Combined Focus + Maximize
```bash
win window "Steam"
```
Convenience command that focuses a window and then maximizes it.

## Usage Examples

### Open and Maximize Steam
```bash
# Start Steam if not running
win ps "Start-Process steam://"

# Wait a moment for it to load
sleep 3

# Focus and maximize
win window "Steam"
```

### Check Window State
```python
from windows_control import WindowsControl
win = WindowsControl()

# Get window state
state = win.window_state(title="Steam")
print(f"State: {state['state']}")  # 'normal', 'minimized', or 'maximized'
print(f"Position: {state['rect']}")
```

### Find Specific Window
```python
# List all windows
windows = win.list_windows()

# Find Steam
for w in windows:
    if 'steam' in w['title'].lower():
        print(f"Found: {w['title']} (PID: {w['pid']}, State: {w['state']})")
```

## API Endpoints

The Windows Agent provides these REST API endpoints:

- `GET /window/list` - List all visible windows
- `POST /window/focus` - Bring window to foreground
- `POST /window/maximize` - Maximize window
- `POST /window/minimize` - Minimize window
- `POST /window/restore` - Restore window to normal size
- `POST /window/state` - Get current window state

Each endpoint accepts either `title` (partial match) or `pid` in the request body.

## Benefits

1. **No More Minimized Windows**: When launching applications via PowerShell, they often start minimized. Now you can automatically bring them to front and maximize.

2. **Better Control**: Full window state management for automation tasks.

3. **Multi-Window Support**: Handle multiple application windows programmatically.

4. **State Detection**: Know if a window is minimized, maximized, or normal.

## Installation

1. Update Windows Agent:
   - The windows_agent.py file now includes win32gui import and window management endpoints

2. Restart Windows Agent:
   ```cmd
   python windows_agent.py
   ```

3. Test from WSL:
   ```bash
   win windows
   win focus "Steam"
   win maximize "Steam"
   ```

## Troubleshooting

- **"404 Not Found" Error**: Windows Agent needs to be restarted after updating
- **"Window not found"**: Make sure the window title matches (partial match is supported)
- **Permission Issues**: Some system windows may require admin privileges