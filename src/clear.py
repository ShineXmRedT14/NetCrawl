import subprocess
import platform
import os
import shutil
import importlib.util as ifl

from netcrawl.util.utils import ferr
from netcrawl.config.cnf import dependencies

def uninstall() -> None:
    try:
        for dp in dependencies:
            if ifl.find_spec(dp) is not None and dp != "playwright":
                subprocess.run(["pip", "uninstall", dp], shell=True, timeout=60, check=True)
            elif dp == "playwright":
                if ifl.find_spec(dp) is not None:
                    subprocess.run(["pip", "uninstall", dp], shell=True, timeout=60, check=True)
                
                if platform.system == "Linux":
                    pwdir = os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright")
                elif platform.system == "Windows":
                    pwdir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")

                if os.path.exists(pwdir):
                    shutil.rmtree(pwdir)
        if ifl.find_spec("netcrawl") is not None:
            subprocess.run(["pip", "uninstall", "netcrawl"], shell=True, timeout=60, check=True)
    except subprocess.CalledProcessError as e:print(ferr(e), exc_info=True)
    except Exception as e:print(ferr(e), exc_info=True)

if __name__ == "__main__":
    uninstall()