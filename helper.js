#!/usr/bin/env osascript -l JavaScript
// Minimal macOS input helper via JXA. No compilation needed.
// Usage: osascript helper.js <click|move|scroll|cursor|screens> [args]
ObjC.import('CoreGraphics');
ObjC.import('AppKit');

const args = $.NSProcessInfo.processInfo.arguments;
const cmd = ObjC.unwrap(args.objectAtIndex(4));
function arg(i) { return ObjC.unwrap(args.objectAtIndex(i)); }
function num(i) { return Number(arg(i)); }

function click(x, y, button, clicks) {
    const point = $.CGPointMake(x, y);
    const isRight = button === 'right';
    const downType = isRight ? $.kCGEventRightMouseDown : $.kCGEventLeftMouseDown;
    const upType = isRight ? $.kCGEventRightMouseUp : $.kCGEventLeftMouseUp;
    const btn = isRight ? $.kCGMouseButtonRight : $.kCGMouseButtonLeft;
    for (let i = 1; i <= clicks; i++) {
        const down = $.CGEventCreateMouseEvent($(), downType, point, btn);
        const up = $.CGEventCreateMouseEvent($(), upType, point, btn);
        $.CGEventSetIntegerValueField(down, $.kCGMouseEventClickState, i);
        $.CGEventSetIntegerValueField(up, $.kCGMouseEventClickState, i);
        $.CGEventPost($.kCGHIDEventTap, down);
        $.CGEventPost($.kCGHIDEventTap, up);
        delay(0.03);
    }
}

switch (cmd) {
    case 'click':
        click(num(5), num(6), args.count > 7 ? arg(7) : 'left', args.count > 8 ? num(8) : 1);
        break;
    case 'move':
        $.CGWarpMouseCursorPosition($.CGPointMake(num(5), num(6)));
        break;
    case 'scroll': {
        $.CGWarpMouseCursorPosition($.CGPointMake(num(5), num(6)));
        const ev = $.CGEventCreateScrollWheelEvent($(), $.kCGScrollEventUnitLine, 2, num(8), num(7));
        $.CGEventPost($.kCGHIDEventTap, ev);
        break;
    }
    case 'cursor': {
        const ev = $.CGEventCreate($());
        const loc = $.CGEventGetLocation(ev);
        `${Math.round(loc.x)},${Math.round(loc.y)}`;
        break;
    }
    case 'screens': {
        const screens = $.NSScreen.screens;
        const mainH = $.NSScreen.mainScreen.frame.size.height;
        const result = [];
        for (let i = 0; i < screens.count; i++) {
            const f = screens.objectAtIndex(i).frame;
            result.push({
                index: i + 1, width: Math.round(f.size.width), height: Math.round(f.size.height),
                x: Math.round(f.origin.x), y: Math.round(mainH - f.origin.y - f.size.height),
                scale: screens.objectAtIndex(i).backingScaleFactor, main: i === 0
            });
        }
        JSON.stringify(result);
        break;
    }
    default:
        ObjC.import('stdlib'); $.exit(1);
}
