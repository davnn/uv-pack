import json
import platform
import sys

import uv_pack


def get_system_info():
    return {
        "library": uv_pack.get_version(),
        "python": sys.version,
        "platform": platform.platform(),
        "architecture": platform.machine(),
    }


if __name__ == "__main__":
    print(json.dumps(get_system_info(), indent=4))
