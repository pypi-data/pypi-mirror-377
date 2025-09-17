#!/usr/bin/env python3
"""
StegHub - Advanced Steganography Toolkit
Main CLI interface that provides access to all tools
"""

import sys
import subprocess
import argparse
import os
import json
import time
import urllib.request
import urllib.error
import re

TOOLS = {
    'gradus': {
        'description': 'Image steganography using histogram shifting',
        'details': 'Hide text messages in PNG images using advanced histogram manipulation'
    },
    'resono': {
        'description': 'Audio steganography using phase coding', 
        'details': 'Hide text messages in WAV audio files using phase manipulation'
    },
    'shadowbits': {
        'description': 'Image and Audio steganography using LSB',
        'details': 'Hide any file type in images or audio using Least Significant Bit technique'
    }
}

# system config for update
PYPI_NAME = 'steghub'
CACHE_DIR = os.path.expanduser("~/.steghub")
CACHE_FILE = os.path.join(CACHE_DIR, "update.json")
CACHE_TTL = int(os.environ.get('STEGHUB_CACHE_TTL', 7 * 24 * 3600)) # weekly checks for update once
HTTP_TIMEOUT = 6

def get_installed_version():
    """Get installed version from package metadata"""
    try:
        from importlib import metadata
        return metadata.version(PYPI_NAME)
    except Exception:
        # Fallback: try pip show
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', PYPI_NAME], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith('Version: '):
                        return line.split('Version: ')[1].strip()
        except Exception:
            pass
        
        return "unknown"
    
INSTALLED_VERSION = get_installed_version()
    
def parse_version(version_str):
    """Parse version string into comparable tuple of integers"""
    if not version_str or version_str == "unknown":
        return (0, 0, 0)
    
    # Remove any non-digit, non-dot characters (like 'v' prefix, alpha/beta suffixes)
    clean_version = re.sub(r'[^\d.]', '', version_str)
    
    try:
        parts = []
        for part in clean_version.split('.'):
            if part.isdigit():
                parts.append(int(part))
            else:
                break  # Stop at first non-numeric part
        
        while len(parts) < 3:
            parts.append(0)
            
        return tuple(parts)
    except Exception:
        return (0, 0, 0)
    
def compare_versions(version1, version2):
    """Compare two version strings. Returns 1 if version1 > version2, -1 if version1 < version2, 0 if equal"""
    v1_tuple = parse_version(version1)
    v2_tuple = parse_version(version2)
    
    if v1_tuple > v2_tuple:
        return 1
    elif v1_tuple < v2_tuple:
        return -1
    else:
        return 0

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def read_cache():
    try:
        with open(CACHE_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
    
def write_cache(data):
    ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding='utf-8') as f:
            json.dump(data,f, indent=2)
    except Exception as e:
        print(f"Warning: Could not write cache: {e}")

def get_pypi_latest():
    url = f'https://pypi.org/pypi/{PYPI_NAME}/json'
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as r:
            data = json.load(r)
            return data.get("info", {}).get("version")
    except (urllib.error.URLError, ValueError, json.JSONDecodeError) as e:
        print(f"Warning: Could not fetch latest version: {e}")
        return None
        
def check_update(force=False):
    cache = read_cache()
    last = int(cache.get("last_check" , 0))
    cached_latest = cache.get('latest_version')
    now = int(time.time())

    if not force and cached_latest and (now - last) < CACHE_TTL:
        has_update = compare_versions(cached_latest, INSTALLED_VERSION) > 0
        return has_update, cached_latest, True
    
    latest = get_pypi_latest()
    if latest:
        cache["last_check"] = now
        cache['latest_version'] = latest
        write_cache(cache)
        has_update = compare_versions(latest, INSTALLED_VERSION) > 0
        return has_update, latest, False
    else:
        if cached_latest:
            has_update = compare_versions(cached_latest, INSTALLED_VERSION) > 0
            return has_update, cached_latest, True
        return False, None, False
    
def print_update_notification(latest):
    print()
    print(f"New StegHub version available: {latest} (installed: {INSTALLED_VERSION})")
    print("   Run: steghub update")
    print("   Or: python -m pip install --upgrade steghub")
    print()

def manual_update(ask=True):
    if ask:
        try:
            resp = input("Update now via pip? [y/N]: ").strip().lower()
            if resp != "y":
                print("Aborted.")
                return False
        except KeyboardInterrupt:
            print("\nUpdate Cancelled.")
            return False
        
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", PYPI_NAME]
    try:
        print("Upgrading StegHub...")
        subprocess.run(cmd, check=True)
        print("✓ Upgrade finished! You may need to restart your terminal.")
        return True
    except subprocess.CalledProcessError:
        print("✗ Upgrade failed. Try running:")
        print("  python -m pip install --upgrade steghub")
        return False
    except KeyboardInterrupt:
        print("\nUpgrade interrupted")
        return False

def show_logo():
    """Display StegHub ASCII logo"""
    logo = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  ███████╗████████╗███████╗ ██████╗ ██╗  ██╗██╗   ██╗██████╗  ║
