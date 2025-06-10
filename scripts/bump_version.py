#!/usr/bin/env python3
"""
Version bump script for mcp-tts package.
Automatically updates version in pyproject.toml and creates a git commit.

Usage:
    python scripts/bump_version.py patch    # 0.2.0 → 0.2.1
    python scripts/bump_version.py minor    # 0.2.0 → 0.3.0
    python scripts/bump_version.py major    # 0.2.0 → 1.0.0
    python scripts/bump_version.py 0.5.0    # Custom version
"""

import re
import sys
import subprocess
from pathlib import Path


def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ Error: pyproject.toml not found")
        print("   Make sure you're running this from the project root")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'^version = ["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        print("❌ Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def parse_version(version_str):
    """Parse version string into major, minor, patch components."""
    parts = version_str.split(".")
    if len(parts) < 3:
        # Handle cases like "0.2" by padding with zeros
        parts.extend(["0"] * (3 - len(parts)))

    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return major, minor, patch
    except ValueError:
        print(f"❌ Error: Invalid version format: {version_str}")
        print("   Expected format: major.minor.patch (e.g., 1.2.3)")
        sys.exit(1)


def bump_version(current_version, bump_type):
    """Bump version based on type."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        # Custom version - validate format
        try:
            new_major, new_minor, new_patch = parse_version(bump_type)
            return f"{new_major}.{new_minor}.{new_patch}"
        except (ValueError, IndexError):
            print(f"❌ Error: Invalid version or bump type: {bump_type}")
            print("   Valid bump types: major, minor, patch")
            print("   Or provide a custom version like: 1.2.3")
            sys.exit(1)

    return f"{major}.{minor}.{patch}"


def update_pyproject_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Replace version line
    updated_content = re.sub(
        r'^version = ["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )

    if content == updated_content:
        print("❌ Error: Failed to update version in pyproject.toml")
        sys.exit(1)

    pyproject_path.write_text(updated_content)
    print(f"✅ Updated pyproject.toml version to {new_version}")


def git_commit_version(old_version, new_version):
    """Create git commit for version bump."""
    try:
        # Check if git repo
        subprocess.run(["git", "status"], check=True, capture_output=True)

        # Add pyproject.toml
        subprocess.run(["git", "add", "pyproject.toml"], check=True)

        # Commit with version bump message
        commit_msg = f"🚀 Bump version from {old_version} to {new_version}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        print(f"✅ Created git commit: {commit_msg}")
        print()
        print("📋 Next steps:")
        print("   1. Review the changes: git show")
        print("   2. Push to trigger CI/CD: git push origin main")
        print(
            "   3. Watch the action: https://github.com/EnviralDesign/mcp-tts/actions"
        )
        print(f"   4. Check PyPI: https://pypi.org/project/mcp-tts/{new_version}/")

    except subprocess.CalledProcessError:
        print("⚠️  Git commit failed or not in a git repository")
        print("   You can manually commit the changes:")
        print("   git add pyproject.toml")
        print(f"   git commit -m '🚀 Bump version from {old_version} to {new_version}'")
        print("   git push origin main")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <bump_type|version>")
        print()
        print("Bump types:")
        print("  patch   - Bump patch version (0.2.0 → 0.2.1)")
        print("  minor   - Bump minor version (0.2.0 → 0.3.0)")
        print("  major   - Bump major version (0.2.0 → 1.0.0)")
        print()
        print("Custom version:")
        print("  0.5.0   - Set specific version")
        sys.exit(1)

    bump_type = sys.argv[1]

    print("🔍 Current version check...")
    current_version = get_current_version()
    print(f"   Current version: {current_version}")

    print("⬆️  Calculating new version...")
    new_version = bump_version(current_version, bump_type)
    print(f"   New version: {new_version}")

    if current_version == new_version:
        print("❌ Error: New version is the same as current version")
        sys.exit(1)

    # Confirm with user
    print()
    response = input(f"Update version from {current_version} to {new_version}? [y/N]: ")
    if response.lower() not in ["y", "yes"]:
        print("❌ Cancelled")
        sys.exit(0)

    print()
    print("📝 Updating pyproject.toml...")
    update_pyproject_version(new_version)

    print("📦 Creating git commit...")
    git_commit_version(current_version, new_version)

    print()
    print("🎉 Version bump complete!")


if __name__ == "__main__":
    main()
