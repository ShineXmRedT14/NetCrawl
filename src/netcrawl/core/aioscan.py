import aiohttp
import warnings
import logging
import asyncio
import dns.asyncresolver as aiodns
import json
import ssl
import aiofiles
import socket as sc
import tree_sitter_javascript as tsjs

from tree_sitter import Language, Parser, Query, QueryCursor
from aiohttp import ClientError, ClientConnectionError
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from netcrawl.config.cnf import dnsr, cnfdeep, cnfhttp, cnfjs, cnftime, cform, qtreesit
from netcrawl.util.utils import ferr, NetCrawlAgent, pather
from netcrawl.core.render import render
from netcrawl.core.params import NetCrawlParams
from playwright.async_api import async_playwright, Browser
from pathlib import Path

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

def jstry(html: str, resp: aiohttp.ClientResponse) -> bool:
    try:
        import re

        bans = [
            403,
            429,
            503
        ]

        soup = BeautifulSoup(html, 'lxml')
        body = soup.find('body')
        text = body.get_text(strip=True)

        ps = body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'section'])
        imn = body.find_all('div', id=re.compile(r'(root|app|__next|nuxt|script|node|__next__)', re.IGNORECASE))
        jss = body.find_all('script')

        if len(jss) >= 1 and (len(text) <= 150 or len(ps) <= 5 or len(imn) >= 1):
            return True
        
        if resp.status in bans:
            return True
        
        serv = resp.headers.get("Server", "").lower()

        if "cloudflare" in serv:
            return True

        return False
    except Exception as e:
        logging.error(ferr(e), exc_info=True)
        return True

