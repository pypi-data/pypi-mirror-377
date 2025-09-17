from ._version import __version__
from .algorithms import extract_scope_bdms, lfn2pfn_bdms

__all__ = [
    "__version__",
    "SUPPORTED_VERSION",
    "get_algorithms",
]

#: RUCIO versions supported by this package
SUPPORTED_VERSION = "~=38.0"


def get_algorithms():
    return {
        "lfn2pfn": {
            "ctao_bdms": lfn2pfn_bdms,
        },
        "scope": {
            "ctao_bdms": extract_scope_bdms,
        },
    }
