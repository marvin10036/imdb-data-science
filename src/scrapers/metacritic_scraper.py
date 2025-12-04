import json
import re
from typing import Iterable, List, Set
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright, BrowserContext

CARD_SELECTOR = ".c-siteReviewHeader_reviewScore"  # cards dos reviews
SPAN_PATH = ":scope a div div span, :scope div a div div span"  # caminho pedido (com fallback)
MAX_STEPS = 400  # limite de rolagens para evitar loop infinito
PAUSE_MS = 350  # pausa entre rolagens (ms)


def try_accept_cookies(page: BrowserContext):
    for sel in [
        "#onetrust-accept-btn-handler",
        '[aria-label="Accept cookies"]',
        'button:has-text("Accept")',
        'button:has-text("I Agree")',
        'button:has-text("Aceitar")',
    ]:
        loc = page.locator(sel)
        if loc.count():
            try:
                loc.first.click(timeout=1500)
                break
            except Exception:
                pass


def extract_target_count(page: BrowserContext) -> int:
    """
    Procura por um texto tipo 'Showing 44 Critic Reviews' e devolve o 44.
    """
    # Tenta esperar explicitamente por um match com regex no texto
    try:
        page.locator(r"text=/Showing\s+\d+\s+Critic Reviews/").first.wait_for(timeout=8000)
    except PlaywrightTimeoutError:
        pass

    # Coleta todo innerText da página e usa regex
    body_text = page.evaluate("() => document.body.innerText")
    m = re.search(r"Showing\s+(\d+)\s+Critic Reviews", body_text, flags=re.I)
    if not m:
        raise RuntimeError("Não encontrei o texto 'Showing N Critic Reviews' na página.")
    return int(m.group(1))


def collect_new_scores(page: BrowserContext, current_list: list, target_count: int):
    """
    Lê os cards já presentes e, do índice len(current_list) até target_count-1,
    extrai o span 'div > a > div > div > span' relativo a cada card e acrescenta na lista.
    Retorna quantos foram adicionados nesta chamada.
    """
    cards = page.locator(CARD_SELECTOR)
    total_cards = min(cards.count(), target_count)
    added = 0

    for i in range(len(current_list), total_cards):
        card = cards.nth(i)
        span = card.locator(SPAN_PATH)
        if span.count():
            txt = span.first.inner_text().strip()
        else:
            # fallback leve: texto do próprio card, caso a estrutura varie
            txt = card.inner_text().strip()
        current_list.append(int(txt))
        added += 1

    return added


def get_metacritic_critic_scores(page_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
            extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"},
        )
        page = context.new_page()
        page.goto(page_url, wait_until="domcontentloaded")

        try_accept_cookies(page)

        # 1) Descobrir N pela string "Showing N Critic Reviews"
        target = extract_target_count(page)

        # 2) While loop: coletar até termos N valores
        scores = []
        steps_no_growth = 0

        step = 0
        while len(scores) < target and step < MAX_STEPS:
            step += 1

            # Coleta todos os cards visíveis e extrai os novos valores
            added_now = collect_new_scores(page, scores, target)

            if len(scores) >= target:
                break

            # Se não adicionou nada, tentamos rolar mais e ver se surgem novos cards
            if added_now == 0:
                steps_no_growth += 1
            else:
                steps_no_growth = 0

            # Scroll 1 viewport para disparar carregamento de mais reviews
            page.evaluate("window.scrollBy(0, document.documentElement.clientHeight)")
            page.wait_for_timeout(PAUSE_MS)

            # Se várias iterações sem crescer, tente estabilizar rede e continuar
            if steps_no_growth >= 3:
                try:
                    page.wait_for_load_state("networkidle", timeout=3000)
                except PlaywrightTimeoutError:
                    pass

        browser.close()

        return scores


