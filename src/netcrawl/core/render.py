import asyncio
import logging

from netcrawl.util.utils import ferr, NetCrawlAgent
from playwright.async_api import Browser, Error as PlayError, TimeoutError as PlayTimeoutError

class renderjs:
    def __init__(self, pwr, url: str, agent: NetCrawlAgent, browser: Browser):
        self.pwr = pwr
        self.url = url
        self.agent = agent
        self.browser = browser
        self.max = 10
        self.min = 0
        self.returned = {}
    async def ajsmain(self) -> dict:
        try:
            context = await self.browser.new_context(viewport = self.agent.view, user_agent = self.agent.user, extra_http_headers = {'Accept': self.agent.accept, 'Accept-Language': self.agent.language}, java_script_enabled=True, ignore_https_errors=True, bypass_csp=True)
            page = await context.new_page()
            try:resp = await page.goto(url=self.url, timeout=30000, referer="https://google.com", wait_until="domcontentloaded")
            except (PlayError, PlayTimeoutError):pass

            if resp:self.returned['status'] = resp.status
            else:self.returned['status'] = "??? / Maybe banned"

            html = await self.ajshtml(page)
            self.returned['html'] = html

            await page.close()
            await context.close()

            return self.returned
        except Exception as e:logging.error(ferr(e), exc_info=True)
    async def ajshtml(self, page) -> str:
        try:
            static_height = await page.evaluate("document.body.scrollHeight")
            while self.min < self.max:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                try:await page.wait_for_load_state("networkidle", timeout=6000)
                except (PlayTimeoutError, PlayError):pass

                render_height = await page.evaluate("document.body.scrollHeight")

                if static_height == render_height:
                    break
                else:
                    static_height = render_height
                self.min += 1

            try:
                async with asyncio.timeout(10):
                    html = await page.content() 
            except (TimeoutError, PlayError, PlayTimeoutError):pass

            if not html: html = "??? / Maybe Banned"

            return str(html)
        except Exception as e:logging.error(ferr(e), exc_info=True)

async def render(url: str, pwr, jssem: asyncio.Semaphore, agent: NetCrawlAgent, browser: Browser) -> dict:
    try:
        rend = renderjs(pwr, url, agent, browser)
        async with jssem:
            datas = await rend.ajsmain()
        
        return datas
    except Exception as e:logging.error(ferr(e), exc_info=True)