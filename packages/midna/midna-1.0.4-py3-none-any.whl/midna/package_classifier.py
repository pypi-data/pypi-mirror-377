"""Package classification for Midna"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Set, Tuple

try:
    from importlib.metadata import distribution
except ImportError:
    from importlib_metadata import distribution  # type: ignore

# Standard library modules in Python 3
STDLIB_MODULES = {
    name.split(".")[0]
    for name in list(sys.builtin_module_names) + list(sys.modules)
    if name.split(".")[0] not in {"test", "pip", "setuptools"}
}

# Common test and internal modules to ignore
IGNORED_MODULES = {
    "test",
    "tests",
    "testing",
    "examples",
    "setup",
    "__main__",
    "__init__",
    "conftest",
}


def is_stdlib_package(package_name: str) -> bool:
    """Check if a package is part of Python's standard library"""
    # Check if it's in our known stdlib modules
    if package_name in STDLIB_MODULES:
        return True

    # Check if it's a built-in module
    if package_name in sys.builtin_module_names:
        return True

    # Check if it's in standard library paths
    try:
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            return (
                "stdlib" in str(spec.origin).lower()
                or "python" in str(spec.origin).lower()
            )
    except (ImportError, AttributeError):
        pass

    return False


def is_project_package(package_name: str, project_root: str) -> bool:
    """Check if a package is part of the current project"""
    if package_name in IGNORED_MODULES:
        return True

    project_path = Path(project_root).resolve()

    # Look for the package in different possible locations
    possible_locations = [
        project_path / package_name / "__init__.py",
        project_path / f"{package_name}.py",
        project_path.parent / package_name / "__init__.py",
        project_path.parent / f"{package_name}.py",
    ]

    return any(loc.exists() for loc in possible_locations)


def get_package_version(package_name: str) -> str:
    """Get the installed version of a package"""
    try:
        # Try getting version from importlib.metadata first
        return str(distribution(package_name).version)
    except ImportError:
        try:
            # Try importing the package and checking __version__
            module = importlib.import_module(package_name)
            if hasattr(module, "__version__"):
                return str(module.__version__)
            elif hasattr(module, "VERSION"):
                return str(module.VERSION)
        except (ImportError, AttributeError):
            pass
    return ""


def classify_packages(
    packages: Set[str], project_root: str
) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    """
    Classify packages into stdlib, project, and third-party packages
    Returns: (stdlib_packages, project_packages, third_party_packages)
    third_party_packages is a list of (name, version) tuples
    """
    stdlib_packages: List[str] = []
    project_packages: List[str] = []
    third_party_packages: List[Tuple[str, str]] = []

    for package in packages:
        # Skip empty or invalid package names
        if not package or package.startswith("."):
            continue

        # Normalize the package name
        base_package = package.split(".")[0].lower()

        if is_stdlib_package(base_package):
            stdlib_packages.append(package)
        elif is_project_package(base_package, project_root):
            project_packages.append(package)
        else:
            version = get_package_version(base_package)
            if version:  # Only include if it's an installed package
                third_party_packages.append((base_package, version))

    return (
        sorted(set(stdlib_packages)),  # Remove duplicates
        sorted(set(project_packages)),
        sorted(set((p, v) for p, v in third_party_packages)),
    )
