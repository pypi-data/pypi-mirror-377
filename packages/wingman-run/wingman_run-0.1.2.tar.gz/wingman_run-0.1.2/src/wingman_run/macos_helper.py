#!/usr/bin/env python3
"""
macOS helper functions for accessibility permissions
"""

import sys
import subprocess

def check_accessibility_permission():
    """Check if the app has accessibility permissions"""
    if sys.platform != 'darwin':
        return True

    try:
        import Quartz
        # Check if we're trusted
        from ApplicationServices import AXIsProcessTrusted
        return AXIsProcessTrusted()
    except ImportError:
        # Fallback to AppleScript method
        script = '''
        tell application "System Events"
            set assistive_access to (get UI elements enabled)
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip() == 'true'
        return False

def request_accessibility_permission():
    """Request accessibility permissions (will show system dialog)"""
    if sys.platform != 'darwin':
        return True

    try:
        import Quartz
        from ApplicationServices import AXIsProcessTrustedWithOptions
        from Cocoa import NSDictionary

        # Create options dictionary to prompt for permission
        options = NSDictionary.dictionaryWithDictionary_({'AXTrustedCheckOptionPrompt': True})

        # This will prompt the user if permissions haven't been granted
        return AXIsProcessTrustedWithOptions(options)
    except ImportError:
        print("Could not import required macOS frameworks")
        print("Please install pyobjc-framework-Quartz and pyobjc-framework-Cocoa")
        return False

def open_accessibility_settings():
    """Open the accessibility settings in System Preferences"""
    if sys.platform != 'darwin':
        return

    subprocess.run([
        'open',
        'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
    ])

def ensure_accessibility_permissions():
    """Ensure the app has accessibility permissions, prompting if necessary"""
    if not check_accessibility_permission():
        print("\n" + "="*60)
        print("ACCESSIBILITY PERMISSIONS REQUIRED")
        print("="*60)
        print("\nWingman Run needs accessibility permissions to:")
        print("- Monitor keyboard shortcuts")
        print("- Simulate keyboard input")
        print("\nRequesting permissions...")

        if not request_accessibility_permission():
            print("\nPlease grant accessibility permissions:")
            print("1. A dialog should appear asking for permissions")
            print("2. If not, go to System Preferences > Security & Privacy > Privacy > Accessibility")
            print("3. Add Terminal (or your Python app) to the list")
            print("4. Restart Wingman Run after granting permissions\n")

            # Open settings as a convenience
            open_accessibility_settings()
            return False

    return True