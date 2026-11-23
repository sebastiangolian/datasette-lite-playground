"""End-to-end check of every scenario link on the playground landing page.

Opens the landing page, collects the links from each scenario card and loads
each one in a fresh headless Chrome context, waiting for text that proves
Datasette rendered the expected data inside its iframe.

Usage: python tests/check_scenarios.py <site-url> [--host all|lite|self]
Requires: pip install playwright, and Google Chrome installed (channel="chrome").
"""

import argparse
import asyncio
import sys

from playwright.async_api import async_playwright

# Per scenario title: texts that must appear in the Datasette iframe, plus an
# optional CSS selector that must exist there.
EXPECTATIONS = {
    "SQLite database + metadata + config": (["Population by voivodeship", "SQLite database built by"], None),
    "Canned query with a parameter": (["Cities above a population threshold", "Lublin"], None),
    "Facets and sorting via URL": (["Warszawa", "świętokrzyskie"], ".facet-info"),
    "Plain CSV import": (["cities", "23 rows"], None),
    "SQL schema, then CSV": (["cities", "23 rows"], None),
    "JSON import": (["voivodeships", "16 rows"], None),
    "Plugin: datasette-cluster-map": (["23 rows", "Warszawa"], ".leaflet-container"),
    "Pinned Datasette + SQLite version": (['"version": "3.54.1"'], None),
    "Writes as root: datasette-write": (["Write to poland with SQL"], None),
}
HOST_LABELS = {"lite": "lite.datasette.io", "self": "Self-hosted"}
TIMEOUT_MS = 240_000  # first Pyodide boot plus plugin install can be slow
CONCURRENCY = 4


async def check(browser, semaphore, title, host, url):
    texts, selector = EXPECTATIONS.get(title, ([], None))
    if not texts and not selector:
        return False, f"FAIL [{host:17}] {title}: no expectations defined"
    async with semaphore:
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url)
            frame = page.frame_locator("#datasette")
            for text in texts:
                await frame.get_by_text(text).first.wait_for(state="attached", timeout=TIMEOUT_MS)
            if selector:
                await frame.locator(selector).first.wait_for(state="attached", timeout=TIMEOUT_MS)
            return True, f"PASS [{host:17}] {title}"
        except Exception as error:
            shell = (await page.locator("body").inner_text())[:300].replace("\n", " | ")
            return False, f"FAIL [{host:17}] {title}: {str(error).splitlines()[0]} | shell: {shell}"
        finally:
            await context.close()


async def main(site, host_filter):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page()
        await page.goto(site)
        jobs = []
        for card in await page.locator("article.card").all():
            title = await card.locator("h2").inner_text()
            for link in await card.locator(".actions a").all():
                host = await link.inner_text()
                if host_filter == "all" or host == HOST_LABELS[host_filter]:
                    jobs.append((title, host, await link.get_attribute("href")))
        await page.close()
        print(f"Checking {len(jobs)} links from {site}", flush=True)

        semaphore = asyncio.Semaphore(CONCURRENCY)
        results = await asyncio.gather(*(check(browser, semaphore, *job) for job in jobs))
        await browser.close()

    for _, line in results:
        print(line)
    passed = sum(ok for ok, _ in results)
    print(f"{passed}/{len(results)} passed")
    return bool(results) and passed == len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", help="URL of the landing page")
    parser.add_argument("--host", choices=["all", "lite", "self"], default="all")
    args = parser.parse_args()
    sys.exit(0 if asyncio.run(main(args.site, args.host)) else 1)
