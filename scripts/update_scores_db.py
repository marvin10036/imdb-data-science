"""
Atualiza as tabelas de notas (rating_samples e rating_sample_features)
com base no JSON data/processed/movie_scores.json.

Útil após rodar o scraping dos IDs faltantes de ml_split_prediction_2025.
"""

import json
import math
import os
from typing import Iterable, List, Tuple

import pandas as pd
import psycopg2
from psycopg2 import extras


def _none_if_nan(value):
    return None if pd.isna(value) else float(value)


def compute_geometric_mean(values: List[int]) -> float | None:
    if not values:
        return None
    if any(v < 0 for v in values):
        return None
    if any(v == 0 for v in values):
        return 0.0
    log_sum = sum(math.log(v) for v in values)
    return math.exp(log_sum / len(values))


def compute_harmonic_mean(values: List[int]) -> float | None:
    if not values or any(v <= 0 for v in values):
        return None
    return len(values) / sum(1 / v for v in values)


def compute_rating_features(imdb_id: str, samples: List[int]) -> Tuple:
    if not samples:
        return (
            imdb_id,
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            0,
        )

    series = pd.Series(samples, dtype="float64")
    sample_count = int(series.size)
    mean_score = _none_if_nan(series.mean())
    median_score = _none_if_nan(series.median())

    mode_series = series.mode()
    mode_score = int(mode_series.iloc[0]) if not mode_series.empty else None
    mode_frequency = int((series == mode_score).sum()) if mode_score is not None else None

    variance_score = _none_if_nan(series.var(ddof=0))
    stddev_score = _none_if_nan(series.std(ddof=0))
    geometric_mean_score = compute_geometric_mean(samples)
    harmonic_mean_score = compute_harmonic_mean(samples)

    min_score = int(series.min())
    max_score = int(series.max())
    p10_score = _none_if_nan(series.quantile(0.10))
    p25_score = _none_if_nan(series.quantile(0.25))
    p75_score = _none_if_nan(series.quantile(0.75))
    p90_score = _none_if_nan(series.quantile(0.90))
    iqr_score = p75_score - p25_score if p75_score is not None and p25_score is not None else None
    range_score = max_score - min_score if min_score is not None and max_score is not None else None
    unique_scores = int(series.nunique())

    return (
        imdb_id,
        sample_count,
        mean_score,
        median_score,
        mode_score,
        mode_frequency,
        variance_score,
        stddev_score,
        geometric_mean_score,
        harmonic_mean_score,
        min_score,
        max_score,
        p10_score,
        p25_score,
        p75_score,
        p90_score,
        iqr_score,
        range_score,
        unique_scores,
    )


def main():
    # Config de conexão (usa env se existir)
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "moviesdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

    with open("data/processed/movie_scores.json", "r", encoding="utf-8") as f:
        rating_data = json.load(f)

    try:
        with open("data/errors/error_list_from_error_list.json", "r", encoding="utf-8") as f:
            error_list = json.load(f)
        error_ids = set(error_list.keys())
    except FileNotFoundError:
        error_ids = set()

    ids_to_process = [imdb_id for imdb_id in rating_data.keys() if imdb_id not in error_ids]

    if not ids_to_process:
        print("Nenhum ID para processar (arquivo de notas vazio ou apenas IDs com erro).")
        return

    rating_rows: List[Tuple] = []
    feature_rows: List[Tuple] = []

    for imdb_id in ids_to_process:
        samples = rating_data.get(imdb_id, [])
        for idx, score in enumerate(samples, start=1):
            rating_rows.append((imdb_id, int(score), idx))
        feature_rows.append(compute_rating_features(imdb_id, samples))

    cur = conn.cursor()

    # Limpa registros existentes dos IDs em questão para garantir sincronização
    cur.execute("DELETE FROM rating_samples WHERE movie_id = ANY(%s)", (ids_to_process,))
    cur.execute("DELETE FROM rating_sample_features WHERE movie_id = ANY(%s)", (ids_to_process,))

    # Inserir novas amostras
    extras.execute_values(
        cur,
        "INSERT INTO rating_samples (movie_id, score_value, sample_index) VALUES %s",
        rating_rows,
    )

    # Inserir/atualizar features agregadas
    extras.execute_values(
        cur,
        """
        INSERT INTO rating_sample_features (
            movie_id, sample_count, mean_score, median_score, mode_score, mode_frequency,
            variance_score, stddev_score, geometric_mean_score, harmonic_mean_score,
            min_score, max_score, p10_score, p25_score, p75_score, p90_score,
            iqr_score, range_score, unique_scores
        ) VALUES %s
        ON CONFLICT (movie_id) DO UPDATE SET
            sample_count = EXCLUDED.sample_count,
            mean_score = EXCLUDED.mean_score,
            median_score = EXCLUDED.median_score,
            mode_score = EXCLUDED.mode_score,
            mode_frequency = EXCLUDED.mode_frequency,
            variance_score = EXCLUDED.variance_score,
            stddev_score = EXCLUDED.stddev_score,
            geometric_mean_score = EXCLUDED.geometric_mean_score,
            harmonic_mean_score = EXCLUDED.harmonic_mean_score,
            min_score = EXCLUDED.min_score,
            max_score = EXCLUDED.max_score,
            p10_score = EXCLUDED.p10_score,
            p25_score = EXCLUDED.p25_score,
            p75_score = EXCLUDED.p75_score,
            p90_score = EXCLUDED.p90_score,
            iqr_score = EXCLUDED.iqr_score,
            range_score = EXCLUDED.range_score,
            unique_scores = EXCLUDED.unique_scores
        """,
        feature_rows,
    )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Atualizados {len(ids_to_process)} filmes em rating_samples e rating_sample_features.")


if __name__ == "__main__":
    main()
