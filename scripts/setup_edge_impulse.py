#!/usr/bin/env python3
"""
Setup script to configure Edge Impulse credentials and verify connection.

Usage:
    python scripts/setup_edge_impulse.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def check_cli_installed() -> bool:
    """Check if Edge Impulse CLI is installed."""
    try:
        result = subprocess.run(
            ["edge-impulse-cli", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_cli() -> None:
    """Install Edge Impulse CLI."""
    print("[setup] Installing Edge Impulse CLI...")
    try:
        subprocess.run(
            ["npm", "install", "-g", "edge-impulse-cli"],
            check=True
        )
        print("[setup] ✅ Edge Impulse CLI installed")
    except subprocess.CalledProcessError:
        print("[setup] ❌ Failed to install CLI. Please install manually:")
        print("       npm install -g edge-impulse-cli")
        sys.exit(1)


def check_env_file() -> bool:
    """Check if .env file exists."""
    env_path = Path(".env")
    return env_path.exists()


def create_env_file() -> None:
    """Create .env file template."""
    env_path = Path(".env")
    if env_path.exists():
        print("[setup] .env file already exists")
        return
    
    print("[setup] Creating .env file template...")
    template = """# Edge Impulse Credentials
# Get your API key from: https://studio.edgeimpulse.com/ → Profile → API Keys
# Get your Project ID from: Edge Impulse Studio project URL or settings

EI_API_KEY=your_api_key_here
EI_PROJECT_ID=your_project_id_here
"""
    env_path.write_text(template, encoding="utf-8")
    print(f"[setup] ✅ Created {env_path}")
    print("[setup] ⚠️  Please edit .env and add your credentials")


def verify_credentials() -> bool:
    """Verify Edge Impulse credentials are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("EI_API_KEY")
    project_id = os.getenv("EI_PROJECT_ID")
    
    if not api_key or api_key == "your_api_key_here":
        print("[setup] ❌ EI_API_KEY not set in .env")
        return False
    
    if not project_id or project_id == "your_project_id_here":
        print("[setup] ❌ EI_PROJECT_ID not set in .env")
        return False
    
    print("[setup] ✅ Credentials found in .env")
    return True


def test_connection() -> bool:
    """Test Edge Impulse connection."""
    print("[setup] Testing Edge Impulse connection...")
    try:
        result = subprocess.run(
            ["edge-impulse-cli", "whoami"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("[setup] ✅ Connected to Edge Impulse")
            print(f"[setup] {result.stdout.strip()}")
            return True
        else:
            print("[setup] ❌ Connection failed")
            print(f"[setup] {result.stderr}")
            return False
    except FileNotFoundError:
        print("[setup] ❌ Edge Impulse CLI not found")
        return False
    except subprocess.TimeoutExpired:
        print("[setup] ❌ Connection timeout")
        return False


def main() -> None:
    print("=" * 60)
    print("EmberSense Edge Impulse Setup")
    print("=" * 60)
    print()
    
    # Check CLI
    if not check_cli_installed():
        print("[setup] Edge Impulse CLI not found")
        response = input("[setup] Install now? (y/n): ")
        if response.lower() == 'y':
            install_cli()
        else:
            print("[setup] Please install manually: npm install -g edge-impulse-cli")
            sys.exit(1)
    else:
        print("[setup] ✅ Edge Impulse CLI installed")
    
    # Check .env file
    if not check_env_file():
        create_env_file()
        print()
        print("[setup] Next steps:")
        print("  1. Edit .env file with your credentials")
        print("  2. Get API key from: https://studio.edgeimpulse.com/ → Profile → API Keys")
        print("  3. Get Project ID from your Edge Impulse project")
        print("  4. Run this script again to verify")
        sys.exit(0)
    
    # Verify credentials
    if not verify_credentials():
        print()
        print("[setup] Please edit .env file with your credentials")
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print()
        print("[setup] Please login to Edge Impulse CLI:")
        print("  edge-impulse-cli login")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Setup complete! You're ready to use Edge Impulse.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Upload data to Edge Impulse Studio")
    print("  2. Configure DSP pipeline")
    print("  3. Train models")
    print("  4. Run optimization scripts")
    print()
    print("See docs/EDGE_IMPULSE_SETUP.md for detailed instructions")


if __name__ == "__main__":
    main()

