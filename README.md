# Echo MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/echo-mcp?style=flat-square&logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/echo-mcp/)
[![Python Version](https://img.shields.io/pypi/pyversions/echo-mcp?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/echo-mcp/)
[![License](https://img.shields.io/pypi/l/echo-mcp?style=flat-square&label=License)](https://pypi.org/project/echo-mcp/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/echo-mcp?period=total&units=ABBREVIATION&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/echo-mcp)
[![GitHub](https://img.shields.io/badge/GitHub-repo-blue?style=flat-square&logo=github)](https://github.com/bala-2305/echo-mcp)
[![MCP](https://img.shields.io/badge/MCP-compatible-brightgreen?style=flat-square)](https://modelcontextprotocol.io)

A Model Context Protocol (MCP) server that provides autonomous GUI automation capabilities to LLM clients (like Claude Desktop). This tool allows an AI to interact directly with your computer's screen, mouse, keyboard, and browser.

## Features

- **Computer Vision & OCR**: Extract text from screen regions and find UI elements visually.
- **Mouse & Keyboard Control**: Perform clicks, typing, hotkeys, and precise movements.
- **Window Management**: Focus, minimize, maximize, and query open windows.
- **System Automation**: Manage processes, execute system commands, adjust volume, and check system health.
- **Browser Automation**: Full web browsing capabilities (Selenium) for navigating, finding elements, extracting text, and clicking.
- **File System**: Read/write files, list directories, download files.

## Setup Instructions

### 1. Environment Requirements
- Python 3.12 or higher
- Windows (recommended for PyAutoGUI compatibility)

### 2. Installation
You can install the package directly from PyPI (https://pypi.org/project/echo-mcp/):

```powershell
pip install echo-mcp
```

### 3.Configuration
You can Configure your AI apps/IDE to make use of the mcp server by running the following command
```powershell
python -m echo_mcp.config
```

This will launch a CLI based setup wizard which help you to configure your AI apps/IDE to use the mcp server.
You will need to restart the app/IDE for the changes to take effect.

## Available Tools

The server provides a comprehensive suite of tools spanning multiple categories:

### Mouse & Keyboard
- `mouse_click`, `mouse_double_click`, `move_mouse`, `mouse_drag`, `mouse_scroll`, `get_mouse_position`
- `type_text`, `press_key`, `hotkey`

### Screen & Vision
- `take_screenshot`, `get_screen_size`, `get_text_at_coords`, `find_text_on_screen`, `click_element`

### Window & Process Management
- `list_all_windows`, `focus_window`, `maximize_window`, `minimize_window`, `get_window_geometry`, `close_all_windows_by_title`, `get_active_window_info`
- `list_processes`, `kill_process`, `get_process_stats`, `wait_for_process`

### System Utilities
- `system_power`, `set_volume`, `get_system_health`, `get_disk_usage`, `ping`, `list_network_interfaces`
- `launch_application`, `get_environment_variable`, `get_clipboard`, `set_clipboard`, `wait`

### File System
- `list_directory`, `read_file_content`, `write_to_file`, `delete_file`, `create_directory`, `download_file`

### Browser Automation
- `browser_open`, `browser_close`, `browser_navigate`, `browser_get_url`, `browser_get_title`, `browser_get_page_source`
- `browser_find_element`, `browser_click`, `browser_fill_form`, `browser_extract_text`
- `browser_screenshot`, `browser_scroll`, `browser_execute_script`, `browser_wait_for_element`

## Security Warning
**Giving an LLM control over your mouse and keyboard is powerful but risky.** Only run this server with prompts you trust, and never leave the automation unattended while active.
