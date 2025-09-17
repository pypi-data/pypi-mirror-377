import os
from packaging.version import Version
import get_compiler

AMULET_COMPILER_TARGET_REQUIREMENT = "==2.0"

PYBIND11_REQUIREMENT = "==3.0.0"
AMULET_PYBIND11_EXTENSIONS_REQUIREMENT = "~=1.2.0.0a0"
AMULET_IO_REQUIREMENT = "~=1.0"
AMULET_ZLIB_REQUIREMENT = "~=1.0.8.0a0"
NUMPY_REQUIREMENT = "~=2.0"

if os.environ.get("AMULET_PYBIND11_EXTENSIONS_REQUIREMENT", None):
    AMULET_PYBIND11_EXTENSIONS_REQUIREMENT = f"{AMULET_PYBIND11_EXTENSIONS_REQUIREMENT},{os.environ['AMULET_PYBIND11_EXTENSIONS_REQUIREMENT']}"

if os.environ.get("AMULET_IO_REQUIREMENT", None):
    AMULET_IO_REQUIREMENT = (
        f"{AMULET_IO_REQUIREMENT},{os.environ['AMULET_IO_REQUIREMENT']}"
    )

if os.environ.get("AMULET_ZLIB_REQUIREMENT", None):
    AMULET_ZLIB_REQUIREMENT = (
        f"{AMULET_ZLIB_REQUIREMENT},{os.environ['AMULET_ZLIB_REQUIREMENT']}"
    )


def get_specifier_set(version_str: str) -> str:
    """
    version_str: The PEP 440 version number of the library.
    """
    version = Version(version_str)
    if version.epoch != 0 or version.is_devrelease or version.is_postrelease:
        raise RuntimeError(f"Unsupported version format. {version_str}")

    return f"~={version.major}.{version.minor}.{version.micro}.0{''.join(map(str, version.pre or ()))}"


AMULET_COMPILER_VERSION_REQUIREMENT = get_compiler.main()


try:
    import amulet.pybind11_extensions
except ImportError:
    pass
else:
    AMULET_PYBIND11_EXTENSIONS_REQUIREMENT = get_specifier_set(
        amulet.pybind11_extensions.__version__
    )

try:
    import amulet.io
except ImportError:
    pass
else:
    AMULET_IO_REQUIREMENT = get_specifier_set(amulet.io.__version__)

try:
    import amulet.zlib
except ImportError:
    pass
else:
    AMULET_ZLIB_REQUIREMENT = get_specifier_set(amulet.zlib.__version__)


def get_build_dependencies() -> list:
    return [
        f"amulet-compiler-version{AMULET_COMPILER_VERSION_REQUIREMENT}",
        f"pybind11{PYBIND11_REQUIREMENT}",
        f"amulet-pybind11-extensions{AMULET_PYBIND11_EXTENSIONS_REQUIREMENT}",
        f"amulet-io{AMULET_IO_REQUIREMENT}",
        f"amulet-zlib{AMULET_ZLIB_REQUIREMENT}",
    ] * (not os.environ.get("AMULET_SKIP_COMPILE", None))


def get_runtime_dependencies() -> list[str]:
    return [
        f"amulet-compiler-target{AMULET_COMPILER_TARGET_REQUIREMENT}",
        f"amulet-compiler-version{AMULET_COMPILER_VERSION_REQUIREMENT}",
        f"pybind11{PYBIND11_REQUIREMENT}",
        f"amulet-pybind11-extensions{AMULET_PYBIND11_EXTENSIONS_REQUIREMENT}",
        f"amulet-io{AMULET_IO_REQUIREMENT}",
        f"amulet-zlib{AMULET_ZLIB_REQUIREMENT}",
        f"numpy{NUMPY_REQUIREMENT}",
    ]
