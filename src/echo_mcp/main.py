import mcp.server.fastmcp as fastmcp
import pyautogui
from PIL import ImageGrab, Image
import os
import tempfile
import time
import base64
import io
import subprocess
import psutil
import pygetwindow as gw
import pytesseract
import webbrowser
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

mcp_server = fastmcp.FastMCP("PyAutoControl")

# Global browser instance
_browser = None

def get_browser():
    """Get or create browser instance."""
    global _browser
    if _browser is None:
        options = webdriver.ChromeOptions()
        service = Service(ChromeDriverManager().install())
        _browser = webdriver.Chrome(service=service, options=options)
    return _browser

def close_browser():
    """Close browser instance."""
    global _browser
    if _browser is not None:
        _browser.quit()
        _browser = None

@mcp_server.tool()
def get_text_at_coords(x: int, y: int, w: int, h: int) -> str:
    """OCR text in region."""
    try:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def find_text_on_screen(text: str) -> str:
    """Find text coords via OCR."""
    try:
        img = ImageGrab.grab()
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data['text']):
            if text.lower() in word.lower():
                return f"{data['left'][i]},{data['top'][i]}"
        return "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def set_volume(level: int) -> str:
    """Set vol 0-100 (Windows via PowerShell)."""
    try:
        level = max(0, min(100, level))  # Clamp 0-100
        ps_script = f"""
[Windows.Media.Devices.MediaDevice, Windows.Media.Devices.MediaDevice, ContentType = WindowsRuntime] > $null
[Windows.Media.Devices.MediaDevice]::GetDefaultAudioPlaybackDevice().Volume = {level / 100.0}
"""
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        return "OK" if result.returncode == 0 else f"Err: {result.stderr}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def get_window_geometry(title: str) -> str:
    """Get {x,y,w,h} of window."""
    try:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            w = wins[0]
            return f"{w.left},{w.top},{w.width},{w.height}"
        return "None"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def close_all_windows_by_title(title: str) -> str:
    """Close windows by title."""
    try:
        wins = gw.getWindowsWithTitle(title)
        for w in wins: w.close()
        return f"Closed {len(wins)}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def system_power(action: str) -> str:
    """shutdown/reboot/logoff."""
    try:
        cmd = {"shutdown": "shutdown /s /t 1", "reboot": "shutdown /r /t 1", "logoff": "shutdown /l"}
        if action in cmd:
            os.system(cmd[action])
            return "OK"
        return "Invalid action"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def ping(host: str) -> str:
    """Ping host."""
    try:
        res = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True)
        return "Up" if res.returncode == 0 else "Down"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def download_file(url: str, path: str) -> str:
    """Download URL to path."""
    try:
        r = requests.get(url, stream=True)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        return "OK"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def get_process_stats(name: str) -> str:
    """Get CPU/Mem for process name."""
    try:
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            if p.info['name'].lower() == name.lower():
                return f"CPU:{p.info['cpu_percent']}% Mem:{p.info['memory_percent']:.1f}%"
        return "None"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def wait_for_process(name: str, timeout: int = 30) -> str:
    """Wait for process to start."""
    start = time.time()
    while time.time() - start < timeout:
        if any(p.info['name'].lower() == name.lower() for p in psutil.process_iter(['name'])):
            return "Started"
        time.sleep(1)
    return "Timeout"

