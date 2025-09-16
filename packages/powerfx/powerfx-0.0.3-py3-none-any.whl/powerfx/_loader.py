import sys
from importlib import resources
from pathlib import Path

_loaded_key = "_powerfx_loaded"


def load() -> None:
    """
    Ensure Microsoft.PowerFx assemblies are loadable via pythonnet (CoreCLR).

    Precedence for dll_dir:
    - explicit arg
    - env var POWERFX_DLL_DIR
    - <pkg>/runtime (optional fallback)
    """
    if getattr(sys.modules[__name__], _loaded_key, False):
        return

    base = _bundled_dir()
    if not base.is_dir():
        raise RuntimeError(f"Power Fx DLL directory '{base}' does not exist.")

    # Select CoreCLR BEFORE any clr import
    import pythonnet  # type: ignore

    pythonnet.load("coreclr")

    import clr  # type: ignore

    # Make sure PowerFx DLL folder is in probing paths
    if base not in sys.path:
        sys.path.append(str(base))

    # Load ONLY the PowerFx assemblies you ship; let CoreCLR resolve System.* deps.
    for name in ("Microsoft.PowerFx.Core", "Microsoft.PowerFx.Interpreter"):
        try:
            clr.AddReference(name)
        except Exception as ex:
            # Fallback to explicit path if name load fails
            print(f"Failed to load '{name}' by name, trying explicit path. Exception: {ex}")
            raise

    setattr(sys.modules[__name__], _loaded_key, True)


def _bundled_dir() -> Path:
    """
    Return the path to the bundled PowerFx assemblies inside this package.
    """
    return Path(str(resources.files("powerfx") / "_bundled")).resolve()
