#!/usr/bin/env python3

import time
import sys
import subprocess
import pyperclip
from pynput import keyboard
from .macos_helper import ensure_accessibility_permissions

def replace_text():
    """Perform the text replacement action"""
    # Small delay to ensure the hotkey release doesn't interfere
    time.sleep(0.2)

    # Save current clipboard content to restore later if needed
    old_clipboard = pyperclip.paste()

    # Clear clipboard to ensure we get fresh content
    pyperclip.copy('')

    # AppleScript to select all and copy in the frontmost application
    applescript = '''
    tell application "System Events"
        keystroke "a" using command down
        delay 0.2
        keystroke "c" using command down
    end tell
    '''

    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: Could not select and copy text")
        return

    # Give time for clipboard to update
    time.sleep(0.3)

    # Get the clipboard content
    try:
        text = pyperclip.paste()

        # Check if there's any text to process
        if not text:
            print("No text found in the focused area")
            pyperclip.copy(old_clipboard)  # Restore original clipboard
            return

        # Replace "helloworld" with "Hello World!"
        modified_text = text.replace("helloworld", "Hello World!")

        if text == modified_text:
            print("No 'helloworld' found to replace")
            pyperclip.copy(old_clipboard)  # Restore original clipboard
        else:
            # Put modified text back on clipboard
            pyperclip.copy(modified_text)

            # Paste using AppleScript to ensure it goes to the frontmost app
            paste_script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''

            subprocess.run(['osascript', '-e', paste_script], capture_output=True, text=True)

            count = text.count("helloworld")
            print(f"✓ Replaced {count} instance(s) of 'helloworld' with 'Hello World!'")
    except Exception as e:
        print(f"Error: {e}")
        pyperclip.copy(old_clipboard)  # Restore original clipboard on error

def main():
    # Check for accessibility permissions first
    if not ensure_accessibility_permissions():
        print("\nExiting: Accessibility permissions are required")
        sys.exit(1)

    print("\n" + "="*50)
    print("Wingman Run is running!")
    print("="*50)
    print("Hotkey: Ctrl+Option+Space")
    print("Action: Replaces 'helloworld' with 'Hello World!'")
    print("Press Ctrl+C to quit")
    print("-" * 50 + "\n")

    # Create a global hotkey listener
    def for_canonical(f):
        return lambda k: f(listener.canonical(k))

    # The hotkey combination - Ctrl+Option+Space
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+<alt>+<space>'),
        replace_text
    )

    # Listener for keyboard events
    with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)
    ) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nShutting down Wingman Run...")
            sys.exit(0)

if __name__ == '__main__':
    main()