║  ██╔════╝╚══██╔══╝██╔════╝██╔════╝ ██║  ██║██║   ██║██╔══██╗ ║
║  ███████╗   ██║   █████╗  ██║  ███╗███████║██║   ██║██████╔╝ ║
║  ╚════██║   ██║   ██╔══╝  ██║   ██║██╔══██║██║   ██║██╔══██╗ ║
║  ███████║   ██║   ███████╗╚██████╔╝██║  ██║╚██████╔╝██████╔╝ ║
║  ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ║
║                                                       ║
║           ░▒▓█ STEGANOGRAPHY METAPACKAGE █▓▒░         ║
║                                                       ║
║    ┌─[HIDE]───────────────────────────────[SEEK]─┐    ║
║    │    🔐 Advanced Steganography Toolkit 🔐     │    ║
║    │     ∴ What you see is not what you get ∴    │    ║
║    └─────────────────────────────────────────────┘    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    print(logo)

def show_version():
    """Show version information"""
    print(f"StegHub version: {INSTALLED_VERSION}")
    
    # Check for updates (use cache)
    try:
        has_update, latest, used_cache = check_update(force=False)
        if latest and latest != INSTALLED_VERSION:
            cache_indicator = " (cached)" if used_cache else " (live)"
            if has_update:
                print(f"Latest version: {latest}{cache_indicator} - UPDATE AVAILABLE")
            else:
                print(f"Latest version: {latest}{cache_indicator}")
        elif latest:
            print("✓ You have the latest version")
    except Exception:
        print("Could not check for updates")

def main():
    if len(sys.argv) >= 2 and sys.argv[1] in TOOLS:
        tool = sys.argv[1]
        tool_args = sys.argv[2:]
        
        try:
            subprocess.run([tool] + tool_args, check=True)
            return
        except FileNotFoundError:
            print(f"Error: {tool} is not installed")
            print(f"Install with: pip install {tool}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            print(f"\n{tool} interrupted.")
            sys.exit(130)
    
    # StegHub commands
    parser = argparse.ArgumentParser(
        description='StegHub - Advanced Steganography Toolkit',
        epilog='Use: steghub <tool> --help for tool-specific help'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Tools subparsers (for help display only)
    for tool, info in TOOLS.items():
        subparsers.add_parser(tool, help=info['description'], add_help=False)
    
    # StegHub specific commands
    subparsers.add_parser('info', help='Show detailed information about each tool')
    subparsers.add_parser('list', help='List all available tools')
    subparsers.add_parser('version', help='Show version information')
    subparsers.add_parser('update', help='Update StegHub to latest version')
    subparsers.add_parser('check-update', help='Check for StegHub updates')
    
    args = parser.parse_args()
    
    if not args.command:
        show_main_help()
        return
    
    try:
        if args.command == 'info':
            show_info()
        elif args.command == 'list':
            list_tools()
        elif args.command == 'version':
            show_version()
        elif args.command =='update':
            manual_update(ask=True)
        elif args.command == 'check-update':
            check_update_command()
        else:
            show_main_help()
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(130)

def show_main_help():
    """Show main StegHub help"""
    show_logo()
    print("StegHub - Advanced Steganography Toolkit")
    print("=" * 45)
    print()
    print("Available tools:")
    
    for tool, info in TOOLS.items():
        print(f"  {tool:<12} - {info['description']}")
    
    print()
    print("StegHub commands:")
    print("  info         - Show detailed information about each tool")
    print("  list         - List all available tools")
    print("  version      - Show version information")
    print("  update       - Update StegHub to latest version")
    print("  check-update - Check for StegHub updates")
    print()
    print("Usage examples:")
    print("  gradus --help                       # Show gradus help")
    print("  gradus embed --in 'secret' ...      # Use gradus directly")
    print("  resono embed --in 'secret' ...      # Use resono directly")
    print("  steghub info                        # Show tool details")

def show_info():
    """Show detailed information about each tool"""
    print("StegHub - Tool Information")
    print("=" * 30)
    print()
    
    for tool, info in TOOLS.items():
        # Check if tool is installed
        try:
            subprocess.run([tool, '--help'], capture_output=True, timeout=5)
            status = "✓ Installed"
        except FileNotFoundError:
            status = "✗ Not installed (pip install {})".format(tool)
        except:
            status = "? Unknown status"
        
        print(f"{tool.upper()}")
        print(f"  Status: {status}")
        print(f"  Purpose: {info['details']}")
        print(f"  Usage: steghub {tool} --help")
        print()

def list_tools():
    """Simple list of available tools"""
    print("Available StegHub tools:")
    for tool in TOOLS.keys():
        print(f"  - {tool}")

def check_update_command():
    print("Checking for StegHub updates...")
    try:
        has_update, latest, used_cache = check_update(force=True)

        cache_info = " (from cache)" if used_cache else " (live check)"
        
        if latest:
            if has_update:
                print(f"✓ Update available: {latest} (current: {INSTALLED_VERSION})")
                print("   Run 'steghub update' to upgrade")
            else:
                print(f"✓ You have the latest version: {INSTALLED_VERSION}{cache_info}")
        else:
            print("✗ Could not check for updates (network error)")
    except Exception as e:
        print(f"✗ Update check failed: {e}")

if __name__ == "__main__":
    main()