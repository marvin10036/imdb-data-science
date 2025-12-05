"""
Scraper de IMDb IDs a partir de uma página de resultados.

Procura todos os <a> com classe "ipc-title-link-wrapper" e extrai o href no formato:
    /title/tt1234567/?ref_=sr_t_50

O site carrega mais resultados ao clicar em "50 more" (classe "ipc-see-more__text").
Este script clica até o botão sumir e salva os IMDb IDs encontrados em um arquivo JSON.
"""

import json
import sys
from pathlib import Path
from typing import List, Set

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def extract_ids_from_page(page) -> Set[str]:
    ids: Set[str] = set()
    anchors = page.locator("a.ipc-title-link-wrapper")
    count = anchors.count()
    for i in range(count):
        href = anchors.nth(i).get_attribute("href") or ""
        # href esperado: /title/tt1234567/?ref_=...
        parts = href.split("/")
        if len(parts) >= 3 and parts[1] == "title":
            imdb_id = parts[2]
            if imdb_id.startswith("tt"):
                ids.add(imdb_id)
    return ids


def click_see_more_until_end(page, pause_ms: int = 1200):
    """
    Clica em "50 more" até o botão desaparecer. Ignora timeouts.
    """
    while True:
        btn = page.locator(".ipc-see-more__text")
        print("clicou")
        if not btn.count():
            break
        try:
            btn.first.click(timeout=2000)
            page.wait_for_timeout(pause_ms)
        except PlaywrightTimeoutError:
            break


def scrape_imdb_ids(url: str, headless: bool = True) -> List[str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        # rolar um pouco para garantir render
        page.wait_for_timeout(800)
        click_see_more_until_end(page)
        ids = extract_ids_from_page(page)
        browser.close()
        return sorted(ids)


def main():
    # if len(sys.argv) < 3:
    #     print("Uso: python scripts/get_2025_ttid.py <URL_IMDB> <OUTPUT_JSON_PATH>")
    #     sys.exit(1)

    url = "https://www.imdb.com/search/title/?title_type=feature&release_date=2025-01-01,2025-12-03&num_votes=10000,&sort=year,desc"
    output_path = "teste.json"

    ids = scrape_imdb_ids(url)
    print(f"Encontrados {len(ids)} IMDb IDs.")

    # output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

    print(f"IDs salvos em {output_path}")


if __name__ == "__main__":
    main()
