from pathlib import Path


_PACKAGE_DIR = Path(__file__).resolve().parent
_SOURCE_ROOT = _PACKAGE_DIR.parent


def resource_path(*parts: str) -> Path:
    """Locate a bundled resource in an installed package or source checkout."""
    package_path = _PACKAGE_DIR.joinpath(*parts)
    if package_path.exists():
        return package_path
    return _SOURCE_ROOT.joinpath(*parts)
