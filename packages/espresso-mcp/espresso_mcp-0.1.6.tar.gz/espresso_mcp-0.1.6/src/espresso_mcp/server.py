import logging
import subprocess
from datetime import datetime
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP
from PIL import Image as PILImage

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Setup Console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# Create an MCP server
mcp = FastMCP("Espresso-MCP")


@mcp.tool()
def list_avds() -> list:
    """List all available Android Virtual Devices (AVDs)"""
    result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error listing AVDs: {result.stderr}")
    return result.stdout.splitlines()


@mcp.tool()
def list_emulators() -> list:
    """List all running Android Emulators"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error listing emulators: {result.stderr}")
    lines = result.stdout.splitlines()
    print("---lines", lines)
    emulators = [line.split()[0] for line in lines[1:] if "emulator" in line]
    return emulators


@mcp.tool()
def start_emulator(emulator_name: str) -> str:
    """Start an Android Emulator by name"""
    result = subprocess.Popen(
        ["emulator", "-avd", emulator_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return f"Emulator '{emulator_name}' is starting."


@mcp.tool()
def kill_emulator(emulator_name: str) -> str:
    """Kill a specific Android Emulator"""
    result = subprocess.run(
        ["adb", "-s", emulator_name, "emu", "kill"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error killing emulator '{emulator_name}': {result.stderr}")
    return f"Emulator '{emulator_name}' has been killed."


@mcp.tool()
def dump_ui_hierarchy() -> str:
    """Dump the UI hierarchy of the connected Android device"""
    result = subprocess.run(["adb", "shell", "uiautomator", "dump"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error dumping UI hierarchy: {result.stderr}")

    # The UI hierarchy is dumped to a file on the device /sdcard/window_dump.xml
    # Pull the file to the local machine and read its contents
    pull_result = subprocess.run(
        ["adb", "pull", "/sdcard/window_dump.xml", "window_dump.xml"],
        capture_output=True,
        text=True,
    )
    if pull_result.returncode != 0:
        raise RuntimeError(f"Error pulling UI hierarchy file: {pull_result.stderr}")

    with open("window_dump.xml", encoding="utf-8") as f:
        ui_hierarchy = f.read()
    return ui_hierarchy


@mcp.tool()
def open_uri(uri: str) -> str:
    """Open a URI on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", uri],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error opening URI '{uri}': {result.stderr}")
    return f"URI '{uri}' has been opened successfully."


@mcp.tool()
def list_apps() -> list:
    """List all installed apps on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "pm", "list", "packages"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error listing installed apps: {result.stderr}")
    apps = [line.replace("package:", "").strip() for line in result.stdout.splitlines()]
    return apps


@mcp.tool()
def start_app(package_name: str) -> str:
    """Start an app on the connected Android device"""
    result = subprocess.run(
        [
            "adb",
            "shell",
            "monkey",
            "-p",
            package_name,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error starting app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been started successfully."


@mcp.tool()
def stop_app(package_name: str) -> str:
    """Stop an app on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "am", "force-stop", package_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error stopping app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been stopped successfully."


