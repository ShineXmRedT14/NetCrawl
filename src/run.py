import subprocess
import platform

from netcrawl.util.utils import ferr

def install():
    try:
        from netcrawl.util.install import rdep

        rdep()

        if platform.system == "Linux":
            subprocess.run(["pip", "install", ".", "--user", "--break-system-packages"])
        else: subprocess.run(["pip", "install", "."])
    except subprocess.CalledProcessError as e:print(ferr(e), flush=True)
    except Exception as e:print(ferr(e), flush=True)

if __name__ == "__main__":
    install()