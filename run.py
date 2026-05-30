
"""
Single entry point: starts the backend and opens the browser.
Run from the project root:  python run.py
"""
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT      = Path(__file__).parent
BACKEND   = ROOT / "backend"
_scripts  = "Scripts" if sys.platform == "win32" else "bin"
_exe      = ".exe" if sys.platform == "win32" else ""
VENV_PY   = ROOT / ".venv" / _scripts / f"python{_exe}"
UVICORN   = ROOT / ".venv" / _scripts / f"uvicorn{_exe}"

if sys.platform == "win32":
    import winreg
    def _reg_path(hive, subkey):
        try:
            with winreg.OpenKey(hive, subkey) as k:
                return winreg.QueryValueEx(k, "PATH")[0]
        except OSError:
            return ""
    _sys_path = _reg_path(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
    _usr_path = _reg_path(winreg.HKEY_CURRENT_USER, r"Environment")
    os.environ["PATH"] = _sys_path + ";" + _usr_path

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def check_setup():
    if not VENV_PY.exists():
        print("[ERROR] Virtual environment not found.")
        print("        Run setup.bat first to install dependencies.")
        sys.exit(1)

def main():
    check_setup()

    print("Starting Battleship backend...")
    backend = subprocess.Popen(
        [str(UVICORN), "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND,
    )

    print("Starting Battleship frontend...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=ROOT / "frontend",
        shell=True,
    )

    # Give servers a moment to start, then open browser
    time.sleep(2)
    print(f"Opening {FRONTEND_URL} ...")
    webbrowser.open(FRONTEND_URL)

    print()
    print("  Backend  →  http://localhost:8000")
    print("  Frontend →  http://localhost:5173")
    print()
    print("  Press Ctrl+C to stop both servers.")
    print()

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Done.")

if __name__ == "__main__":
    main()
