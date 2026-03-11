#!/usr/bin/env python3
"""Minimal computer-use MCP server for macOS."""
import asyncio, base64, os, subprocess, tempfile
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helper.js")
server = Server("computer-use")

def sh(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()

def jxa(*args):
    return sh("osascript", "-l", "JavaScript", HELPER, *[str(a) for a in args])

KEYS = {
    "return": 36, "enter": 36, "tab": 48, "space": 49, "delete": 51,
    "escape": 53, "esc": 53, "left": 123, "right": 124, "down": 125, "up": 126,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97,
    "f7": 98, "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
    "home": 115, "end": 119, "pageup": 116, "pagedown": 121,
}
MODS = {
    "command": "command down", "cmd": "command down", "shift": "shift down",
    "option": "option down", "alt": "option down",
    "control": "control down", "ctrl": "control down",
}

TOOLS = [
    Tool(name="screenshot", description="Screenshot. display_index (1-based) for multi-monitor.",
         inputSchema={"type": "object", "properties": {"display_index": {"type": "integer"}}}),
    Tool(name="click", description="Click at x,y.",
         inputSchema={"type": "object", "properties": {
             "x": {"type": "integer"}, "y": {"type": "integer"},
             "button": {"type": "string", "enum": ["left", "right"]},
             "clicks": {"type": "integer"}}, "required": ["x", "y"]}),
    Tool(name="type_text", description="Type a string.",
         inputSchema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}),
    Tool(name="press_key", description="Key combo, e.g. 'cmd+c', 'shift+tab', 'return'.",
         inputSchema={"type": "object", "properties": {"keys": {"type": "string"}}, "required": ["keys"]}),
    Tool(name="mouse_move", description="Move cursor to x,y.",
         inputSchema={"type": "object", "properties": {
             "x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}),
    Tool(name="scroll", description="Scroll at x,y. direction: up/down/left/right.",
         inputSchema={"type": "object", "properties": {
             "x": {"type": "integer"}, "y": {"type": "integer"},
             "direction": {"type": "string", "enum": ["up", "down", "left", "right"]},
             "amount": {"type": "integer"}}, "required": ["x", "y", "direction"]}),
    Tool(name="screen_info", description="Resolution and position of all displays.",
         inputSchema={"type": "object"}),
    Tool(name="cursor_position", description="Current cursor coordinates.",
         inputSchema={"type": "object"}),
]

@server.list_tools()
async def list_tools():
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "screenshot":
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            cmd = ["screencapture", "-x", "-t", "png"]
            d = arguments.get("display_index")
            if d:
                cmd += ["-D", str(d)]
            cmd.append(path)
            subprocess.run(cmd, check=True, timeout=10)
            with open(path, "rb") as f:
                data = base64.standard_b64encode(f.read()).decode()
            return [ImageContent(type="image", data=data, mimeType="image/png")]
        finally:
            os.unlink(path)

    elif name == "click":
        jxa("click", arguments["x"], arguments["y"],
            arguments.get("button", "left"), arguments.get("clicks", 1))

    elif name == "type_text":
        text = arguments["text"].replace("\\", "\\\\").replace('"', '\\"')
        sh("osascript", "-e", f'tell app "System Events" to keystroke "{text}"')

    elif name == "press_key":
        parts = [p.strip().lower() for p in arguments["keys"].split("+")]
        mods = [MODS[p] for p in parts if p in MODS]
        key = next((p for p in parts if p not in MODS), None)
        if not key:
            return [TextContent(type="text", text="no key specified")]
        using = f" using {{{', '.join(mods)}}}" if mods else ""
        if key in KEYS:
            sh("osascript", "-e", f'tell app "System Events" to key code {KEYS[key]}{using}')
        elif len(key) == 1:
            sh("osascript", "-e", f'tell app "System Events" to keystroke "{key}"{using}')
        else:
            return [TextContent(type="text", text=f"unknown key: {key}")]

    elif name == "mouse_move":
        jxa("move", arguments["x"], arguments["y"])

    elif name == "scroll":
        amt = arguments.get("amount", 3)
        dx, dy = {"up": (0, amt), "down": (0, -amt), "left": (amt, 0), "right": (-amt, 0)}[arguments["direction"]]
        jxa("scroll", arguments["x"], arguments["y"], dx, dy)

    elif name == "screen_info":
        return [TextContent(type="text", text=jxa("screens"))]

    elif name == "cursor_position":
        return [TextContent(type="text", text=jxa("cursor"))]

    return [TextContent(type="text", text="ok")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
