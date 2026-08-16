import importlib.util as ifl
import subprocess
import logging
import sys

from netcrawl.config.cnf import dependencies
from netcrawl.util.utils import ferr

def idep(dp: str):
    try:
        subprocess.run(["pip", "install", dp], shell=True, timeout=60, check=True)
    except subprocess.CalledProcessError as e:logging.error(ferr(e), exc_info=True)
    except Exception as e:logging.error(ferr(e), exc_info=True)

def pdep(dp: str):
    try:
        if ifl.find_spec(dp) is None:
            subprocess.run(["pip", "install", dp], shell=True, timeout=60, check=True)
        subprocess.run(["playwright", "install"], shell=True, timeout=80, check=True)
    except subprocess.CalledProcessError as e:logging.error(ferr(e), exc_info=True)
    except Exception as e:logging.error(ferr(e), exc_info=True)

def rdep() -> bool:
    try:
        for dp in dependencies:
            if ifl.find_spec(dp) is not None and dp != "playwright":
                continue
            elif dp == "playwright":
                pdep(dp)
            else:idep(dp)
    except Exception as e:logging.error(ferr(e), exc_info=True)