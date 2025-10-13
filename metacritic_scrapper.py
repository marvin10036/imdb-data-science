# pip install playwright
# playwright install

import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://www.metacritic.com/movie/roofman/critic-reviews/"
CARD_SELECTOR = ".c-siteReviewHeader_reviewScore"  # cards dos reviews
SPAN_PATH = ":scope a div div span, :scope div a div div span"  # caminho pedido (com fallback)
MAX_STEPS = 400            # limite de rolagens para evitar loop infinito
PAUSE_MS = 350             # pausa entre rolagens (ms)

def try_accept_cookies(page):
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

def extract_target_count(page) -> int:
    """
    Procura por um texto tipo 'Showing 44 Critic Reviews' e devolve o 44.
    """
    # Tenta esperar explicitamente por um match com regex no texto
    try:
        page.locator(r'text=/Showing\s+\d+\s+Critic Reviews/').first.wait_for(timeout=8000)
    except PlaywrightTimeoutError:
        pass

    # Coleta todo innerText da página e usa regex
    body_text = page.evaluate("() => document.body.innerText")
    m = re.search(r"Showing\s+(\d+)\s+Critic Reviews", body_text, flags=re.I)
    if not m:
        raise RuntimeError("Não encontrei o texto 'Showing N Critic Reviews' na página.")
    return int(m.group(1))

def collect_new_scores(page, current_list, target_count):
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
        current_list.append(txt)
        added += 1

    return added

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        locale="pt-BR",
        extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"},
    )
    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    try_accept_cookies(page)

    # 1) Descobrir N pela string "Showing N Critic Reviews"
    target = extract_target_count(page)
    print("Alvo (N de cards):", target)

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

    print(f"Coletados: {len(scores)} valores (esperado {target})")
    # Lista final com os valores dos spans (na ordem dos cards)
    print(scores)
