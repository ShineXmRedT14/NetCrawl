import logging
import platform
import os
import time as tm

from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.rule import Rule

from netcrawl.util.utils import ferr

logo = """
███╗   ██╗███████╗████████╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     
████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██║    ██║██║     
██╔██╗ ██║█████╗     ██║   ██║     ██████╔╝███████║██║ █╗ ██║██║     
██║╚██╗██║██╔══╝     ██║   ██║     ██╔══██╗██╔══██║██║███╗██║██║     
██║ ╚████║███████╗   ██║   ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝
"""

def clear():
    try:
        if platform.system == "Linux":
            os.system('clear')
        else:os.system('cls')
    except Exception as e:logging.error(ferr(e), exc_info=True)

def renderlogo():
    try:
        clear()
        cnsl = Console()
        text = Text(logo)
        text.stylize("bold bright_red")
        text1 = Text(" N e t   C r a w l e r   -   T o o l   F o r   I n f o")
        text1.stylize("bold red")
        cnsl.print(Align.center(text))
        cnsl.print(Align.center(text1))
        cnsl.print(Rule(style="bright_red", characters="______"))
        tm.sleep(1)
        text2 = Text.from_markup("[bold red]NetCrawl -> [/][bold yellow]Start -> [/][bold green]In 4 Seconds[/]")
        text3 = Text.from_markup("[bold yellow]In the end, All found data will be in [/][bold red]->[/] [bold bright_green]/netcrawl/info/*[/]")
        cnsl.print(Align.center(text3))
        cnsl.print(Align.center(text2))
        tm.sleep(4)
    except Exception as e:logging.error(ferr(e), exc_info=True)