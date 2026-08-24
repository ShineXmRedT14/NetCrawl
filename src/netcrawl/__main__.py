import argparse
import logging
import sys
import asyncio

from netcrawl.util.utils import ferr, pather
from pathlib import Path

logging.basicConfig(
    filename=f"{pather(str(Path.cwd()))}/netcrawl/logs/err.log",
    level=logging.ERROR
)

def setcrawl():
    try:
        from colorama import Fore
        from netcrawl.config.cnf import version, epitext, lflag, bflag, hflag, typeindex, actionindex

        parser = argparse.ArgumentParser(add_help=False, description=f"{Fore.LIGHTCYAN_EX}Netcrawl tool, {Fore.LIGHTRED_EX}Version - {Fore.LIGHTYELLOW_EX}{version}", epilog=epitext)

        for index in range(len(lflag)):
            if index in typeindex:
                parser.add_argument(lflag[index], bflag[index], help=hflag[index], type=int)
            elif index in actionindex:
                parser.add_argument(lflag[index], bflag[index], help=hflag[index], action="store_true")
            else: parser.add_argument(lflag[index], bflag[index], help=hflag[index])

        args = parser.parse_args()

        from netcrawl.core.core import asynl
        from netcrawl.core.params import NetCrawlParams

        context = NetCrawlParams()

        if args.low:context.time = 0.2
        elif args.mid:context.time = 0.05
        elif args.high:context.time = 0.02
        elif args.custom:
            if int(args.custom) != 0:
                context.time = round(int(args.custom)/1000)
        if args.deep:context.deep = int(args.deep)
        if args.http:context.http = int(args.http)
        if args.js:context.js = int(args.js)
        if args.help:
            print(epitext, flush=True)
            sys.exit(0)
        if args.url:
            asyncio.run(asynl(args.url, context))
            sys.exit(0)
        else:
            print(f"{Fore.LIGHTRED_EX}Invalid Arguments\n -> -u <url> and -d int:<deep>, -http int:<http>, -js int:<js>, -AL, -AM, -AH, -cd int:<delay> if need\n -> For help -h or --help{Fore.LIGHTWHITE_EX}", flush=True)
            sys.exit(0)
    except Exception as e:logging.error(ferr(e), exc_info=True)
