from __future__ import annotations
from typing import Dict, Sequence, List, Tuple
import math
import numpy as np
import pandas as pd
from src.scrapers.metacritic_scraper import get_metacritic_critic_scores_from_id

# ---------- utilidades robustas ----------

def _clean_scores(scores: Sequence[float]) -> np.ndarray:
    """Filtra None/NaN, garante float e recorta para [0, 100]."""
    arr = np.asarray([s for s in scores if s is not None and not (isinstance(s, float) and math.isnan(s))], dtype=float)
    if arr.size == 0:
        return arr
    # (opcional) limitar a faixa válida caso o scraping traga outliers malformados
    arr = np.clip(arr, 0.0, 100.0)
    return arr

def trimmed_mean(arr: np.ndarray, proportion_to_cut: float = 0.10) -> float:
    """Média aparada bilateral. proportion_to_cut em [0, 0.5)."""
    n = arr.size
    if n == 0:
        return float("nan")
    if not (0.0 <= proportion_to_cut < 0.5):
        raise ValueError("proportion_to_cut deve estar em [0, 0.5).")
    k = int(math.floor(n * proportion_to_cut))
    if k == 0:
        return float(arr.mean())
    arr_sorted = np.sort(arr)
    return float(arr_sorted[k:n - k].mean()) if (n - 2 * k) > 0 else float("nan")

def iqr(arr: np.ndarray) -> float:
    """Intervalo interquartil (Q3 - Q1)."""
    if arr.size == 0:
        return float("nan")
    q75, q25 = np.percentile(arr, [75, 25], method="linear")
    return float(q75 - q25)

def mad(arr: np.ndarray, scale: bool = True) -> float:
    """Median Absolute Deviation. Se scale=True, multiplica por 1.4826 (estima σ normal)."""
    if arr.size == 0:
        return float("nan")
    med = float(np.median(arr))
    mads = np.abs(arr - med)
    mad_val = float(np.median(mads))
    return float(1.4826 * mad_val) if scale else mad_val

def skewness(arr: np.ndarray) -> float:
    """Assimetria (Fisher-Pearson, com correção de viés)."""
    n = arr.size
    if n < 3:
        return float("nan")
    x = arr.astype(float)
    mu = float(x.mean())
    m2 = float(np.mean((x - mu) ** 2))
    if m2 == 0.0:
        return 0.0
    m3 = float(np.mean((x - mu) ** 3))
    g1 = m3 / (m2 ** 1.5)
    # correção de viés amostral
    G1 = math.sqrt(n * (n - 1)) / (n - 2) * g1
    return float(G1)

def excess_kurtosis(arr: np.ndarray) -> float:
    """Excesso de curtose (Fisher). Sem correção de viés (suficiente na prática)."""
    n = arr.size
    if n < 4:
        return float("nan")
    x = arr.astype(float)
    mu = float(x.mean())
    m2 = float(np.mean((x - mu) ** 2))
    if m2 == 0.0:
        return 0.0
    m4 = float(np.mean((x - mu) ** 4))
    g2 = m4 / (m2 ** 2) - 3.0
    return float(g2)

def proportions_above(arr: np.ndarray, thresholds: Sequence[float]) -> Dict[str, float]:
    """Proporção de notas >= cada limiar informado."""
    n = arr.size
    if n == 0:
        return {f"p_ge_{int(t)}": float("nan") for t in thresholds}
    return {f"p_ge_{int(t)}": float((arr >= t).mean()) for t in thresholds}

def metacritic_buckets(arr: np.ndarray) -> Tuple[float, float, float]:
    """
    Proporções Metacritic por cor (aprox.):
    - verde: 61–100
    - amarelo: 40–60
    - vermelho: 0–39
    """
    n = arr.size
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p_green = float(((arr >= 61) & (arr <= 100)).mean())
    p_yellow = float(((arr >= 40) & (arr <= 60)).mean())
    p_red = float(((arr >= 0) & (arr <= 39)).mean())
    return (p_green, p_yellow, p_red)

def shannon_entropy(proportions: Sequence[float], base: float = 2.0) -> float:
    """Entropia de Shannon das proporções (ignora p=0)."""
    ps = [p for p in proportions if p and not math.isnan(p)]
    if not ps:
        return float("nan")
    return float(-sum(p * (math.log(p) / math.log(base)) for p in ps))

# ---------- geração de features por filme ----------

def features_from_scores_map(scores_by_film: Dict[str, Sequence[float]]) -> pd.DataFrame:
    """
    Constrói um DataFrame com features estatísticas por filme.
    Entrada: { 'Filme A': [95, 88, ...], 'Filme B': [72, ...], ... }
    """
    rows: List[Dict[str, float]] = []

    for film, scores in scores_by_film.items():
        arr = _clean_scores(scores)

        n = int(arr.size)
        mean = float(arr.mean()) if n else float("nan")
        median = float(np.median(arr)) if n else float("nan")
        tmean10 = trimmed_mean(arr, 0.10) if n else float("nan")
        tmean20 = trimmed_mean(arr, 0.20) if n else float("nan")
        std = float(arr.std(ddof=1)) if n > 1 else 0.0 if n == 1 else float("nan")
        _iqr = iqr(arr)
        _mad = mad(arr, scale=True)
        _skew = skewness(arr)
        _kurt = excess_kurtosis(arr)

        props = proportions_above(arr, thresholds=[90, 80])
        p_green, p_yellow, p_red = metacritic_buckets(arr)
        entropy_gyr = shannon_entropy([p_green, p_yellow, p_red], base=2.0)

        row = {
            "film": film,
            "n_reviews": n,
            "mean": mean,
            "median": median,
            "trimmed_mean_10": tmean10,
            "trimmed_mean_20": tmean20,
            "std": std,
            "iqr": _iqr,
            "mad": _mad,
            "skewness": _skew,
            "excess_kurtosis": _kurt,
            "p_ge_90": props["p_ge_90"],
            "p_ge_80": props["p_ge_80"],
            "p_green_61_100": p_green,
            "p_yellow_40_60": p_yellow,
            "p_red_0_39": p_red,
            "entropy_gyr_bits": entropy_gyr,
        }
        rows.append(row)

    df = pd.DataFrame(rows).set_index("film").sort_values(["p_ge_90", "median", "n_reviews"], ascending=[False, False, False])
    return df

# ---------- exemplo de uso ----------


