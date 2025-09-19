# Runtime hook for LZ4 modules
# This ensures LZ4 is properly loaded when PyInstaller runs

import sys
import importlib


def _ensure_lz4_available():
    """Ensure LZ4 modules are available at runtime"""
    try:
        # Try to import lz4.frame
        import lz4.frame
        # Verify the specific functions exist
        if hasattr(lz4.frame, 'compress') and hasattr(lz4.frame, 'decompress'):
            return True
    except ImportError:
        pass

    # If LZ4 is not available, create dummy modules to prevent crashes
    try:
        # Create a dummy lz4.frame module
        class DummyLZ4Frame:
            @staticmethod
            def compress(data):
                # Fallback to zlib if LZ4 not available
                import zlib
                return zlib.compress(data, level=9)

            @staticmethod
            def decompress(data):
                # Fallback to zlib if LZ4 not available
                import zlib
                return zlib.decompress(data)

        # Create the module structure
        import types
        lz4_module = types.ModuleType('lz4')
        lz4_frame_module = types.ModuleType('lz4.frame')
        lz4_frame_module.compress = DummyLZ4Frame.compress
        lz4_frame_module.decompress = DummyLZ4Frame.decompress

        # Add to sys.modules
        sys.modules['lz4'] = lz4_module
        sys.modules['lz4.frame'] = lz4_frame_module

        return True
    except Exception:
        return False


# Run the check when this module is imported
_ensure_lz4_available()
