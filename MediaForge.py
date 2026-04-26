#!/usr/bin/env python3
"""
MediaForge - Professional Open Source Media Converter
A comprehensive video, audio, and image converter with editing capabilities.
"""

import sys
import os
import subprocess
import platform
import urllib.request
import zipfile
import shutil
import tempfile
from pathlib import Path
from PyQt6.QtGui import QIcon


# codex-branding:start
def _branding_icon_path() -> Path:
    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "icon.png")
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "icon.png")
    current = Path(__file__).resolve()
    candidates.extend([current.parent / "icon.png", current.parent.parent / "icon.png", current.parent.parent.parent / "icon.png"])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path("icon.png")
# codex-branding:end


APP_NAME = "MediaForge"
APP_VERSION = "1.0.0"

def get_app_data_dir():
    """Get application data directory"""
    if platform.system() == "Windows":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(base) / APP_NAME
    else:
        return Path.home() / f".{APP_NAME.lower()}"

def check_python_packages():
    """Check and install required Python packages"""
    required_packages = [
        ("PyQt6", "PyQt6"),
        ("PyQt6.QtMultimedia", "PyQt6-Multimedia"),
        ("cv2", "opencv-python"),
        ("PIL", "Pillow"),
        ("numpy", "numpy"),
        ("mutagen", "mutagen"),
        ("moviepy", "moviepy"),
        ("av", "av"),
    ]
    
    missing = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name.split('.')[0])
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"Installing required packages: {', '.join(missing)}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--quiet", "--disable-pip-version-check"
        ] + missing)
        print("Packages installed successfully!")

def get_ffmpeg_url():
    """Get FFmpeg download URL based on platform"""
    system = platform.system()
    machine = platform.machine().lower()
    
    if system == "Windows":
        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == "Darwin":
        return "https://evermeet.cx/ffmpeg/getrelease/zip"
    else:  # Linux
        if "arm" in machine or "aarch64" in machine:
            return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
        return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

def download_ffmpeg(target_dir):
    """Download and extract FFmpeg"""
    print("Downloading FFmpeg (this may take a few minutes)...")
    url = get_ffmpeg_url()
    system = platform.system()
    
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        if system == "Linux":
            archive_path = tmp_path / "ffmpeg.tar.xz"
        else:
            archive_path = tmp_path / "ffmpeg.zip"
        
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 // total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\rDownloading: {mb_downloaded:.1f}/{mb_total:.1f} MB ({percent}%)", end="", flush=True)
        
        try:
            urllib.request.urlretrieve(url, archive_path, report_progress)
            print("\nExtracting FFmpeg...")
        except Exception as e:
            print(f"\nFailed to download FFmpeg: {e}")
            return False
        
        # Extract based on archive type
        try:
            if system == "Windows":
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(tmp_path)
                # Find ffmpeg.exe in extracted folder
                for root, dirs, files in os.walk(tmp_path):
                    if "ffmpeg.exe" in files:
                        for f in ["ffmpeg.exe", "ffprobe.exe"]:
                            src = Path(root) / f
                            if src.exists():
                                dest = target_dir / f
                                shutil.copy2(src, dest)
                                print(f"  Installed: {dest}")
                        break
            elif system == "Linux":
                import tarfile
                with tarfile.open(archive_path, "r:xz") as tf:
                    tf.extractall(tmp_path)
                for root, dirs, files in os.walk(tmp_path):
                    if "ffmpeg" in files:
                        for f in ["ffmpeg", "ffprobe"]:
                            src = Path(root) / f
                            if src.exists():
                                dest = target_dir / f
                                shutil.copy2(src, dest)
                                os.chmod(dest, 0o755)
                                print(f"  Installed: {dest}")
                        break
            else:  # macOS
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(tmp_path)
                for f in tmp_path.glob("**/ffmpeg*"):
                    if f.is_file() and f.name in ["ffmpeg", "ffprobe"]:
                        dest = target_dir / f.name
                        shutil.copy2(f, dest)
                        os.chmod(dest, 0o755)
                        print(f"  Installed: {dest}")
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False
    
    # Verify installation
    ffmpeg_exe = "ffmpeg.exe" if system == "Windows" else "ffmpeg"
    ffprobe_exe = "ffprobe.exe" if system == "Windows" else "ffprobe"
    
    ffmpeg_path = target_dir / ffmpeg_exe
    ffprobe_path = target_dir / ffprobe_exe
    
    if ffmpeg_path.exists() and ffprobe_path.exists():
        print(f"FFmpeg installed successfully to: {target_dir}")
        return True
    else:
        print("FFmpeg installation incomplete.")
        return False