def get_metacritic_page_from_imdb_db_id(db_id: str):

    imdb_page_url = f"https://www.imdb.com/title/{db_id}/criticreviews/"

    resp = requests.get(
        imdb_page_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/124.0.0.0 Safari/537.36"
            )
        },
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 1) Tentativa via seletor CSS (filhos diretos e 2º de cada nível):
    # div[data-testid="critic-reviews-title"] > div:nth-of-type(2) > div:nth-of-type(2) a[href]
    css = 'div[data-testid="critic-reviews-title"] > div:nth-of-type(2) > div:nth-of-type(2) a[href]'
    tag = soup.select_one(css)
    if not tag:
        raise ValueError(f"Link do Metacritic não encontrado na página do IMDb para {db_id}")

    metacritic_general_url = urljoin(imdb_page_url, tag["href"])

    metacritic_movie_name = metacritic_general_url.split("?")[0].split("https://www.metacritic.com/movie/")[1]

    return metacritic_movie_name, f"https://www.metacritic.com/movie/{metacritic_movie_name}/critic-reviews/"


def get_metacritic_critic_scores_from_id(imdb_id: str):
    metacritic_movie_name, metacritic_page_url = get_metacritic_page_from_imdb_db_id(imdb_id)

    return metacritic_movie_name, get_metacritic_critic_scores(metacritic_page_url)


def list_missing_scores_for_prediction(
    engine,
    scores_json_path: str = "data/processed/movie_scores.json",
    error_list_path: str = "data/errors/error_list_from_error_list.json",
) -> List[str]:
    """
    Retorna os IMDb IDs presentes em ml_split_prediction_2025 que ainda não estão no movie_scores.json.
    Ignora IDs listados no arquivo de erros para evitar reprocessar casos problemáticos.

    Args:
        engine: sqlalchemy engine já configurado.
        scores_json_path: caminho para o JSON de notas coletadas.
        error_list_path: caminho para o JSON de IDs com erro conhecidos.

    Returns:
        Lista de imdb_ids faltantes.
    """
    with open(scores_json_path, "r", encoding="utf-8") as f:
        scores_data = json.load(f)
    collected_ids: Set[str] = set(scores_data.keys())

    try:
        with open(error_list_path, "r", encoding="utf-8") as f:
            error_data = json.load(f)
        error_ids: Set[str] = set(error_data.keys())
    except FileNotFoundError:
        error_ids = set()

    df_pred = pd.read_sql("SELECT imdb_id FROM ml_split_prediction_2025", engine)
    prediction_ids: Iterable[str] = df_pred["imdb_id"].tolist()

    missing = [imdb_id for imdb_id in prediction_ids if imdb_id not in collected_ids and imdb_id not in error_ids]
    return missing


def scrape_missing_prediction_scores(
    engine,
    scores_json_path: str = "data/processed/movie_scores.json",
    error_list_path: str = "data/errors/error_list_from_error_list.json",
) -> List[str]:
    """
    Faz scraping de todos os IMDb IDs de ml_split_prediction_2025 que ainda não estão no movie_scores.json.
    IDs com erro conhecido (error_list_path) são ignorados para evitar retrabalho.
    Atualiza o JSON de scores e registra falhas no arquivo de erros.

    Args:
        engine: sqlalchemy engine já configurado.
        scores_json_path: caminho para o JSON de notas coletadas.
        error_list_path: caminho para o JSON de IDs com erro conhecidos.

    Returns:
        Lista de IMDb IDs que foram coletados com sucesso.
    """
    with open(scores_json_path, "r", encoding="utf-8") as f:
        scores_data = json.load(f)

    try:
        with open(error_list_path, "r", encoding="utf-8") as f:
            error_data = json.load(f)
    except FileNotFoundError:
        error_data = {}

    missing_ids = list_missing_scores_for_prediction(engine, scores_json_path, error_list_path)
    collected_now: List[str] = []

    for imdb_id in missing_ids:
        try:
            _, scores = get_metacritic_critic_scores_from_id(imdb_id)
            if not scores:
                raise ValueError("Scraping não retornou notas.")
            scores_data[imdb_id] = scores
            collected_now.append(imdb_id)
            print(f"✅ Coletado {imdb_id} ({len(scores)} reviews)")
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Falha ao coletar {imdb_id}: {exc}")
            error_data[imdb_id] = str(exc)

    # Persistir atualizações
    with open(scores_json_path, "w", encoding="utf-8") as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)

    with open(error_list_path, "w", encoding="utf-8") as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)

    return collected_now
