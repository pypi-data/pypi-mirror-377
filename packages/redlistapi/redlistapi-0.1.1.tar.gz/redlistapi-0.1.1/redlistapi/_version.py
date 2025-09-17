
try:
    from importlib.metadata import version
    __version__ = version("redlistapi")
except Exception:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Python <3.11

    import pathlib

    pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
        __version__ = data["project"]["version"]