@mcp_server.tool()
def get_active_window_info() -> str:
    """Get title and location of focused window."""
    try:
        window = gw.getActiveWindow()
        return f"{window.title} @ {window.topleft}" if window else "None"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def kill_process(process_name: str) -> str:
    """Kill process by name."""
    try:
        count = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                proc.kill()
                count += 1
        return f"Killed {count}" if count > 0 else "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def get_system_health() -> str:
    """Get CPU, Mem, Battery %."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        res = f"CPU:{cpu}% Mem:{mem}%"
        if battery:
            res += f" Bat:{battery.percent}% ({'Chg' if battery.power_plugged else 'Dis'})"
        return res
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def launch_application(app_name_or_path: str) -> str:
    """Launch app/path."""
    try:
        subprocess.Popen(app_name_or_path, shell=True)
        return f"Launched {app_name_or_path}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def get_screen_size() -> str:
    """Get resolution."""
    return "x".join(map(str, pyautogui.size()))

@mcp_server.tool()
def mouse_click(x: int, y: int, button: str = "left") -> str:
    """Click (x,y)."""
    pyautogui.click(x, y, button=button)
    return f"Clicked {button} ({x},{y})"

@mcp_server.tool()
def click_element(image_path: str, confidence: float = 0.8, retries: int = 3, delay: float = 1.0) -> str:
    """Click image template on screen."""
    try:
        for _ in range(retries):
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if loc:
                pyautogui.click(loc)
                return f"OK: {loc}"
            time.sleep(delay)
        return "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def type_text(text: str, interval: float = 0.1) -> str:
    """Type text."""
    pyautogui.typewrite(text, interval=interval)
    return "Typed"

@mcp_server.tool()
def take_screenshot() -> str:
    """Screen -> base64 PNG."""
    try:
        screenshot = ImageGrab.grab()
        buf = io.BytesIO()
        screenshot.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def list_directory(path: str = ".") -> str:
    """List dir."""
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def read_file_content(path: str) -> str:
    """Read file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def write_to_file(path: str, content: str) -> str:
    """Write file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "Saved"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def move_mouse(x: int, y: int, duration: float = 0.5) -> str:
    """Move mouse."""
    pyautogui.moveTo(x, y, duration=duration)
    return f"Moved ({x},{y})"

@mcp_server.tool()
def mouse_drag(x: int, y: int, duration: float = 0.5) -> str:
    """Drag mouse."""
    pyautogui.dragTo(x, y, duration=duration)
    return f"Dragged ({x},{y})"

@mcp_server.tool()
def mouse_scroll(clicks: int) -> str:
    """Scroll wheel."""
    pyautogui.scroll(clicks)
    return f"Scrolled {clicks}"

@mcp_server.tool()
def press_key(key: str) -> str:
    """Press key."""
    pyautogui.press(key)
    return f"Pressed {key}"

@mcp_server.tool()
def hotkey(keys: list[str]) -> str:
    """Hotkey combo."""
    pyautogui.hotkey(*keys)
    return f"Pressed {'+'.join(keys)}"

@mcp_server.tool()
def mouse_double_click(x: int, y: int) -> str:
    """Double click."""
    pyautogui.doubleClick(x, y)
    return f"Double click ({x},{y})"

@mcp_server.tool()
def get_mouse_position() -> str:
    """Get (x,y)."""
    return str(pyautogui.position())

@mcp_server.tool()
def list_all_windows() -> str:
    """List window titles."""
    return "\n".join([w.title for w in gw.getAllWindows() if w.title])

@mcp_server.tool()
def focus_window(title: str) -> str:
    """Focus window."""
    try:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            wins[0].activate()
            return f"Focused {wins[0].title}"
        return "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def maximize_window(title: str) -> str:
    """Maximize window."""
    try:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            wins[0].maximize()
            return "Maximized"
        return "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def minimize_window(title: str) -> str:
    """Minimize window."""
    try:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            wins[0].minimize()
            return "Minimized"
        return "Not found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def list_processes() -> str:
    """List PID/Name (limit 100)."""
    procs = [f"{p.info['name']} ({p.info['pid']})" for p in psutil.process_iter(['pid', 'name'])]
    return "\n".join(procs[:100])

@mcp_server.tool()
def get_disk_usage() -> str:
    """Disk stats."""
    u = psutil.disk_usage('/')
    return f"T:{u.total//10**9}G U:{u.used//10**9}G F:{u.free//10**9}G {u.percent}%"

@mcp_server.tool()
def delete_file(path: str) -> str:
    """Delete file."""
    try:
        os.remove(path)
        return "Deleted"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def create_directory(path: str) -> str:
    """Mkdir -p."""
    try:
        os.makedirs(path, exist_ok=True)
        return "Created"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def wait(seconds: float) -> str:
    """Sleep."""
    time.sleep(seconds)
    return "Done"

@mcp_server.tool()
def get_clipboard() -> str:
    """Get clipboard text."""
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def set_clipboard(text: str) -> str:
    """Set clipboard text."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return "Copied"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def open_url(url: str) -> str:
    """Open browser."""
    import webbrowser
    webbrowser.open(url)
    return "Opened"