def find_executable(name):
    """Find an executable in PATH or common locations"""
    system = platform.system()
    
    # Add .exe extension on Windows
    if system == "Windows" and not name.endswith(".exe"):
        name_with_ext = name + ".exe"
    else:
        name_with_ext = name
    
    # Check PATH using 'where' (Windows) or 'which' (Unix)
    try:
        if system == "Windows":
            result = subprocess.run(
                ["where", name_with_ext],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout.strip():
                # 'where' returns all matches, take the first one
                return result.stdout.strip().split('\n')[0].strip()
        else:
            result = subprocess.run(
                ["which", name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
    except Exception:
        pass
    
    # Check app data directory
    app_dir = get_app_data_dir() / "ffmpeg"
    local_path = app_dir / name_with_ext
    if local_path.exists():
        return str(local_path)
    
    # Check common Windows locations
    if system == "Windows":
        common_paths = [
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "FFmpeg" / "bin" / name_with_ext,
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "FFmpeg" / "bin" / name_with_ext,
            Path(os.environ.get("LOCALAPPDATA", "")) / "FFmpeg" / "bin" / name_with_ext,
            Path.home() / "ffmpeg" / "bin" / name_with_ext,
            Path("C:\\ffmpeg\\bin") / name_with_ext,
        ]
        for p in common_paths:
            if p.exists():
                return str(p)
    
    return None

def verify_ffmpeg(ffmpeg_path, ffprobe_path):
    """Verify FFmpeg and FFprobe work correctly"""
    system = platform.system()
    kwargs = {}
    if system == "Windows":
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    
    try:
        # Test ffmpeg
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            **kwargs
        )
        if result.returncode != 0:
            return False, "FFmpeg test failed"
        
        # Test ffprobe
        result = subprocess.run(
            [ffprobe_path, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            **kwargs
        )
        if result.returncode != 0:
            return False, "FFprobe test failed"
        
        return True, "OK"
    except FileNotFoundError as e:
        return False, f"File not found: {e}"
    except Exception as e:
        return False, str(e)

def ensure_ffmpeg():
    """Ensure FFmpeg and FFprobe are available, returns (ffmpeg_path, ffprobe_path) or (None, None)"""
    
    # First, try to find existing installations
    ffmpeg_path = find_executable("ffmpeg")
    ffprobe_path = find_executable("ffprobe")
    
    if ffmpeg_path and ffprobe_path:
        print(f"Found FFmpeg: {ffmpeg_path}")
        print(f"Found FFprobe: {ffprobe_path}")
        
        # Verify they work
        ok, msg = verify_ffmpeg(ffmpeg_path, ffprobe_path)
        if ok:
            return ffmpeg_path, ffprobe_path
        else:
            print(f"Warning: Found FFmpeg but verification failed: {msg}")
    
    # Need to download FFmpeg
    print("FFmpeg not found or not working. Downloading...")
    app_dir = get_app_data_dir() / "ffmpeg"
    
    if download_ffmpeg(app_dir):
        system = platform.system()
        ffmpeg_exe = "ffmpeg.exe" if system == "Windows" else "ffmpeg"
        ffprobe_exe = "ffprobe.exe" if system == "Windows" else "ffprobe"
        
        ffmpeg_path = str(app_dir / ffmpeg_exe)
        ffprobe_path = str(app_dir / ffprobe_exe)
        
        # Verify downloaded files work
        ok, msg = verify_ffmpeg(ffmpeg_path, ffprobe_path)
        if ok:
            return ffmpeg_path, ffprobe_path
        else:
            print(f"Error: Downloaded FFmpeg doesn't work: {msg}")
    
    return None, None

def main():
    """Main entry point"""
    print("""
================================================================================
  __  __          _ _       _____                    
 |  \\/  |        | (_)     |  ___|                   
 | \\  / | ___  __| |_  __ _| |_ ___  _ __ __ _  ___ 
 | |\\/| |/ _ \\/ _` | |/ _` |  _/ _ \\| '__/ _` |/ _ \\
 | |  | |  __/ (_| | | (_| | || (_) | | | (_| |  __/
 |_|  |_|\\___|\\__,_|_|\\__,_\\_| \\___/|_|  \\__, |\\___|
                                          __/ |     
                                         |___/      
  Professional Open Source Media Converter v1.0.0
================================================================================
""")
    
    # Check Python packages
    print("[1/3] Checking Python dependencies...")
    check_python_packages()
    print("      Dependencies OK!")
    
    # Check FFmpeg
    print("\n[2/3] Checking FFmpeg...")
    ffmpeg_path, ffprobe_path = ensure_ffmpeg()
    
    if not ffmpeg_path or not ffprobe_path:
        print("\n" + "=" * 60)
        print("ERROR: FFmpeg is required but could not be installed.")
        print("=" * 60)
        print("\nPlease install FFmpeg manually:")
        print("  Windows: winget install FFmpeg")
        print("           or download from https://ffmpeg.org/download.html")
        print("  macOS:   brew install ffmpeg")
        print("  Linux:   sudo apt install ffmpeg")
        print("\nAfter installing, restart MediaForge.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print(f"      FFmpeg OK!")
    
    # Start GUI
    print("\n[3/3] Starting MediaForge...")
    print("=" * 60)
    
    # Import and run the main application
    from mediaforge_app import MediaForgeApp
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    branding_icon = QIcon(str(_branding_icon_path()))
    
    app.setWindowIcon(branding_icon)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    
    window = MediaForgeApp(ffmpeg_path, ffprobe_path)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
