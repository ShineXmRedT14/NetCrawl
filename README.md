# NetCrawl
Async Python web crawler with DNS/SSL/headers recon and playwright for javascript render pages.

> ⚠️ Authorized use only. This tool is intended for security research and penetration testing against targets you own or have explicit written permission to test. Scanning third-party sites without authorization may be illegal in your jurisdiction.

## Features

- Async crawling — concurrent requests via aiohttp + asyncio, configurable concurrency limits
- JS/anti-bot fallback — detects bot-challenge pages and re-renders them with a headless Playwright browser
- Recon data per page — DNS records (A/AAAA), SSL certificate info, HTTP headers, page metadata, forms, scripts, stylesheets
- Link extraction — full list of links found on each page, plus a separate list of newly discovered links added to the crawl queue

## Installation

git clone https://github.com/ShineXmRedT14/NetCrawl
cd src/netcrawl
python run.py
`run.py installs dependencies (including Playwright browser binaries) and the package itself.

### Dependencies

aiohttp, bs4, dnspython, playwright, rich, colorama, aiofiles, lxml

## Usage

``bash
netcrawl -u <url> [options]

### Options

| Flag | Long form | Description |
|---|---|---|
| `-h` | `--help` | Show help |
| `-u` | `--url` | URL to start crawling from |
| `-d` | `--deep` | Crawl depth (number of link-following passes) |
| `-http` | `--http` | Concurrency limit for static (aiohttp) requests |
| `-js` | `--js` | Concurrency limit for Playwright-rendered requests |
| `-AL` | `--low` | Low aggressiveness (longer delay between requests) |
| `-AM` | `--mid` | Medium aggressiveness |
| `-AH` | `--high` | High aggressiveness (shorter delay) |
| `-cd` | `--custom` | Custom Delay |

### Defaults

deep = 8
http = 8
js   = 3
delay = 0.3s

### Example

bash
netcrawl -u https://example.com -d 5 -http 8 -AL

## Output

Each crawled URL is saved as a JSON file (e.g. `hostname-com-path1-path2.json`, `hostname-org-path0-path1-path3.json`, ...) In the /netcrawl/info/* path

## Uninstall

bash
python clear.py
`

Removes dependencies, Playwright browser binaries, and the package.

## License

(MIT) LICENSE
