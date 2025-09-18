#工具函数

def version() -> str:
    """返回库的版本号"""
    from . import __version__
    return f"my-library v{__version__}"
