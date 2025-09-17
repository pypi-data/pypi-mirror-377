"""Python bindings for libwebm"""

from importlib.metadata import version

from _webm import WebMReader, WebMWriter, get_libwebm_version

__version__ = version("libwebm-py")
native_version = get_libwebm_version()

__all__ = ["WebMReader", "WebMWriter", "__version__", "native_version"]