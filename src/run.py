import subprocess
import platform

from pathlib import Path
from netcrawl.util.utils import pather

def install():
    try:
        from netcrawl.util.install import rdep

        rdep()

        paths = pather(str(Path.cwd()))

        if platform.system == "Linux":
            subprocess.run(["pip", "install", paths, "--user", "--break-system-packages"])
        else: subprocess.run(["pip", "install", paths])
    except subprocess.CalledProcessError as e:print(e, flush=True)
    except Exception as e:print(e, flush=True)

if __name__ == "__main__":
    install()
