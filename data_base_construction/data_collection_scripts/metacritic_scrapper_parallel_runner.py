from concurrent.futures import ThreadPoolExecutor, as_completed
from data_base_construction.data_collection_scripts.scores_processor import features_from_scores_map
from .metacritic_scraper import get_metacritic_critic_scores_from_id
import pandas as pd
from datetime import datetime


def fetch_one(imdb_id: str):
    print(f"Procurando {imdb_id}")
    name, scores = get_metacritic_critic_scores_from_id(imdb_id)
    return imdb_id, name, scores

if __name__ == "__main__":
    ids = ["tt7130300", "tt0111161", "tt0068646", "tt0468569", "tt0071562", "tt0050083", "tt0167260", "tt0108052", "tt0120737", "tt0110912", "tt0060196", "tt0109830", "tt0167261", "tt0137523", "tt1375666", "tt0080684"]

    scores_by_film = {}
    # Ajuste o max_workers se o site for sensível a carga; 4–8 costuma ser seguro para scraping
    max_workers = min(8, len(ids))
    now = datetime.now()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in ids}
        for future in as_completed(futures):
            imdb_id = futures[future]
            try:
                _, name, scores = future.result()
                print(f"{name}: {scores}")
                if name:
                    scores_by_film[name] = scores
            except Exception as e:
                print(f"Erro ao processar {imdb_id}: {e}")

    print(datetime.now()-now)
    df_features = features_from_scores_map(scores_by_film)
    pd.set_option("display.max_columns", None)
    print(df_features.round(3))
