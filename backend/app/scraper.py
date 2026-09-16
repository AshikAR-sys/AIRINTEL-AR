import os, re
from datetime import datetime
from random import Random
from playwright.async_api import async_playwright

PRICE_RE = re.compile(r"(?:₹\s*|INR\s*)([0-9][0-9,]*(?:\.[0-9]+)?)")

async def scrape_configured_page():
    url=os.getenv("SCRAPER_TARGET_URL","").strip()
    if not url:
        rnd=Random()
        return [{
            "route":"MAA-DEL","origin":"MAA","destination":"DEL",
            "airline":"Demo Airline","flight_code":f"AI{rnd.randint(100,999)}",
            "price_inr":float(rnd.randint(4500,7200)),
            "source":"Playwright Demo Collector","observed_at":datetime.utcnow()
        }]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        page=await browser.new_page(user_agent="AirIntel-India-Research-Bot/1.0")
        await page.goto(url,wait_until="domcontentloaded",timeout=30000)
        await page.wait_for_timeout(5000)
        text=await page.locator("body").inner_text()
        print(text[:3000])
        await browser.close()
    values=[]
    for m in PRICE_RE.finditer(text):
        v=float(m.group(1).replace(",",""))
        if 500<=v<=200000: values.append(v)
    return [{
        "route":"MAA-DEL","origin":"MAA","destination":"DEL",
        "airline":"Configured Source","flight_code":"SCRAPE",
        "price_inr":v,"source":url,"observed_at":datetime.utcnow()
    } for v in values[:20]]
