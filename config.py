import json
import os
import subprocess
from pathlib import Path

SERVER_NAME = "EchoMCP"
PACKAGE_NAME = "echo-mcp"


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def install_uv():
    print("[INFO] Installing uv...")

    try:
        subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "irm https://astral.sh/uv/install.ps1 | iex"
            ],
            check=True
        )

        print("[OK] uv installed")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to install uv: {e}")
        return False


def find_uvx():
    output = run_command(["where", "uvx"])

    if output:
        for line in output.splitlines():
            if line.lower().endswith("uvx.exe"):
                return line.strip()

    possible_paths = [
        Path.home() / ".local" / "bin" / "uvx.exe",
        Path.home() / ".cargo" / "bin" / "uvx.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "uv" / "uvx.exe",
        Path.home() / "AppData" / "Roaming" / "Python" / "Scripts" / "uvx.exe",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return None


def ensure_uvx():
    uvx = find_uvx()

    if uvx:
        return uvx

    print("[INFO] uvx.exe not found")

    if not install_uv():
        return None

    uvx = find_uvx()

    if uvx:
        return uvx

    raise RuntimeError(
        "uv was installed but uvx.exe could not be located."
    )


def load_json(path):
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def update_mcp_file(path, uvx_path):
    config = load_json(path)

    config.setdefault("mcpServers", {})

    config["mcpServers"][SERVER_NAME] = {
        "command": uvx_path,
        "args": [
            PACKAGE_NAME
        ]
    }

    save_json(path, config)

    print(f"[UPDATED] {path}")


def main():
    print("=" * 60)
    print("Echo MCP Installer")
    print("=" * 60)

    uvx_path = ensure_uvx()

    print(f"[OK] Using uvx:")
    print(uvx_path)

    # Claude Desktop
    appdata = os.getenv("APPDATA")

    claude_config = (
        Path(appdata)
        / "Claude"
        / "claude_desktop_config.json"
    )

    # Global Cursor MCP Config
    cursor_config = (
        Path.home()
        / ".cursor"
        / "mcp.json"
    )

    update_mcp_file(claude_config, uvx_path)
    update_mcp_file(cursor_config, uvx_path)

    print("\n[SUCCESS] Installation completed")
    print("\nUpdated:")
    print(f"  • {claude_config}")
    print(f"  • {cursor_config}")

    print("\nAdded MCP Server:")
    print(json.dumps({
        "command": uvx_path,
        "args": [PACKAGE_NAME]
    }, indent=2))

    print("\nRestart Claude Desktop and Cursor.")


if __name__ == "__main__":
    main()