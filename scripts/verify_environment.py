#!/usr/bin/env python3
"""
Environment Verification Script for Marcus AI Avatar
Checks all dependencies and reports status.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    required: bool = True


def check_python_version() -> CheckResult:
    """Verify Python 3.10+"""
    version = sys.version_info
    passed = version >= (3, 10)
    return CheckResult(
        name="Python Version",
        passed=passed,
        message=f"Python {version.major}.{version.minor}.{version.micro}"
        + ("" if passed else " (need 3.10+)"),
    )


def check_gpu() -> CheckResult:
    """Check for CUDA GPU availability"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            gpu_name = result.stdout.strip().split("\n")[0]
            return CheckResult(
                name="GPU (CUDA)",
                passed=True,
                message=gpu_name,
            )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check for Apple Silicon MPS
    try:
        import torch
        if torch.backends.mps.is_available():
            return CheckResult(
                name="GPU (MPS)",
                passed=True,
                message="Apple Silicon MPS available",
            )
    except ImportError:
        pass

    return CheckResult(
        name="GPU",
        passed=False,
        message="No GPU detected (CUDA or MPS)",
        required=False,
    )


def check_blender() -> CheckResult:
    """Check for Blender installation"""
    blender_path = shutil.which("blender")
    if blender_path:
        try:
            result = subprocess.run(
                ["blender", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version_line = result.stdout.split("\n")[0]
            return CheckResult(
                name="Blender",
                passed=True,
                message=version_line,
            )
        except (subprocess.TimeoutExpired, Exception):
            pass

    # Check common macOS locations
    mac_paths = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
    ]
    for path in mac_paths:
        if os.path.exists(path):
            return CheckResult(
                name="Blender",
                passed=True,
                message=f"Found at {path}",
            )

    return CheckResult(
        name="Blender",
        passed=False,
        message="Not found (install from blender.org)",
        required=False,
    )


def check_node() -> CheckResult:
    """Check for Node.js (needed for MCP)"""
    node_path = shutil.which("node")
    if node_path:
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = result.stdout.strip()
            major = int(version.lstrip("v").split(".")[0])
            passed = major >= 18
            return CheckResult(
                name="Node.js",
                passed=passed,
                message=f"{version}" + ("" if passed else " (need 18+)"),
            )
        except Exception:
            pass
    return CheckResult(
        name="Node.js",
        passed=False,
        message="Not found",
        required=False,
    )


def check_directory_structure() -> CheckResult:
    """Verify all required directories exist"""
    required_dirs = [
        "flame-server",
        "tts-chatterbox",
        "api-bridge",
        "unreal-project",
        "blender-projects",
        "reference-images",
        "docs",
        "tests",
        "scripts",
        "logs",
        ".context/memory",
    ]

    project_root = Path(__file__).parent.parent
    missing = []

    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing.append(dir_name)

    if missing:
        return CheckResult(
            name="Directory Structure",
            passed=False,
            message=f"Missing: {', '.join(missing)}",
        )

    return CheckResult(
        name="Directory Structure",
        passed=True,
        message=f"All {len(required_dirs)} directories present",
    )


def check_python_package(package: str, import_name: Optional[str] = None) -> CheckResult:
    """Check if a Python package is installed"""
    import_name = import_name or package
    spec = importlib.util.find_spec(import_name)
    if spec:
        return CheckResult(
            name=f"Package: {package}",
            passed=True,
            message="Installed",
        )
    return CheckResult(
        name=f"Package: {package}",
        passed=False,
        message="Not installed",
        required=False,
    )


def check_context_files() -> CheckResult:
    """Verify .context/ memory files exist"""
    project_root = Path(__file__).parent.parent
    context_files = [
        ".context/memory/procedural.md",
        ".context/memory/semantic.md",
        ".context/memory/episodic.md",
        ".context/decisions.md",
    ]

    missing = []
    for file_path in context_files:
        if not (project_root / file_path).exists():
            missing.append(file_path)

    if missing:
        return CheckResult(
            name="Context Memory",
            passed=False,
            message=f"Missing: {', '.join(missing)}",
        )

    return CheckResult(
        name="Context Memory",
        passed=True,
        message="All memory files present",
    )


def print_results(results: list[CheckResult]) -> bool:
    """Print results and return overall status"""
    print("\n" + "=" * 60)
    print("  MARCUS AI AVATAR - Environment Verification")
    print("=" * 60 + "\n")

    all_required_passed = True
    warnings = []

    for result in results:
        if result.passed:
            status = "\033[92m✓ PASS\033[0m"
        elif result.required:
            status = "\033[91m✗ FAIL\033[0m"
            all_required_passed = False
        else:
            status = "\033[93m○ WARN\033[0m"
            warnings.append(result)

        print(f"  {status}  {result.name}")
        print(f"         {result.message}\n")

    print("=" * 60)

    if all_required_passed:
        if warnings:
            print("\033[93m  ⚠ READY WITH WARNINGS\033[0m")
            print("  Optional components missing (see above)")
        else:
            print("\033[92m  ✓ ALL CHECKS PASSED\033[0m")
        print("=" * 60 + "\n")
        return True
    else:
        print("\033[91m  ✗ REQUIRED CHECKS FAILED\033[0m")
        print("  Fix the issues above before proceeding")
        print("=" * 60 + "\n")
        return False


def main():
    """Run all environment checks"""
    results = [
        check_python_version(),
        check_directory_structure(),
        check_context_files(),
        check_gpu(),
        check_blender(),
        check_node(),
        check_python_package("fastapi"),
        check_python_package("torch"),
        check_python_package("numpy"),
    ]

    success = print_results(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