class aiohtml:
    def __init__(self, url: str, params: NetCrawlParams):
        if not url.endswith('/'):
            url = f"{url}/"
        self.url = [url]
        self.curl = []
        self.params = params
        self.netparam = {
            'deep': 1,
            'time': 1.0,
            'http': 1,
            'js': 1
        }

        if self.params.deep is not None: self.netparam['deep'] = self.params.deep
        else: self.netparam['deep'] = cnfdeep

        if self.params.time is not None: self.netparam['time'] = self.params.time
        else: self.netparam['time'] = cnftime

        if self.params.http is not None: self.netparam['http'] = self.params.http
        else: self.netparam['http'] = cnfhttp

        if self.params.js is not None: self.netparam['js'] = self.params.js
        else: self.netparam['js'] = cnfjs

        self.urls = {}
        self.netloc = urlparse(url).netloc
        self.lock = asyncio.Lock()
        self.httpsem = asyncio.Semaphore(self.netparam['http'])
        self.jssem = asyncio.Semaphore(self.netparam['js'])
    async def aiostart(self) -> None:
        try:
            agent = NetCrawlAgent()
            
            async with aiohttp.ClientSession() as session:
                async with async_playwright() as pwr:
                    browser = await pwr.chromium.launch(headless=True, timeout=40000, handle_sighup=True, handle_sigint=True, handle_sigterm=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--blink-settings=imagesEnabled=false'])
                    await self.aiomain(session, pwr, agent, browser)
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aiomain(self, session, pwr, agent: NetCrawlAgent, browser: Browser) -> None:
        try:
            self.urls.setdefault(self.url[0], {})
            await asyncio.gather(
                self.aiodns(self.url[0]),
                asyncio.to_thread(self.aiossl, self.url[0]),
                self.aiorules(self.url[0], session, agent)
            )

            for _ in range(self.netparam['deep']):
                if self.url:tasks = [self.aioreq(session, pwr, task, agent, browser) for task in self.url]
                else:break

                for turl in self.url:
                    self.urls.setdefault(turl, {})
                    self.urls[turl]['url'] = turl

                await asyncio.gather(*tasks)

                backlist = []
                for nurl in self.curl:
                    if nurl not in self.urls:
                        if not nurl.lower().endswith(cform) and self.netloc in urlparse(nurl).netloc:backlist.append(nurl)

                self.url.clear()
                self.url.extend(backlist)
                self.curl.clear()
                backlist.clear()

            await browser.close()
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aioreq(self, session, pwr, nurl: str, agent: NetCrawlAgent, browser: Browser) -> None:
        try:
            async with self.httpsem:
                try:
                    async with session.get(url=nurl, timeout=10, headers=agent.all) as rs:
                        try:
                            async with asyncio.timeout(5):
                                html = await rs.text()
                        except TimeoutError as e:logging.warning(ferr(e))

                        if html:
                            resp = await asyncio.to_thread(jstry, html, rs)

                            if not resp:
                                await self.aioparse(html, nurl, rs.status, session, agent)
                            else:
                                nresp = await render(nurl, pwr, self.jssem, agent, browser)
                                if nresp:
                                    chtml = nresp.get('html')
                                    cstat = nresp.get('status')
                                    if chtml and cstat and (chtml != "??? / Maybe Banned" or cstat != "??? / Maybe Banned"):await self.aioparse(chtml, nurl, cstat, session, agent)
                except (TimeoutError, ClientError, ClientConnectionError, asyncio.TimeoutError) as e:logging.warning(ferr(e), exc_info=True)
            await self.aiojson(nurl)
            await asyncio.sleep(self.netparam['time'])
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aioparse(self, html: str, url: str, status: int, session, agent: NetCrawlAgent) -> None:
        try:
            soup = BeautifulSoup(html, 'lxml')

            links = soup.find_all(['link', 'a'])
            lang = soup.find('html')
            hs = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            title = soup.find('title')
            text = soup.get_text(separator=" ", strip=True)
            forms = soup.find_all('form')
            js = soup.find_all('script')
            metas = soup.find_all('meta')
            styles = soup.find_all('link', rel="stylesheet")
            dstyles = soup.find_all('style')
            imgs = soup.find_all('img')
            videos = soup.find_all('video')

            shtml = html.split('\n')
            self.urls[url]['status'] = str(status)

            if shtml:
                self.urls[url].setdefault('html', [])
                for hhtml in shtml:
                    self.urls[url]['html'].append(hhtml.replace('\t', '.'))
            else:self.urls[url]['html'] = html

            if links:
                self.urls[url].setdefault('links', {})
                self.urls[url]['links'].setdefault('url', [])
                self.urls[url]['links'].setdefault('new', [])
                for link in links:
                    href = link.get('href')
                    if href:self.urls[url]['links']['url'].append(href)
                    parse = urlparse(href)

                    if href and ('#' not in href and 'tel:' not in href and 'mailto:' not in href and 'javascript:' not in href):
                        if not parse.scheme:
                            href = urljoin(url, href)
                        
                        if href not in self.urls and href not in self.curl:
                            self.curl.append(href)

                            if href not in self.urls:self.urls[url]['links']['new'].append(href)
            if lang:
                nlan = lang.get('lang')
                if nlan:self.urls[url]['lang'] = nlan

            if hs:
                self.urls[url].setdefault('hs', [])
                for h in hs:self.urls[url]['hs'].append(str(h))

            if title:self.urls[url]['title'] = title.text

            if text:
                stext = text.splitlines()

                if stext:
                    self.urls[url].setdefault('raw', [])
                    for htext in stext:
                        self.urls[url]['raw'].append(htext)
                else:self.urls[url]['raw'] = text

            if forms:
                self.urls[url].setdefault('forms', {})
                self.urls[url]['forms'].setdefault('raw', [])
                self.urls[url]['forms'].setdefault('input', [])
                self.urls[url]['forms'].setdefault('textarea', [])
                for frm in forms:
                    self.urls[url]['forms']['raw'].append(str(frm))
                    inputs = frm.find_all('input')
                    areas = frm.find_all('textarea')

                    if inputs:
                        for inp in inputs:self.urls[url]['forms']['input'].append(str(inp))
                    
                    if areas:
                        for area in areas:self.urls[url]['forms']['textarea'].append(str(area))

            if js:
                self.urls[url].setdefault('script', {})
                self.urls[url]['script'].setdefault('in-html', {})
                self.urls[url]['script'].setdefault('src', {})
                self.urls[url]['script']['in-html'].setdefault('parsed', [])
                self.urls[url]['script']['in-html'].setdefault('code', [])
                self.urls[url]['script']['src'].setdefault('links', [])
                self.urls[url]['script']['src'].setdefault('parsed', [])
                self.urls[url]['script']['src'].setdefault('code', [])

                for njs in js:
                    src = njs.get('src')

                    if src:
                        self.urls[url]['script']['src']['links'].append(src)
                        parse = urlparse(src)

                        if not parse.scheme:
                            purl = urljoin(url, src)
                        else:purl = src

                        await self.aioscript(purl, session, agent, self.urls[url]['script']['src'])
                    else:
                        snjs = njs.text.split('\n')

                        if snjs:
                            for gnjs in snjs:
                                self.urls[url]['script']['in-html']['code'].append(gnjs)
                        else:
                            self.urls[url]['script']['in-html']['code'].append(njs.text)
                            
                        await asyncio.to_thread(self.aiojsparse, self.urls[url]['script']['in-html'], njs.text, url)
                
            if styles or dstyles:
                self.urls[url].setdefault('style', {})
                self.urls[url]['style'].setdefault('links', [])
                self.urls[url]['style'].setdefault('code', [])

                if styles:
                    for lstyle in styles:
                        css = lstyle.get('href')
                        if css:self.urls[url]['style']['links'].append(css)

                if dstyles:
                    for dstyle in dstyles:
                        try:
                            greps = dstyle.text.split('\n')

                            if greps:
                                for ngrep in greps:
                                    self.urls[url]['style']['code'].append(ngrep)
                        except:pass

            if metas:
                self.urls[url].setdefault('meta', {})
                self.urls[url]['meta'].setdefault('raw', [])
                self.urls[url]['meta'].setdefault('name', [])
                self.urls[url]['meta'].setdefault('content', [])
                self.urls[url]['meta'].setdefault('property', [])
                self.urls[url]['meta'].setdefault('charset', [])
                self.urls[url]['meta'].setdefault('http-equiv', [])

                for meta in metas:
                    self.urls[url]['meta']['raw'].append(str(meta))
                    name = meta.get('name')
                    content = meta.get('content')
                    prop = meta.get('property')
                    charset = meta.get('charset')
                    equ = meta.get('http-equiv')

                    if name:self.urls[url]['meta']['name'].append(name)
                    if content:self.urls[url]['meta']['content'].append(content)
                    if prop:self.urls[url]['meta']['property'].append(prop)
                    if charset:self.urls[url]['meta']['charset'].append(charset)
                    if equ:self.urls[url]['meta']['http-equiv'].append(equ)

            if imgs:
                self.urls[url].setdefault('img', {})
                self.urls[url]['img'].setdefault('raw', [])
                self.urls[url]['img'].setdefault('links', [])

                for img in imgs:
                    self.urls[url]['img']['raw'].append(str(img))

                    imgsrc = img.get('src')
                    if imgsrc:self.urls[url]['img']['links'].append(imgsrc)

            if videos:
                self.urls[url].setdefault('video', {})
                self.urls[url]['video'].setdefault('raw', [])
                self.urls[url]['video'].setdefault('source', {})
                self.urls[url]['video']['source'].setdefault('raw', [])
                self.urls[url]['video']['source'].setdefault('links', [])

                for vid in videos:
                    self.urls[url]['video']['raw'].append(str(vid))

                    vidsrc = vid.find_all('source')

                    if vidsrc:
                        for vds in vidsrc:
                            self.urls[url]['video']['source']['raw'].append(str(vds))

                            vdssrc = vds.get('src')
                            if vdssrc:self.urls[url]['video']['source']['links'].append(vdssrc)

        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aiorules(self, curl: str, session, agent: NetCrawlAgent) -> None:
        try:
            robots = urljoin(curl, "/robots.txt")
            sitemap = urljoin(curl, "/sitemap.xml")

            self.urls[curl].setdefault('rules', {})

            async with session.get(url=robots, timeout=10, headers=agent.all) as rs:
                self.urls[curl]['rules'].setdefault('robots', {})
                self.urls[curl]['rules']['robots']['status'] = rs.status
                try:
                    async with asyncio.timeout(5):
                        html = await rs.text()
                except (asyncio.TimeoutError, TimeoutError) as e:logging.warning(ferr(e))

                if html:
                    shtml = html.split('\n')

                    if shtml:
                        self.urls[curl]['rules']['robots'].setdefault('html', [])
                            
                        for dhtml in shtml:
                            self.urls[curl]['rules']['robots']['html'].append(dhtml.replace('\t', '.'))
                    else:self.urls[curl]['rules']['robots']['html'] = str(html)

                    soup = BeautifulSoup(html, 'lxml')
                    body = soup.find('body')

                    rawtext = body.get_text(separator=" ", strip=True)
                    stext = rawtext.splitlines()

                    if stext:
                        self.urls[curl]['rules']['robots'].setdefault('text', [])
                            
                        for htext in stext:
                            self.urls[curl]['rules']['robots']['text'].append(htext)
                    else:self.urls[curl]['rules']['robots']['text'] = rawtext

            async with session.get(url=sitemap, timeout=10, headers=agent.all) as rs:
                self.urls[curl]['rules'].setdefault('sitemap', {})
                self.urls[curl]['rules']['sitemap']['status'] = rs.status
                try:
                    async with asyncio.timeout(5):
                        xml = await rs.text()
                except (asyncio.TimeoutError, TimeoutError) as e:logging.warning(ferr(e))

                if xml:
                    sxml = xml.split('\n')

                    if sxml:
                        self.urls[curl]['rules']['sitemap'].setdefault('xml', [])
                            
                        for dxml in sxml:
                            self.urls[curl]['rules']['sitemap']['xml'].append(dxml.replace('\t', '.'))
                    else:self.urls[curl]['rules']['sitemap']['xml'] = str(xml)

                    soup = BeautifulSoup(xml, 'lxml-xml')
                    urls = soup.find_all('url')

                    if urls:
                        self.urls[curl]['rules']['sitemap'].setdefault('url', [])

                        for url in urls:
                            locatt = url.find('loc')

                            if locatt:self.urls[curl]['rules']['sitemap']['url'].append(locatt.text)

        except Exception as e:logging.error(ferr(e))
    async def aiodns(self, url: str) -> None:
        try:
            resolv = aiodns.Resolver()
            parse = urlparse(url)

            for rd in dnsr:
                try:
                    record = await resolv.resolve(parse.netloc, rd)

                    if record:
                        self.urls[url].setdefault('dns', [])
                    
                        for r in record:
                            self.urls[url]['dns'].append(f"{rd}: {r.to_text()}")
                except (NoAnswer, NoNameservers, NXDOMAIN):pass
        except Exception as e:logging.error(ferr(e), exc_info=True)
    def aiossl(self, url: str) -> None:
        try:
            parse = urlparse(url)

            if parse.scheme == 'https':
                ctx = ssl.create_default_context()

                with sc.create_connection((parse.hostname, 443)) as scs:
                    with ctx.wrap_socket(scs, server_hostname=parse.hostname) as ns:
                        self.urls[url].setdefault('ssl', {})
                        resp = ns.getpeercert(binary_form=False)
                        shr = ns.cipher()
                        shs = ns.server_hostname

                        if resp:self.urls[url]['ssl']['cert'] = resp
                        if shr:self.urls[url]['ssl']['parameter'] = shr
                        if shs:self.urls[url]['ssl']['hostname'] = shs
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aioscript(self, url: str, session, agent: NetCrawlAgent, dsrc: dict) -> None:
        try:
            async with session.get(url=url, timeout=5, headers=agent.all) as rs:
                dsrc['status'] = rs.status

                try:
                    async with asyncio.timeout(5):
                        script = await rs.text()
                except (asyncio.TimeoutError, TimeoutError) as e:logging.warning(ferr(e))

                if script:
                    sjs = script.split('\n')

                    if sjs:
                        for sjsline in sjs:
                            dsrc['code'].append(sjsline.replace('\t', '.'))
                    else:dsrc['code'] = script

                    await asyncio.to_thread(self.aiojsparse, dsrc, script, url)
        except Exception as e:logging.error(ferr(e), exc_info=True)
    def aiojsparse(self, dsrc: dict, script: str, src: str) -> None:
        try:
            jen = script.encode("utf-8")
            jsl = Language(tsjs.language())
            parser = Parser(jsl)
            tree = parser.parse(jen)

            qercap = Query(jsl, qtreesit)
            cursor = QueryCursor(qercap)
            qcap = cursor.captures(tree.root_node)
            cap = {
                'src': src,
                'info': []
            }
            ccap = {}

            for node, tag in qcap:
                ntext = jen[node.start_byte:node.end_byte].decode("utf-8")

                if tag == "func.name":
                    ccap['func'] = ntext

                elif tag == "func.args":
                    ccap['args'] = ntext

                    if ccap:
                        cap['info'].append(ccap.copy())
                    ccap.clear()

            dsrc['parsed'].append(cap)
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def aiojson(self, url: str) -> None:
        try:
            parse = urlparse(url)
            hostn = parse.hostname
            paths = parse.path.strip('/')

            varurl = f"{hostn.replace('.', '-')}-{paths.replace('/', '-')}"
            name = self.urls.get(url)
            if name:
                jsn = json.dumps(name, indent=4, ensure_ascii=False)
                async with self.lock:
                    async with aiofiles.open(f"{pather(str(Path.cwd()))}/netcrawl/info/{varurl}.json", "w", encoding="utf-8") as jf:
                        await jf.write(jsn)
                    self.urls[url] = {}
        except Exception as e:logging.error(ferr(e), exc_info=True)
