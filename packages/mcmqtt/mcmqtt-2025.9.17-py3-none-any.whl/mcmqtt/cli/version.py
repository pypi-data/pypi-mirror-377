"""Version management for mcmqtt."""


def get_version() -> str:
    """Get package version."""
    try:
        from importlib.metadata import version
        return version("mcmqtt")
    except Exception:
        return "0.1.0"