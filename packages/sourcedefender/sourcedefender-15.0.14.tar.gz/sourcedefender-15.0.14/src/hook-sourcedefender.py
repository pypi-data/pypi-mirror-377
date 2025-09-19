from PyInstaller.utils.hooks import get_hook_config

# SOURCEdefender PyInstaller Hook
# Declares all dependencies used by SOURCEdefender's compiled .so files
# that PyInstaller cannot automatically detect

hiddenimports = [
    # Core dependencies from requirements.txt
    "msgpack",
    "msgpack.exceptions",
    "lz4",
    "lz4.frame",
    "lz4.frame.compress",
    "lz4.frame.decompress",
    "feedparser",
    "tgcrypto",
    "boltons",
    "boltons.timeutils",
    "environs",
    "psutil",
    "ntplib",
    "requests",
    "requests.adapters",
    "requests.packages.urllib3.util.retry",
    "packaging",
    "packaging.version",
    "setuptools",
    "setuptools.command.easy_install",
    "wheel",
    "docopt",
    # SOURCEdefender internal modules
    "sourcedefender.encrypt",
    "sourcedefender.loader",
    "sourcedefender.register",
    "sourcedefender.script",
    "sourcedefender.tools",
    # Standard library modules used by SOURCEdefender
    "os",
    "sys",
    "datetime",
    "threading",
    "subprocess",
    "re",
    "gc",
    "marshal",
    "zlib",
    "hashlib",
    "inspect",
    "types",
    "importlib",
    "importlib.abc",
    "importlib.util",
    "ast",
    "textwrap",
    "logging",
    "pathlib",
    "tempfile",
    "glob",
    "shutil",
    "socket",
    # Crypto and encoding
    "base64",
    "uuid",
    # Network utilities
    "urllib3",
    "urllib3.exceptions",
    "urllib.request",
    "urllib.parse",
    "certifi",
    # Environment and configuration
    "dotenv",
    "marshmallow",
    # Additional security-critical modules
    "platform",
    "time",
    "traceback",
    "warnings",
    "weakref",
    "copy",
    "collections",
    "itertools",
    "functools",
    # Anti-debugging protection modules
    "ctypes",
    "struct",
    "signal",
    "atexit",
    # Windows-specific modules
    "winreg",
    "_winreg",
    # PyInstaller integration
    "PyInstaller",
    "PyInstaller.__main__",
]

# Data files that may be needed
datas = []

# Binary dependencies (if any)
binaries = []

# Runtime hooks for critical modules
runtime_hooks = [
    "rthook-lz4.py"
]