@mcp_server.tool()
def get_environment_variable(name: str) -> str:
    """Get ENV var."""
    return f"{name}={os.environ.get(name, 'None')}"

@mcp_server.tool()
def list_network_interfaces() -> str:
    """List Interface:IP."""
    res = []
    for intf, snics in psutil.net_if_addrs().items():
        ips = [s.address for s in snics if s.family == 2]
        if ips: res.append(f"{intf}: {','.join(ips)}")
    return "\n".join(res)


@mcp_server.tool()
def browser_open(headless: bool = False) -> str:
    """Open Chrome browser."""
    try:
        browser = get_browser()
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        return "Browser opened"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_navigate(url: str) -> str:
    """Navigate to URL."""
    try:
        browser = get_browser()
        browser.get(url)
        return f"Navigated to {url}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_find_element(selector: str, by: str = "css") -> str:
    """Find element by selector (css|xpath|id|class|name)."""
    try:
        browser = get_browser()
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME
        }
        loc_by = by_map.get(by, By.CSS_SELECTOR)
        element = browser.find_element(loc_by, selector)
        return f"Found: {element.tag_name} - {element.text[:50] if element.text else 'no text'}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_click(selector: str, by: str = "css") -> str:
    """Click element."""
    try:
        browser = get_browser()
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME
        }
        loc_by = by_map.get(by, By.CSS_SELECTOR)
        element = browser.find_element(loc_by, selector)
        element.click()
        return "Clicked"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_fill_form(selector: str, text: str, by: str = "css", clear: bool = True) -> str:
    """Fill form field with text."""
    try:
        browser = get_browser()
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME
        }
        loc_by = by_map.get(by, By.CSS_SELECTOR)
        element = browser.find_element(loc_by, selector)
        if clear:
            element.clear()
        element.send_keys(text)
        return "Filled"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_extract_text(selector: str, by: str = "css") -> str:
    """Extract text from element."""
    try:
        browser = get_browser()
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME
        }
        loc_by = by_map.get(by, By.CSS_SELECTOR)
        element = browser.find_element(loc_by, selector)
        return element.text
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_screenshot() -> str:
    """Capture page screenshot -> base64 PNG."""
    try:
        browser = get_browser()
        screenshot = browser.get_screenshot_as_png()
        return f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_get_page_source() -> str:
    """Get HTML source of page."""
    try:
        browser = get_browser()
        return browser.page_source
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_execute_script(script: str) -> str:
    """Execute JavaScript on page."""
    try:
        browser = get_browser()
        result = browser.execute_script(script)
        return str(result)
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_wait_for_element(selector: str, by: str = "css", timeout: int = 10) -> str:
    """Wait for element to appear (up to timeout seconds)."""
    try:
        browser = get_browser()
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME
        }
        loc_by = by_map.get(by, By.CSS_SELECTOR)
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((loc_by, selector))
        )
        return "Element found"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_get_title() -> str:
    """Get page title."""
    try:
        browser = get_browser()
        return browser.title
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_get_url() -> str:
    """Get current URL."""
    try:
        browser = get_browser()
        return browser.current_url
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_close() -> str:
    """Close browser."""
    try:
        close_browser()
        return "Browser closed"
    except Exception as e:
        return f"Err: {e}"

@mcp_server.tool()
def browser_scroll(direction: str = "down", amount: int = 3) -> str:
    """Scroll page (up/down)."""
    try:
        browser = get_browser()
        if direction.lower() == "down":
            browser.execute_script(f"window.scrollBy(0, {amount * 100});")
        else:
            browser.execute_script(f"window.scrollBy(0, {-amount * 100});")
        return f"Scrolled {direction}"
    except Exception as e:
        return f"Err: {e}"

def main():
    """Main entry point for the PyAutoControl MCP server."""
    mcp_server.run()

if __name__ == "__main__":
    main()

