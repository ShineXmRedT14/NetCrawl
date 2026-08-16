from dataclasses import dataclass

@dataclass
class NetCrawlParams:
    deep: int | None = None
    time: float | None = None
    http: int | None = None
    js: int | None = None