@mcp.tool()
def install_app(app_path: str) -> str:
    """Install an App APK on the connected Android device"""
    result = subprocess.run(["adb", "install", app_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error installing App: {result.stderr}")
    return f"App '{app_path}' has been installed successfully."


@mcp.tool()
def uninstall_app(package_name: str) -> str:
    """Uninstall an app from the connected Android device"""
    result = subprocess.run(["adb", "uninstall", package_name], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error uninstalling app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been uninstalled successfully."


@mcp.tool()
def clear_app_data(package_name: str) -> str:
    """Clear app data for a specific app on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "pm", "clear", package_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error clearing app data for '{package_name}': {result.stderr}")
    return f"App data for '{package_name}' has been cleared."


@mcp.tool()
def take_screenshot(output_path: str) -> str:
    """Take a screenshot of the connected Android device"""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file = f"/sdcard/espresso-mcp_screenshot_{timestamp}.mp4"

    # Capture screenshot on the device
    subprocess.run(["adb", "shell", "screencap", "-p", file], check=True)
    # Pull the screenshot to the local machine
    subprocess.run(["adb", "pull", file, "screenshot.png"], check=True)
    # Remove the screenshot from the device
    subprocess.run(["adb", "shell", "rm", file], check=True)

    # Compress the screenshot to reduce size
    with PILImage.open("screenshot.png") as img:
        width, height = img.size
        new_width = int(width * 0.3)
        new_height = int(height * 0.3)
        resized_img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        resized_img.save(output_path, "PNG", quality=85, optimize=True)

    return f"Screenshot saved to '{output_path}'."


@mcp.tool()
def record_screen(output_path: str, duration: int) -> str:
    """Record the screen of the connected Android device for a specified duration"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file = f"/sdcard/espresso-mcp_recording_{timestamp}.mp4"
    result = subprocess.run(
        ["adb", "shell", "screenrecord", file],
        capture_output=True,
        text=True,
        timeout=duration,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error recording screen: {result.stderr}")

    pull_result = subprocess.run(
        ["adb", "pull", file, output_path],
        capture_output=True,
        text=True,
    )
    if pull_result.returncode != 0:
        raise RuntimeError(f"Error pulling recorded file: {pull_result.stderr}")
    return f"Screen recording saved to '{output_path}'."


class Button(Enum):
    HOME = "3"
    BACK = "4"
    MENU = "82"
    POWER = "26"
    VOLUME_UP = "24"
    VOLUME_DOWN = "25"
    CAMERA = "27"
    ENTER = "66"


@mcp.tool()
def press_button(button: Button) -> str:
    """Simulate a button press on the connected Android device using an Enum button"""
    result = subprocess.run(
        ["adb", "shell", "input", "keyevent", button.value],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error pressing button '{button.name}': {result.stderr}")
    return f"Button '{button.name}' has been pressed."


@mcp.tool()
def type_text(text: str) -> str:
    """Type text on the connected Android device. Handles spaces correctly."""
    # Replace spaces with %s for adb input
    adb_text = text.replace(" ", "%s")
    result = subprocess.run(
        ["adb", "shell", "input", "text", adb_text],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error typing text '{text}': {result.stderr}")
    return f"Text '{text}' has been typed successfully."


@mcp.tool()
def clear_and_type_text(text: str) -> str:
    """Clear all text and type new text on the connected Android device"""
    # Clear existing text by selecting all and deleting
    move_home = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_MOVE_HOME"],
        capture_output=True,
        text=True,
    )
    if move_home.returncode != 0:
        raise RuntimeError(f"Error moving cursor to start: {move_home.stderr}")

    # Try to select all (long-press SHIFT + move to end)
    shift_down = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_SHIFT_LEFT"],
        capture_output=True,
        text=True,
    )
    if shift_down.returncode != 0:
        raise RuntimeError(f"Error pressing SHIFT: {shift_down.stderr}")

    move_end = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_MOVE_END"],
        capture_output=True,
        text=True,
    )
    if move_end.returncode != 0:
        raise RuntimeError(f"Error moving cursor to end: {move_end.stderr}")

    # Delete selected text
    delete = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_DEL"],
        capture_output=True,
        text=True,
    )
    if delete.returncode != 0:
        raise RuntimeError(f"Error clearing text: {delete.stderr}")

    # Type new text
    adb_text = text.replace(" ", "%s")
    type_result = subprocess.run(
        ["adb", "shell", "input", "text", adb_text],
        capture_output=True,
        text=True,
    )
    if type_result.returncode != 0:
        raise RuntimeError(f"Error typing text '{text}': {type_result.stderr}")

    return f"Cleared existing text and typed '{text}' successfully."


@mcp.tool()
def tap(x: int, y: int) -> str:
    """Simulate a tap on the connected Android device at the specified coordinates"""
    result = subprocess.run(
        ["adb", "shell", "input", "tap", str(x), str(y)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error performing tap at ({x}, {y}): {result.stderr}")
    return f"Tap performed at coordinates ({x}, {y})."


@mcp.tool()
def swipe(direction: str, duration: int = 500) -> str:
    """Perform a swipe gesture in a specific direction on the connected Android device"""
    directions = {
        "up": (500, 1500, 500, 500),
        "down": (500, 500, 500, 1500),
        "left": (1500, 500, 500, 500),
        "right": (500, 500, 1500, 500),
    }
    if direction not in directions:
        raise ValueError(
            f"Invalid direction '{direction}'. Valid directions are: {list(directions.keys())}"
        )

    start_x, start_y, end_x, end_y = directions[direction]
    result = subprocess.run(
        [
            "adb",
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error performing swipe: {result.stderr}")
    return f"Swipe gesture performed in '{direction}' direction over {duration}ms."


@mcp.tool()
def dump_current_activity() -> str:
    """Dump the current activity name of the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "activity", "activities"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error dumping current activity: {result.stderr}")
    
    # Parse the output to find the current activity
    output = result.stdout
    lines = output.splitlines()
    
    # Look for the "mResumedActivity" line which contains the current activity
    for line in lines:
        if "mResumedActivity" in line:
            # Extract activity name from the line
            # Format: mResumedActivity: ActivityRecord{...component=package.name/.ActivityName...}
            if "component=" in line:
                component_part = line.split("component=")[1]
                activity_name = component_part.split(" ")[0].split("}")[0]
                return f"Current activity: {activity_name}"
    
    # Alternative: look for "Running activities" section and get the top one
    in_running_activities = False
    for line in lines:
        if "Running activities" in line:
            in_running_activities = True
            continue
        if in_running_activities and "ActivityRecord" in line and "state=RESUMED" in line:
            # Extract activity name from ActivityRecord line
            if " " in line and "/" in line:
                parts = line.strip().split()
                for part in parts:
                    if "/" in part and "." in part:
                        activity_name = part
                        return f"Current activity: {activity_name}"
    
    return "Current activity information not found in dumpsys output"


@mcp.tool()
def replace_text(text: str) -> str:
    """Replace text on the connected Android device by clearing current text and typing new text"""
    # Try using Ctrl+A to select all text
    ctrl_a = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_CTRL_LEFT", "KEYCODE_A"],
        capture_output=True,
        text=True,
    )
    
    # If Ctrl+A doesn't work, try alternative selection methods
    if ctrl_a.returncode != 0:
        # Method 1: Select all using key combination
        select_all_combo = subprocess.run(
            ["adb", "shell", "input", "keyevent", "29", "29", "29"],  # Multiple Ctrl+A attempts
            capture_output=True,
            text=True,
        )
        
        if select_all_combo.returncode != 0:
            # Method 2: Move to start, then select to end
            move_home = subprocess.run(
                ["adb", "shell", "input", "keyevent", "KEYCODE_MOVE_HOME"],
                capture_output=True,
                text=True,
            )
            if move_home.returncode == 0:
                # Hold shift and move to end
                subprocess.run(
                    ["adb", "shell", "input", "keyevent", "KEYCODE_SHIFT_LEFT"],
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    ["adb", "shell", "input", "keyevent", "KEYCODE_MOVE_END"],
                    capture_output=True,
                    text=True,
                )
    
    # Clear the selected text by pressing delete/backspace
    delete = subprocess.run(
        ["adb", "shell", "input", "keyevent", "KEYCODE_DEL"],
        capture_output=True,
        text=True,
    )
    if delete.returncode != 0:
        # If delete doesn't work, try backspace
        backspace = subprocess.run(
            ["adb", "shell", "input", "keyevent", "KEYCODE_BACK"],
            capture_output=True,
            text=True,
        )
        if backspace.returncode != 0:
            raise RuntimeError("Error clearing text: unable to delete selected text")
    
    # Type the new text
    adb_text = text.replace(" ", "%s")
    type_result = subprocess.run(
        ["adb", "shell", "input", "text", adb_text],
        capture_output=True,
        text=True,
    )
    if type_result.returncode != 0:
        raise RuntimeError(f"Error typing text '{text}': {type_result.stderr}")
    
    return f"Replaced text with '{text}' successfully."


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


def main():
    # Start the MCP server
    print("Starting Espresso MCP server...")

    import argparse

    parser = argparse.ArgumentParser(description="Run MCP Server")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3333, help="Port to listen on")
    args = parser.parse_args()

    transport = "stdio"  # Default transport
    if args.sse:
        transport = "sse"

    # mcp.run()
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
