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

    if not isinstance(config, dict):
        config = {}
        
    if not isinstance(config.get("mcpServers"), dict):
        config["mcpServers"] = {}

    config["mcpServers"][SERVER_NAME] = {
        "command": uvx_path,
        "args": [
            PACKAGE_NAME
        ]
    }

    save_json(path, config)

    print(f"[UPDATED] {path}")


def get_app_configs():
    """Return a dict of supported apps and their config file paths."""
    appdata = os.getenv("APPDATA", "")

    return {
        "Claude Desktop": (
            Path(appdata) / "Claude" / "claude_desktop_config.json"
        ),
        "Cursor": (
            Path.home() / ".cursor" / "mcp.json"
        ),
        "Windsurf": (
            Path(appdata) / "Windsurf" / "mcp.json"
        ),
        "VS Code": (
            Path(appdata) / "Code" / "User" / "mcp.json"
        ),
    }


def prompt_app_selection(apps):
    """Show a menu and return the list of selected app names."""
    app_names = list(apps.keys())

    print("\nSelect which app(s) to configure:\n")

    for i, name in enumerate(app_names, 1):
        print(f"  {i}. {name}")

    print(f"  {len(app_names) + 1}. All")
    print()

    while True:
        choice = input("Enter your choice (comma-separated for multiple, e.g. 1,3): ").strip()

        if not choice:
            continue

        parts = [p.strip() for p in choice.split(",")]
        selected = []

        try:
            for part in parts:
                num = int(part)

                if num == len(app_names) + 1:
                    return app_names

                if 1 <= num <= len(app_names):
                    name = app_names[num - 1]

                    if name not in selected:
                        selected.append(name)
                else:
                    print(f"[ERROR] Invalid option: {num}")
                    selected = []
                    break
        except ValueError:
            print("[ERROR] Please enter numbers only.")
            continue

        if selected:
            return selected


def main():
    print("=" * 60)
    print("  Echo MCP Installer")
    print("=" * 60)

    uvx_path = ensure_uvx()

    print(f"\n[OK] Using uvx: {uvx_path}")

    apps = get_app_configs()
    selected = prompt_app_selection(apps)

    print()

    updated = []

    for name in selected:
        path = apps[name]
        update_mcp_file(path, uvx_path)
        updated.append((name, path))

    print("\n" + "=" * 60)
    print("  [SUCCESS] Installation completed")
    print("=" * 60)

    print("\nUpdated:")

    for name, path in updated:
        print(f"  • {name}: {path}")

    print("\nAdded MCP Server:")
    print(json.dumps({
        "command": uvx_path,
        "args": [PACKAGE_NAME]
    }, indent=2))

    restart_names = ", ".join(name for name, _ in updated)
    print(f"\nRestart {restart_names} to apply changes.")


if __name__ == "__main__":
    main()
