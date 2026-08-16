from colorama import Fore

dependencies = [
    "aiohttp",
    "bs4",
    "dnspython",
    "playwright",
    "rich",
    "colorama",
    "aiofiles",
    'lxml'
]

dnsr = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "TXT",
    "NS"
]

cform = (
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.css', '.js', '.json', '.xml', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar'
)

version = "1.0"
epitext = f"""
{Fore.LIGHTRED_EX}-h / {Fore.LIGHTYELLOW_EX}--help / {Fore.LIGHTGREEN_EX}Get commands/help
{Fore.LIGHTRED_EX}-u / {Fore.LIGHTYELLOW_EX}--url / {Fore.LIGHTGREEN_EX}URL from where crawler start
{Fore.LIGHTRED_EX}-d / {Fore.LIGHTYELLOW_EX}--deep / {Fore.LIGHTGREEN_EX}Scan deep
{Fore.LIGHTRED_EX}-http / {Fore.LIGHTYELLOW_EX}--http / {Fore.LIGHTGREEN_EX}Async I/O Limit for static requests
{Fore.LIGHTRED_EX}-js / {Fore.LIGHTYELLOW_EX}--js / {Fore.LIGHTGREEN_EX}Async I/O Limit for hard javascript render from playwright module
{Fore.LIGHTRED_EX}-AL / {Fore.LIGHTYELLOW_EX}--low / {Fore.LIGHTGREEN_EX}Crawler/agressive speed/Low
{Fore.LIGHTRED_EX}-AM / {Fore.LIGHTYELLOW_EX}--mid / {Fore.LIGHTGREEN_EX}Crawler/agressive speed/Mid
{Fore.LIGHTRED_EX}-AH / {Fore.LIGHTYELLOW_EX}--high / {Fore.LIGHTGREEN_EX}Crawler/agressive speed/High
{Fore.LIGHTWHITE_EX}
"""

lflag = ["-h", "-u", "-d", "-http", "-js", "-AL", "-AM", "-AH"]
bflag = ["--help", "--url", "--deep", "--http", "--js", "--low", "--mid", "--high"]
hflag = ["Get commands/help", "URL from where crawler start", "Scan deep", "Async I/O Limit for static requests", "Async I/O Limit for hard javascript render from playwright module", "URL (sites) Limit", "Crawler/agressive speed/Low", "Crawler/agressive speed/Mid", "Crawler/agressive speed/High"]

typeindex = [2, 3, 4]
actionindex = [0, 5, 6, 7]

cnfdeep = 8
cnftime = 0.1
cnfhttp = 5
cnfjs = 3