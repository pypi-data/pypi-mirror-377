"""
OpenBio - A placeholder package reserving the name for future development.

This package is currently a placeholder to reserve the name "openbio" on PyPI.
OpenBio is being developed as an open-source bioinformatics library.
"""

__version__ = "0.1.0"
__author__ = "ravishar313"
__email__ = "ravishar313@gmail.com"

def main() -> None:
    """Main entry point for the openbio CLI."""
    print("🧬 OpenBio v{}".format(__version__))
    print("This is currently a placeholder package.")
    print("You can use OpenBio at https://openbio.tech")
    print("Stay tuned for updates!")
    
def get_version() -> str:
    """Return the current version of OpenBio."""
    return __version__
