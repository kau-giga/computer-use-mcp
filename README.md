# computer-use-mcp

Minimal computer use MCP server for macOS. 186 lines, zero compiled binaries.

## Tools

| Tool | Description |
|------|-------------|
| `screenshot` | Capture screen (multi-monitor via `display_index`) |
| `click` | Mouse click at x,y (left/right, single/double/triple) |
| `type_text` | Type a string via AppleScript |
| `press_key` | Key combos like `cmd+c`, `shift+tab`, `return` |
| `mouse_move` | Move cursor to x,y |
| `scroll` | Scroll at x,y (up/down/left/right) |
| `screen_info` | Resolution, position, and scale of all displays |
| `cursor_position` | Current cursor coordinates |

## Architecture

- `server.py` — MCP stdio server (Python, uses `mcp` SDK)
- `helper.js` — JXA script calling CoreGraphics directly for mouse/scroll/cursor/screen info
- Screenshots via macOS built-in `screencapture`
- Keyboard input via AppleScript `System Events`

No compiled binaries. Fully auditable.

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USER/computer-use-mcp
cd computer-use-mcp

# Python venv
uv venv venv
uv pip install mcp --python venv/bin/python

# Register with Claude Code
claude mcp add computer-use -- $(pwd)/venv/bin/python $(pwd)/server.py
```

## Permissions

Grant to your terminal app (one-time):
- **System Settings → Privacy & Security → Accessibility**
- **System Settings → Privacy & Security → Screen Recording**

## Multi-Monitor

`screen_info` returns all displays with CG coordinates:
```json
[
  {"index": 1, "width": 1512, "height": 982, "x": 0, "y": 0, "scale": 2, "main": true},
  {"index": 2, "width": 2560, "height": 1440, "x": -2560, "y": -293, "scale": 2, "main": false}
]
```

Use `display_index` parameter with `screenshot` to capture specific monitors.

## License

MIT
